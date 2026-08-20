"""Persist truck load inspections locally and in Snowflake."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.config import PROJECT_ROOT, load_config
from src.dock_vision.schemas import LoadInspection

DATA_DIR = PROJECT_ROOT / "data" / "dock_vision"
PHOTO_DIR = DATA_DIR / "photos"
INSPECTIONS_CSV = DATA_DIR / "inspections.csv"

COLUMNS = [
    "inspection_id",
    "truck_id",
    "trip_id",
    "warehouse_id",
    "route_id",
    "dock_id",
    "planned_pallets",
    "planned_load_pct",
    "estimated_load_pct",
    "status",
    "issue_codes",
    "confidence",
    "recommendation",
    "supervisor_action",
    "captured_at",
    "photo_path",
    "synced_to_snowflake",
]


def ensure_data_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    if not INSPECTIONS_CSV.exists():
        pd.DataFrame(columns=COLUMNS).to_csv(INSPECTIONS_CSV, index=False)


def save_photo(inspection_id: str, image_bytes: bytes) -> str:
    ensure_data_dirs()
    photo_path = PHOTO_DIR / f"{inspection_id}.jpg"
    photo_path.write_bytes(image_bytes)
    return str(photo_path.relative_to(PROJECT_ROOT))


def append_inspection(inspection: LoadInspection) -> dict[str, Any]:
    ensure_data_dirs()
    record = inspection.to_record()
    frame = pd.DataFrame([record])
    if INSPECTIONS_CSV.exists() and INSPECTIONS_CSV.stat().st_size > 0:
        frame.to_csv(INSPECTIONS_CSV, mode="a", header=False, index=False)
    else:
        frame.to_csv(INSPECTIONS_CSV, index=False)
    return record


def load_inspections() -> pd.DataFrame:
    ensure_data_dirs()
    if not INSPECTIONS_CSV.exists() or INSPECTIONS_CSV.stat().st_size == 0:
        return pd.DataFrame(columns=COLUMNS)
    frame = pd.read_csv(INSPECTIONS_CSV)
    if "captured_at" in frame.columns:
        frame["captured_at"] = pd.to_datetime(frame["captured_at"], utc=True, errors="coerce")
    return frame


def _snowflake_available() -> bool:
    cfg = load_config().snowflake
    key_path = Path(cfg.private_key_path)
    return bool(cfg.account and cfg.user and key_path.exists())


def sync_unsynced_to_snowflake() -> int:
    """Push local inspections not yet synced to Snowflake RAW.DV_LOAD_INSPECTIONS."""
    if not _snowflake_available():
        return 0

    from snowflake.connector.pandas_tools import write_pandas

    from src.snowflake_client import get_connection

    frame = load_inspections()
    if frame.empty:
        return 0

    pending = frame[frame["synced_to_snowflake"].fillna(False).astype(bool) == False]  # noqa: E712
    if pending.empty:
        return 0

    upload = pending.copy()
    upload.columns = [col.upper() for col in upload.columns]
    upload["ISSUE_CODES"] = upload["ISSUE_CODES"].fillna("")
    upload["CAPTURED_AT"] = pd.to_datetime(upload["CAPTURED_AT"], utc=True, errors="coerce")
    upload["SYNCED_TO_SNOWFLAKE"] = True

    cfg = load_config().snowflake
    conn = get_connection(cfg, schema="RAW")
    try:
        success, _, row_count, _ = write_pandas(
            conn,
            upload,
            "DV_LOAD_INSPECTIONS",
            database=cfg.database,
            schema="RAW",
            auto_create_table=False,
            quote_identifiers=False,
        )
        if not success:
            raise RuntimeError("Snowflake write_pandas returned success=False")
    finally:
        conn.close()

    frame.loc[pending.index, "synced_to_snowflake"] = True
    frame.to_csv(INSPECTIONS_CSV, index=False)
    return int(row_count)


def dashboard_metrics(frame: pd.DataFrame) -> dict[str, Any]:
    if frame.empty:
        return {
            "total_inspections": 0,
            "avg_load_pct": 0.0,
            "underloaded_count": 0,
            "optimal_count": 0,
            "unsafe_count": 0,
            "utilization_gap": 0.0,
        }

    underloaded = frame["status"].eq("UNDERLOADED").sum()
    optimal = frame["status"].eq("OPTIMAL").sum()
    unsafe = frame["status"].isin(["UNSAFE", "OVERLOADED"]).sum()
    avg_load = float(frame["estimated_load_pct"].mean())
    planned = float(frame["planned_load_pct"].mean()) if "planned_load_pct" in frame else 100.0

    return {
        "total_inspections": int(len(frame)),
        "avg_load_pct": round(avg_load, 1),
        "underloaded_count": int(underloaded),
        "optimal_count": int(optimal),
        "unsafe_count": int(unsafe),
        "utilization_gap": round(planned - avg_load, 1),
    }


def metrics_by_warehouse(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["warehouse_id", "inspections", "avg_load_pct", "underloaded_count"])
    grouped = (
        frame.groupby("warehouse_id", as_index=False)
        .agg(
            inspections=("inspection_id", "count"),
            avg_load_pct=("estimated_load_pct", "mean"),
            underloaded_count=("status", lambda s: int((s == "UNDERLOADED").sum())),
        )
        .sort_values("avg_load_pct")
    )
    grouped["avg_load_pct"] = grouped["avg_load_pct"].round(1)
    return grouped


def metrics_by_route(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["route_id", "inspections", "avg_load_pct"])
    grouped = (
        frame.groupby("route_id", as_index=False)
        .agg(
            inspections=("inspection_id", "count"),
            avg_load_pct=("estimated_load_pct", "mean"),
        )
        .sort_values("avg_load_pct")
    )
    grouped["avg_load_pct"] = grouped["avg_load_pct"].round(1)
    return grouped


def recent_inspections(frame: pd.DataFrame, limit: int = 20) -> pd.DataFrame:
    if frame.empty:
        return frame
    cols = [
        "captured_at",
        "truck_id",
        "warehouse_id",
        "route_id",
        "estimated_load_pct",
        "planned_load_pct",
        "status",
        "issue_codes",
        "supervisor_action",
    ]
    available = [col for col in cols if col in frame.columns]
    ordered = frame.sort_values("captured_at", ascending=False)
    return ordered[available].head(limit)
