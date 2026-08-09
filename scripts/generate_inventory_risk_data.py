#!/usr/bin/env python3
"""Generate intentional inventory-risk demo CSVs for the simple AI assistant.

Outputs to data/inventory_risk/ — does not touch data/ Control Tower files.
"""

from __future__ import annotations

import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "data" / "inventory_risk"
SNAPSHOT_DATE = "2026-08-09"

# (product_id, product_name, warehouse, stock_qty, daily_demand, risk_tier)
PRODUCTS = [
    # CRITICAL — <1 day supply + delayed supply chain
    ("P001", "Coconut Body Wash", "LON", 50, 100, "CRITICAL"),
    ("P002", "Baby Formula Stage 1", "NYC", 120, 200, "CRITICAL"),
    ("P003", "Frozen Pizza Margherita", "CHI", 80, 150, "CRITICAL"),
    # HIGH — <2 days supply or poor supplier
    ("P004", "Dark Chocolate 70%", "LON", 180, 120, "HIGH"),
    ("P005", "Energy Drink Citrus", "NYC", 200, 140, "HIGH"),
    ("P006", "Sunscreen SPF50", "AMS", 90, 70, "HIGH"),
    # MEDIUM — 2–5 days supply
    ("P007", "Olive Oil Extra Virgin", "LON", 400, 80, "MEDIUM"),
    ("P008", "Whole Grain Pasta", "NYC", 350, 60, "MEDIUM"),
    ("P009", "Granola Honey Crunch", "CHI", 280, 50, "MEDIUM"),
    # HEALTHY — comfortable buffer
    ("P010", "Sparkling Mineral Water", "LON", 2000, 100, "HEALTHY"),
    ("P011", "Green Tea Organic", "NYC", 1500, 90, "HEALTHY"),
    ("P012", "Basmati Rice 5kg", "CHI", 3000, 120, "HEALTHY"),
    ("P013", "Laundry Detergent Pods", "AMS", 600, 40, "HEALTHY"),
    ("P014", "Hand Soap Lavender", "SIN", 450, 55, "MEDIUM"),
    ("P015", "Vitamin C Tablets", "LON", 220, 45, "HIGH"),
]

# (supplier_id, supplier_name, product_id, lead_time_days, supplier_otd_pct)
SUPPLIERS = [
    ("S001", "ABC Personal Care Ltd", "P001", 7, 72),
    ("S002", "Nordic Nutrition Co", "P002", 10, 68),
    ("S003", "Baltic Frozen Foods", "P003", 12, 75),
    ("S004", "Andes Cocoa Partners", "P004", 8, 78),
    ("S005", "Pacific Beverage Inc", "P005", 6, 76),
    ("S006", "Alpine Health Supply", "P006", 9, 79),
    ("S007", "Mediterranean Oils SA", "P007", 7, 92),
    ("S008", "Great Plains Grains", "P008", 5, 94),
    ("S009", "Sunrise Snacks LLC", "P009", 6, 91),
    ("S010", "Alpine Spring Waters", "P010", 5, 97),
    ("S011", "Tokyo Tea Works", "P011", 8, 96),
    ("S012", "Himalaya Rice Exports", "P012", 14, 95),
    ("S013", "Euro Household GmbH", "P013", 7, 93),
    ("S014", "Asia Pacific Hygiene", "P014", 10, 88),
    ("S015", "Wellness Labs Inc", "P015", 7, 77),
]

# (po_id, product_id, supplier_id, ordered_qty, expected_date, status)
PURCHASE_ORDERS = [
    ("PO001", "P001", "S001", 800, "2026-08-05", "DELAYED"),
    ("PO002", "P002", "S002", 1200, "2026-08-03", "DELAYED"),
    ("PO003", "P003", "S003", 900, "2026-08-04", "DELAYED"),
    ("PO004", "P004", "S004", 600, "2026-08-07", "OPEN"),
    ("PO005", "P005", "S005", 700, "2026-08-06", "DELAYED"),
    ("PO006", "P006", "S006", 400, "2026-08-08", "OPEN"),
    ("PO007", "P007", "S007", 500, "2026-08-10", "OPEN"),
    ("PO008", "P008", "S008", 450, "2026-08-11", "RECEIVED"),
    ("PO009", "P009", "S009", 350, "2026-08-09", "OPEN"),
    ("PO010", "P010", "S010", 1000, "2026-08-12", "RECEIVED"),
    ("PO011", "P011", "S011", 800, "2026-08-12", "RECEIVED"),
    ("PO012", "P012", "S012", 1500, "2026-08-13", "RECEIVED"),
    ("PO013", "P013", "S013", 300, "2026-08-14", "RECEIVED"),
    ("PO014", "P014", "S014", 250, "2026-08-08", "OPEN"),
    ("PO015", "P015", "S015", 350, "2026-08-07", "DELAYED"),
]

