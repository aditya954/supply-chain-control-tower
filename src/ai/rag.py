"""RAG pipeline: retrieval → context → LLM → structured answer."""

from __future__ import annotations

import json
import logging
import re
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from src.ai.prompts import SYSTEM_PROMPT, build_context_block, build_user_prompt
from src.ai.retriever import RetrievedDocument, RetrievalFilters, SupplyChainRetriever
from src.config import AppConfig, LLMConfig, load_config
from src.snowflake_client import get_connection

logger = logging.getLogger(__name__)

INSUFFICIENT_DATA = "Insufficient data."


@dataclass
class RAGAnswer:
    question: str
    risk: str
    reasons: list[str]
    business_impact: str
    recommended_action: str
    sources: list[str]
    confidence: str
    raw_response: str
    retrieval_count: int
    retrieval_latency_ms: float
    llm_latency_ms: float
    model: str
    status: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def format(self) -> str:
        if self.status == "insufficient_data":
            return INSUFFICIENT_DATA

        reasons_text = "\n".join(f"- {r}" for r in self.reasons) if self.reasons else "-"
        sources_text = ", ".join(self.sources) if self.sources else "-"
        return (
            f"Risk:\n{self.risk}\n\n"
            f"Key Reasons:\n{reasons_text}\n\n"
            f"Business Impact:\n{self.business_impact}\n\n"
            f"Recommended Action:\n{self.recommended_action}\n\n"
            f"Supporting Sources:\n{sources_text}\n\n"
            f"Confidence:\n{self.confidence}"
        )


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError


class OpenAILLMProvider(LLMProvider):
    def __init__(self, cfg: LLMConfig) -> None:
        if not cfg.api_key:
            raise ValueError("LLM_API_KEY or OPENAI_API_KEY must be set for OpenAI provider")
        self.cfg = cfg

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.cfg.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,
        }
        return _post_with_retry(
            url=f"{self.cfg.base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.cfg.api_key}",
                "Content-Type": "application/json",
            },
            payload=payload,
            timeout=self.cfg.timeout_seconds,
            max_retries=self.cfg.max_retries,
            response_parser=_parse_openai_response,
        )


class CortexLLMProvider(LLMProvider):
    def __init__(self, cfg: LLMConfig, cursor: Any) -> None:
        self.cfg = cfg
        self.cursor = cursor

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        prompt = f"{system_prompt}\n\n{user_prompt}"
        self.cursor.execute(
            "SELECT snowflake.cortex.complete(%s, %s) AS response",
            (self.cfg.model, prompt),
        )
        row = self.cursor.fetchone()
        if not row or row[0] is None:
            raise RuntimeError("Cortex LLM returned empty response")
        return str(row[0])


def _parse_openai_response(body: dict) -> str:
    return body["choices"][0]["message"]["content"]


def _post_with_retry(
    url: str,
    headers: dict[str, str],
    payload: dict,
    timeout: int,
    max_retries: int,
    response_parser,
) -> str:
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            return response_parser(body)
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError) as exc:
            last_error = exc
            sleep_s = 2 ** (attempt - 1)
            logger.warning("llm_request_failed attempt=%s error=%s retry_in=%ss", attempt, exc, sleep_s)
            time.sleep(sleep_s)
    raise RuntimeError(f"LLM request failed after {max_retries} attempts: {last_error}")


def build_llm_provider(cfg: AppConfig, cursor: Any | None = None) -> LLMProvider:
    if cfg.llm.provider == "cortex":
        if cursor is None:
            conn = get_connection(cfg.snowflake, schema="AI")
            cursor = conn.cursor()
        return CortexLLMProvider(cfg.llm, cursor)
    if cfg.llm.provider == "openai":
        return OpenAILLMProvider(cfg.llm)
    raise ValueError(f"Unsupported LLM_PROVIDER: {cfg.llm.provider}")


def _extract_section(text: str, header: str) -> str:
    pattern = rf"{re.escape(header)}\s*(.*?)(?=\n[A-Z][A-Za-z ]+:|$)"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ""


