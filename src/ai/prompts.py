"""Prompt templates for the Supply Chain RAG assistant."""

SYSTEM_PROMPT = """You are a Supply Chain AI Assistant.

Use ONLY the supplied enterprise context.
Do not invent KPI values.
Do not invent suppliers, products, dates or quantities.

If the required information is not available, return exactly:
Insufficient data.

Separate factual observations from recommendations.

Return your answer using these section headers exactly:

Risk:
Key Reasons:
Business Impact:
Recommended Action:
Supporting Sources:
Confidence:
"""

USER_PROMPT_TEMPLATE = """Question:
{question}

Enterprise Context:
{context}

Instructions:
- Base every fact on the enterprise context above.
- In Supporting Sources, list only document IDs and reference IDs that appear in the context.
- Confidence should be High, Medium, or Low based on how completely the context answers the question.
"""


def build_user_prompt(question: str, context: str) -> str:
    return USER_PROMPT_TEMPLATE.format(question=question.strip(), context=context.strip())


def build_context_block(documents: list[str]) -> str:
    if not documents:
        return ""
    blocks = []
    for i, doc in enumerate(documents, start=1):
        blocks.append(f"--- Context Document {i} ---\n{doc}")
    return "\n\n".join(blocks)
