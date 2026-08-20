#!/usr/bin/env python3
"""Generate sample truck load inspection data for DockVision demos."""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "dock_vision"
OUTPUT = DATA_DIR / "inspections.csv"

WAREHOUSES = ["LON", "MAN", "BHM", "GLA"]
ROUTES = ["RT-MAN-01", "RT-BHM-02", "RT-GLA-03", "RT-LON-04"]
STATUSES = ["OPTIMAL", "UNDERLOADED", "UNDERLOADED", "OPTIMAL", "UNSAFE"]
ISSUES = {
    "OPTIMAL": "",
    "UNDERLOADED": "below_target|low_fill",
    "UNSAFE": "uneven_loading",
}


def generate_rows(count: int = 40) -> pd.DataFrame:
    random.seed(42)
    now = datetime.now(timezone.utc)
    rows = []
    for idx in range(count):
        status = random.choice(STATUSES)
        planned = random.choice([92.0, 95.0, 100.0])
        if status == "OPTIMAL":
            estimated = round(random.uniform(90.0, 97.0), 1)
        elif status == "UNDERLOADED":
            estimated = round(random.uniform(62.0, 88.0), 1)
        else:
            estimated = round(random.uniform(78.0, 92.0), 1)

        captured_at = now - timedelta(hours=random.randint(1, 240))
        rows.append(
            {
                "inspection_id": f"INS-SAMPLE{idx:04d}",
                "truck_id": f"TRK-{4400 + idx}",
                "trip_id": f"TRIP-{10000 + idx}",
                "warehouse_id": random.choice(WAREHOUSES),
                "route_id": random.choice(ROUTES),
                "dock_id": random.choice(["D01", "D02", "D03"]),
                "planned_pallets": random.choice([20, 22, 24, 26]),
                "planned_load_pct": planned,
                "estimated_load_pct": estimated,
                "status": status,
                "issue_codes": ISSUES[status],
                "confidence": round(random.uniform(0.72, 0.93), 3),
                "recommendation": "Sample generated record for dashboard demo.",
                "supervisor_action": random.choice(["APPROVE", "TOP_UP", "HOLD"]),
                "captured_at": captured_at.isoformat(),
                "photo_path": "",
                "synced_to_snowflake": False,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    frame = generate_rows()
    frame.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(frame)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
