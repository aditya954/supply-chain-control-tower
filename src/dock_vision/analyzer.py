"""Estimate truck load completion from rear-door photos."""

from __future__ import annotations

from io import BytesIO

import numpy as np
from PIL import Image

from src.dock_vision.schemas import LoadAnalysisResult, LoadStatus

TARGET_LOAD_PCT = 90.0


def _crop_cargo_region(gray: np.ndarray) -> np.ndarray:
    height, _ = gray.shape
    top = int(height * 0.2)
    bottom = int(height * 0.95)
    left = int(gray.shape[1] * 0.08)
    right = int(gray.shape[1] * 0.92)
    return gray[top:bottom, left:right]


def _fill_score(region: np.ndarray) -> float:
    normalized = region.astype(np.float32) / 255.0
    variation = float(np.std(normalized))
    dark_ratio = float(np.mean(normalized < np.percentile(normalized, 35)))
    gradient = float(np.mean(np.abs(np.diff(normalized, axis=0))))
    score = (dark_ratio * 0.55) + (variation * 0.30) + (min(gradient * 4.0, 1.0) * 0.15)
    return max(0.0, min(1.0, score))


def _uneven_score(region: np.ndarray) -> float:
    midpoint = region.shape[1] // 2
    left = region[:, :midpoint]
    right = region[:, midpoint:]
    left_fill = _fill_score(left)
    right_fill = _fill_score(right)
    return abs(left_fill - right_fill)


def _status_for_load(estimated_load_pct: float, uneven_score: float) -> LoadStatus:
    if uneven_score >= 0.22 and estimated_load_pct >= 70:
        return LoadStatus.UNSAFE
    if estimated_load_pct > 98:
        return LoadStatus.OVERLOADED
    if estimated_load_pct < TARGET_LOAD_PCT:
        return LoadStatus.UNDERLOADED
    return LoadStatus.OPTIMAL


def _issue_codes(estimated_load_pct: float, uneven_score: float, planned_load_pct: float) -> list[str]:
    issues: list[str] = []
    if estimated_load_pct < 75:
        issues.append("low_fill")
    elif estimated_load_pct < TARGET_LOAD_PCT:
        issues.append("below_target")
    if uneven_score >= 0.18:
        issues.append("uneven_loading")
    if estimated_load_pct + 8 < planned_load_pct:
        issues.append("manifest_gap")
    if estimated_load_pct > 98:
        issues.append("possible_overload")
    return issues


def _recommendation(status: LoadStatus, estimated_load_pct: float, issue_codes: list[str]) -> str:
    gap = max(0.0, TARGET_LOAD_PCT - estimated_load_pct)
    if status == LoadStatus.OPTIMAL:
        return "Truck load meets target. Approve departure."
    if status == LoadStatus.OVERLOADED:
        return "Load appears above safe capacity. Re-check weight limits before departure."
    if status == LoadStatus.UNSAFE:
        return "Uneven loading detected. Re-stack cargo for balance before departure."
    if "manifest_gap" in issue_codes:
        return (
            f"Truck is ~{gap:.0f}% below target and below the load plan. "
            "Add compatible pallets from the same route before release."
        )
    return (
        f"Truck is ~{gap:.0f}% below target. "
        "Top up with pending orders on this route or consolidate shipments."
    )


def analyze_truck_load(
    image_bytes: bytes,
    *,
    planned_load_pct: float = 100.0,
    target_load_pct: float = TARGET_LOAD_PCT,
) -> LoadAnalysisResult:
    """Estimate load completion from a truck rear-door photo."""
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    gray = np.array(image.convert("L"), dtype=np.float32)
    cargo_region = _crop_cargo_region(gray)

    fill_score = _fill_score(cargo_region)
    uneven_score = _uneven_score(cargo_region)
    estimated_load_pct = max(5.0, min(100.0, fill_score * 105.0))

    status = _status_for_load(estimated_load_pct, uneven_score)
    issues = _issue_codes(estimated_load_pct, uneven_score, planned_load_pct)
    confidence = max(0.55, min(0.95, 0.65 + (fill_score * 0.2) - (uneven_score * 0.15)))

    if status == LoadStatus.OPTIMAL and estimated_load_pct < target_load_pct:
        status = LoadStatus.UNDERLOADED
        if "below_target" not in issues:
            issues.append("below_target")

    return LoadAnalysisResult(
        estimated_load_pct=round(estimated_load_pct, 1),
        status=status,
        issue_codes=issues,
        confidence=round(confidence, 3),
        recommendation=_recommendation(status, estimated_load_pct, issues),
        cargo_fill_score=round(fill_score, 3),
        uneven_load_score=round(uneven_score, 3),
    )