# (shipment_id, po_id, shipment_date, expected_delivery, actual_delivery, status)
SHIPMENTS = [
    ("SHP001", "PO001", "2026-07-28", "2026-08-05", "", "DELAYED"),
    ("SHP002", "PO002", "2026-07-25", "2026-08-03", "", "DELAYED"),
    ("SHP003", "PO003", "2026-07-26", "2026-08-04", "", "DELAYED"),
    ("SHP004", "PO004", "2026-08-01", "2026-08-07", "", "IN_TRANSIT"),
    ("SHP005", "PO005", "2026-07-30", "2026-08-06", "", "DELAYED"),
    ("SHP006", "PO006", "2026-08-02", "2026-08-08", "", "IN_TRANSIT"),
    ("SHP007", "PO007", "2026-08-04", "2026-08-10", "", "IN_TRANSIT"),
    ("SHP008", "PO008", "2026-08-01", "2026-08-08", "2026-08-08", "ON_TIME"),
    ("SHP009", "PO009", "2026-08-03", "2026-08-09", "", "IN_TRANSIT"),
    ("SHP010", "PO010", "2026-08-05", "2026-08-12", "2026-08-11", "ON_TIME"),
    ("SHP011", "PO011", "2026-08-05", "2026-08-12", "2026-08-12", "ON_TIME"),
    ("SHP012", "PO012", "2026-08-06", "2026-08-13", "2026-08-13", "ON_TIME"),
    ("SHP013", "PO013", "2026-08-07", "2026-08-14", "2026-08-14", "ON_TIME"),
    ("SHP014", "PO014", "2026-08-01", "2026-08-08", "", "IN_TRANSIT"),
    ("SHP015", "PO015", "2026-07-29", "2026-08-07", "", "DELAYED"),
]

# (product_id, forecast_date, forecast_demand)
FORECAST = [
    ("P001", "2026-08-10", 120),
    ("P001", "2026-08-11", 115),
    ("P002", "2026-08-10", 220),
    ("P002", "2026-08-11", 210),
    ("P003", "2026-08-10", 160),
    ("P003", "2026-08-11", 155),
    ("P004", "2026-08-10", 125),
    ("P005", "2026-08-10", 150),
    ("P006", "2026-08-10", 75),
    ("P007", "2026-08-10", 85),
    ("P008", "2026-08-10", 62),
    ("P009", "2026-08-10", 52),
    ("P010", "2026-08-10", 98),
    ("P011", "2026-08-10", 88),
    ("P012", "2026-08-10", 118),
    ("P013", "2026-08-10", 38),
    ("P014", "2026-08-10", 58),
    ("P015", "2026-08-10", 48),
]


def write_csv(name: str, fieldnames: list[str], rows: list[dict]) -> None:
    path = OUT_DIR / name
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows):>3} rows -> {path}")


def main() -> None:
    print("=== Generating Inventory Risk Assistant Data ===\n")

    inventory = [
        {
            "product_id": p[0],
            "product_name": p[1],
            "warehouse": p[2],
            "stock_qty": p[3],
            "daily_demand": p[4],
            "snapshot_date": SNAPSHOT_DATE,
        }
        for p in PRODUCTS
    ]
    write_csv(
        "inventory.csv",
        ["product_id", "product_name", "warehouse", "stock_qty", "daily_demand", "snapshot_date"],
        inventory,
    )

    suppliers = [
        {
            "supplier_id": s[0],
            "supplier_name": s[1],
            "product_id": s[2],
            "lead_time_days": s[3],
            "supplier_otd_pct": s[4],
        }
        for s in SUPPLIERS
    ]
    write_csv(
        "suppliers.csv",
        ["supplier_id", "supplier_name", "product_id", "lead_time_days", "supplier_otd_pct"],
        suppliers,
    )

    pos = [
        {
            "po_id": p[0],
            "product_id": p[1],
            "supplier_id": p[2],
            "ordered_qty": p[3],
            "expected_date": p[4],
            "status": p[5],
        }
        for p in PURCHASE_ORDERS
    ]
    write_csv(
        "purchase_orders.csv",
        ["po_id", "product_id", "supplier_id", "ordered_qty", "expected_date", "status"],
        pos,
    )

    shipments = [
        {
            "shipment_id": s[0],
            "po_id": s[1],
            "shipment_date": s[2],
            "expected_delivery": s[3],
            "actual_delivery": s[4],
            "status": s[5],
        }
        for s in SHIPMENTS
    ]
    write_csv(
        "shipments.csv",
        ["shipment_id", "po_id", "shipment_date", "expected_delivery", "actual_delivery", "status"],
        shipments,
    )

    forecast = [
        {"product_id": f[0], "forecast_date": f[1], "forecast_demand": f[2]}
        for f in FORECAST
    ]
    write_csv("forecast.csv", ["product_id", "forecast_date", "forecast_demand"], forecast)

    tiers = {}
    for p in PRODUCTS:
        tiers[p[5]] = tiers.get(p[5], 0) + 1
    print("\n=== Risk tier distribution ===")
    for tier, count in sorted(tiers.items()):
        print(f"  {tier}: {count} products")
    print("\n=== Complete ===")


if __name__ == "__main__":
    main()