def _extract_bullets(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    bullets = []
    for line in lines:
        if line.startswith(("-", "*", "•")):
            bullets.append(line.lstrip("-*• ").strip())
        elif not bullets and line:
            bullets.append(line)
    return bullets


def parse_llm_response(raw: str, fallback_sources: list[str]) -> dict[str, Any]:
    if INSUFFICIENT_DATA.lower() in raw.lower():
        return {
            "risk": INSUFFICIENT_DATA,
            "reasons": [],
            "business_impact": "",
            "recommended_action": "",
            "sources": fallback_sources,
            "confidence": "Low",
            "status": "insufficient_data",
        }

    reasons_block = _extract_section(raw, "Key Reasons:")
    sources_block = _extract_section(raw, "Supporting Sources:")
    parsed_sources = [s.strip() for s in re.split(r"[,;\n]", sources_block) if s.strip()]
    sources = parsed_sources or fallback_sources

    return {
        "risk": _extract_section(raw, "Risk:") or "Unknown",
        "reasons": _extract_bullets(reasons_block),
        "business_impact": _extract_section(raw, "Business Impact:") or "Not specified",
        "recommended_action": _extract_section(raw, "Recommended Action:") or "Not specified",
        "sources": sources,
        "confidence": _extract_section(raw, "Confidence:") or "Medium",
        "status": "success",
    }


def _confidence_from_similarity(scores: list[float]) -> str:
    if not scores:
        return "Low"
    avg = sum(scores) / len(scores)
    if avg >= 0.75:
        return "High"
    if avg >= 0.55:
        return "Medium"
    return "Low"


def _collect_sources(documents: list[RetrievedDocument]) -> list[str]:
    sources: list[str] = []
    for doc in documents:
        sources.append(doc.document_id)
        for token in re.findall(r"\b(?:PO|SHP|S)\d+\b", doc.document_text):
            if token not in sources:
                sources.append(token)
    return sources


class SupplyChainRAG:
    def __init__(
        self,
        config: AppConfig | None = None,
        retriever: SupplyChainRetriever | None = None,
        llm_provider: LLMProvider | None = None,
    ) -> None:
        self.config = config or load_config()
        self.retriever = retriever or SupplyChainRetriever(self.config)
        self._llm_provider = llm_provider

    def answer_question(
        self,
        question: str,
        top_k: int = 5,
        filters: RetrievalFilters | None = None,
        hybrid: bool = True,
        min_similarity: float = 0.3,
    ) -> RAGAnswer:
        retrieval_start = time.perf_counter()
        if hybrid:
            documents = self.retriever.retrieve_hybrid(
                question, top_k=top_k, filters=filters
            )
        else:
            documents = self.retriever.retrieve(
                question,
                top_k=top_k,
                filters=filters,
                min_similarity=min_similarity,
            )
        retrieval_latency_ms = (time.perf_counter() - retrieval_start) * 1000

        source_ids = _collect_sources(documents)
        logger.info(
            "rag_retrieval question=%r documents_retrieved=%s source_document_ids=%s latency_ms=%.1f",
            question,
            len(documents),
            source_ids,
            retrieval_latency_ms,
        )

        if not documents:
            return RAGAnswer(
                question=question,
                risk=INSUFFICIENT_DATA,
                reasons=[],
                business_impact="",
                recommended_action="",
                sources=[],
                confidence="Low",
                raw_response=INSUFFICIENT_DATA,
                retrieval_count=0,
                retrieval_latency_ms=retrieval_latency_ms,
                llm_latency_ms=0.0,
                model=self.config.llm.model,
                status="insufficient_data",
            )

        context = build_context_block([doc.document_text for doc in documents])
        user_prompt = build_user_prompt(question, context)

        llm_start = time.perf_counter()
        provider = self._llm_provider or build_llm_provider(self.config)
        raw_response = provider.complete(SYSTEM_PROMPT, user_prompt)
        llm_latency_ms = (time.perf_counter() - llm_start) * 1000

        parsed = parse_llm_response(raw_response, fallback_sources=source_ids)
        if parsed["status"] == "insufficient_data":
            return RAGAnswer(
                question=question,
                risk=INSUFFICIENT_DATA,
                reasons=[],
                business_impact="",
                recommended_action="",
                sources=source_ids,
                confidence="Low",
                raw_response=raw_response,
                retrieval_count=len(documents),
                retrieval_latency_ms=retrieval_latency_ms,
                llm_latency_ms=llm_latency_ms,
                model=self.config.llm.model,
                status="insufficient_data",
            )

        confidence = parsed["confidence"] or _confidence_from_similarity(
            [doc.similarity_score for doc in documents]
        )

        answer = RAGAnswer(
            question=question,
            risk=parsed["risk"],
            reasons=parsed["reasons"],
            business_impact=parsed["business_impact"],
            recommended_action=parsed["recommended_action"],
            sources=parsed["sources"],
            confidence=confidence,
            raw_response=raw_response,
            retrieval_count=len(documents),
            retrieval_latency_ms=retrieval_latency_ms,
            llm_latency_ms=llm_latency_ms,
            model=self.config.llm.model,
            status="success",
        )
        logger.info(
            "rag_complete status=%s model=%s llm_latency_ms=%.1f token_usage=n/a",
            answer.status,
            answer.model,
            llm_latency_ms,
        )
        return answer


def answer_question(question: str, **kwargs) -> RAGAnswer:
    return SupplyChainRAG().answer_question(question, **kwargs)
