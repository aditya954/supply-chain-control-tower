"""Data models for truck load inspections."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class LoadStatus(str, Enum):
    OPTIMAL = "OPTIMAL"
    UNDERLOADED = "UNDERLOADED"
    OVERLOADED = "OVERLOADED"
    UNSAFE = "UNSAFE"


@dataclass
class LoadAnalysisResult:
    estimated_load_pct: float
    status: LoadStatus
    issue_codes: list[str]
    confidence: float
    recommendation: str
    cargo_fill_score: float
    uneven_load_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "estimated_load_pct": round(self.estimated_load_pct, 1),
            "status": self.status.value,
            "issue_codes": self.issue_codes,
            "confidence": round(self.confidence, 3),
            "recommendation": self.recommendation,
            "cargo_fill_score": round(self.cargo_fill_score, 3),
            "uneven_load_score": round(self.uneven_load_score, 3),
        }


@dataclass
class LoadInspection:
    inspection_id: str
    truck_id: str
    trip_id: str
    warehouse_id: str
    route_id: str
    dock_id: str
    planned_pallets: int
    planned_load_pct: float
    estimated_load_pct: float
    status: LoadStatus
    issue_codes: list[str]
    confidence: float
    recommendation: str
    supervisor_action: str
    captured_at: datetime
    photo_path: str = ""
    synced_to_snowflake: bool = False

    @classmethod
    def create(
        cls,
        *,
        truck_id: str,
        trip_id: str,
        warehouse_id: str,
        route_id: str,
        dock_id: str,
        planned_pallets: int,
        planned_load_pct: float,
        analysis: LoadAnalysisResult,
        supervisor_action: str = "PENDING",
        photo_path: str = "",
    ) -> LoadInspection:
        return cls(
            inspection_id=f"INS-{uuid4().hex[:12].upper()}",
            truck_id=truck_id.strip().upper(),
            trip_id=trip_id.strip().upper(),
            warehouse_id=warehouse_id.strip().upper(),
            route_id=route_id.strip().upper(),
            dock_id=dock_id.strip().upper(),
            planned_pallets=planned_pallets,
            planned_load_pct=planned_load_pct,
            estimated_load_pct=analysis.estimated_load_pct,
            status=analysis.status,
            issue_codes=analysis.issue_codes,
            confidence=analysis.confidence,
            recommendation=analysis.recommendation,
            supervisor_action=supervisor_action,
            captured_at=datetime.now(timezone.utc),
            photo_path=photo_path,
        )

    def to_record(self) -> dict[str, Any]:
        record = asdict(self)
        record["status"] = self.status.value
        record["issue_codes"] = "|".join(self.issue_codes)
        record["captured_at"] = self.captured_at.isoformat()
        return record
