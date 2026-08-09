#!/usr/bin/env python3
"""Generate synthetic consumer-products supply chain data for the AI Control Tower.

Outputs CSV files to data/ with embedded risk scenarios:
  HEALTHY, WARNING, HIGH_RISK, CRITICAL
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

RANDOM_SEED = 20260809
random.seed(RANDOM_SEED)

TODAY = date(2026, 8, 9)
HISTORY_START = TODAY - timedelta(days=89)  # 90 days inclusive
FORECAST_END = TODAY + timedelta(days=29)   # 30 days forecast

PRODUCTS = [
    ("P001", "Coconut Water", "Beverages"),
    ("P002", "Olive Oil Extra Virgin", "Pantry"),
    ("P003", "Organic Almond Milk", "Beverages"),
    ("P004", "Dark Chocolate 70%", "Snacks"),
    ("P005", "Whole Grain Pasta", "Pantry"),
    ("P006", "Greek Yogurt Plain", "Dairy"),
    ("P007", "Sparkling Mineral Water", "Beverages"),
    ("P008", "Granola Honey Crunch", "Snacks"),
    ("P009", "Canned Tuna", "Pantry"),
    ("P010", "Plant Protein Powder", "Health"),
    ("P011", "Baby Formula Stage 1", "Baby"),
    ("P012", "Diapers Size 3", "Baby"),
    ("P013", "Laundry Detergent Pods", "Household"),
    ("P014", "Hand Sanitizer 500ml", "Personal Care"),
    ("P015", "Sunscreen SPF50", "Personal Care"),
    ("P016", "Frozen Berries Mix", "Frozen"),
    ("P017", "Avocado Oil", "Pantry"),
    ("P018", "Rice Basmati 5kg", "Pantry"),
    ("P019", "Energy Drink Citrus", "Beverages"),
    ("P020", "Pet Food Premium", "Pet"),
    ("P021", "Vitamin C Tablets", "Health"),
    ("P022", "Coffee Beans Arabica", "Beverages"),
    ("P023", "Tea Green Organic", "Beverages"),
    ("P024", "Tomato Sauce", "Pantry"),
    ("P025", "Chicken Broth", "Pantry"),
    ("P026", "Butter Unsalted", "Dairy"),
    ("P027", "Cheese Cheddar Block", "Dairy"),
    ("P028", "Frozen Pizza Margherita", "Frozen"),
    ("P029", "Sparkling Water Lime", "Beverages"),
    ("P030", "Protein Bars Chocolate", "Health"),
]

WAREHOUSES = [
    ("W01", "London DC", "UK", 50000, 0),
    ("W02", "Rotterdam DC", "NL", 60000, 0),
    ("W03", "Chicago DC", "US", 80000, 0),
    ("W04", "Dallas DC", "US", 70000, 0),
    ("W05", "Singapore DC", "SG", 45000, 0),
    ("W06", "Sydney DC", "AU", 40000, 0),
    ("W07", "Toronto DC", "CA", 55000, 0),
    ("W08", "Mumbai DC", "IN", 65000, 0),
]

SUPPLIERS = [
    ("S01", "Pacific Harvest Co", "PH", 12, 94.0, 97.5),
    ("S02", "Mediterranean Oils Ltd", "IT", 10, 91.0, 96.0),
    ("S03", "Nordic Dairy Group", "SE", 8, 88.0, 95.0),
    ("S04", "Andes Cocoa Partners", "PE", 18, 72.0, 88.0),   # poor OTIF
    ("S05", "Great Plains Grains", "US", 7, 96.0, 98.0),
    ("S06", "Alpine Spring Waters", "CH", 9, 93.0, 97.0),
    ("S07", "Sunrise Nutrition Labs", "US", 14, 85.0, 92.0),
    ("S08", "Gulf Packaging Inc", "AE", 16, 68.0, 90.0),    # poor OTIF
    ("S09", "Baltic Frozen Foods", "PL", 11, 90.0, 94.0),
    ("S10", "Amazonia Organics", "BR", 20, 78.0, 91.0),
    ("S11", "Tokyo Beverage Works", "JP", 13, 92.0, 96.5),
    ("S12", "Cape Citrus Exports", "ZA", 15, 82.0, 93.0),
    ("S13", "Himalaya Health Supply", "IN", 17, 75.0, 89.0),
    ("S14", "Canadian Maple Co", "CA", 10, 95.0, 97.0),
    ("S15", "Euro Pet Nutrition", "DE", 9, 89.0, 94.5),
]

# product_id -> (risk_tier, primary_supplier, notes)
RISK_PROFILES: dict[str, tuple[str, str, str]] = {
    "P001": ("CRITICAL", "S10", "Coconut — low stock London, delayed shipment, high demand"),
    "P002": ("HEALTHY", "S02", "Stable olive oil supply"),
    "P003": ("WARNING", "S07", "Rising demand, moderate supplier lead time"),
    "P004": ("HIGH_RISK", "S04", "Poor supplier OTIF, shipment delays"),
    "P005": ("HEALTHY", "S05", "Adequate inventory across regions"),
    "P006": ("WARNING", "S03", "Seasonal demand uptick"),
    "P007": ("HEALTHY", "S06", "Strong spring water supply"),
    "P008": ("HEALTHY", "S05", "Normal granola replenishment"),
    "P009": ("WARNING", "S08", "Packaging supplier reliability issues"),
    "P010": ("HIGH_RISK", "S13", "Quality concerns, long lead time"),
    "P011": ("CRITICAL", "S07", "Baby formula — regulatory + stockout risk"),
    "P012": ("WARNING", "S08", "Diapers — warehouse near capacity"),
    "P013": ("HEALTHY", "S08", "Household stable"),
    "P014": ("HEALTHY", "S07", "Sanitizer adequate"),
    "P015": ("HIGH_RISK", "S12", "Seasonal spike + delayed inbound"),
    "P016": ("WARNING", "S09", "Cold chain minor delays"),
    "P017": ("HEALTHY", "S02", "Avocado oil stable"),
    "P018": ("HEALTHY", "S05", "Rice — excess in Dallas, low in Mumbai"),
    "P019": ("HIGH_RISK", "S11", "Energy drink — demand surge"),
    "P020": ("WARNING", "S15", "Pet food moderate risk"),
    "P021": ("HEALTHY", "S13", "Vitamins stable"),
    "P022": ("WARNING", "S11", "Coffee — forecast error"),
    "P023": ("HEALTHY", "S11", "Tea stable"),
    "P024": ("HEALTHY", "S02", "Sauce stable"),
    "P025": ("WARNING", "S05", "Broth seasonal"),
    "P026": ("HIGH_RISK", "S03", "Dairy cold chain disruption"),
    "P027": ("WARNING", "S03", "Cheese — utilization high Rotterdam"),
    "P028": ("CRITICAL", "S09", "Frozen pizza — stockout + delayed PO"),
    "P029": ("HEALTHY", "S06", "Sparkling water OK"),
    "P030": ("WARNING", "S07", "Protein bars — moderate backlog"),
}

PO_STATUSES = ["OPEN", "PARTIAL", "RECEIVED", "CANCELLED"]
SHIPMENT_STATUSES = ["IN_TRANSIT", "DELIVERED", "DELAYED", "CANCELLED"]
SO_STATUSES = ["OPEN", "CONFIRMED", "SHIPPED", "DELIVERED", "BACKORDER", "CANCELLED"]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows):,} rows -> {path}")


def daterange(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def tier_multiplier(tier: str) -> tuple[float, float]:
    """Return (inventory_factor, demand_factor) for risk tier."""
    return {
        "HEALTHY": (1.4, 1.0),
        "WARNING": (0.9, 1.15),
        "HIGH_RISK": (0.45, 1.35),
        "CRITICAL": (0.15, 1.6),
    }[tier]


def generate_products() -> list[dict]:
    rows = []
    for pid, name, category in PRODUCTS:
        rows.append({
            "product_id": pid,
            "product_name": name,
            "category": category,
        })
    return rows


def generate_warehouses() -> list[dict]:
    rows = []
    for wid, name, country, capacity, _ in WAREHOUSES:
        used = random.randint(int(capacity * 0.45), int(capacity * 0.92))
        if wid == "W02" and random.random() < 0.9:
            used = int(capacity * 0.93)  # Rotterdam near capacity
        if wid == "W03":
            used = int(capacity * 0.55)  # Chicago has excess capacity
        rows.append({
            "warehouse_id": wid,
            "warehouse_name": name,
            "country": country,
            "capacity": capacity,
            "used_capacity": used,
        })
    return rows


def generate_suppliers() -> list[dict]:
    rows = []
    for sid, name, country, lead, otif, quality in SUPPLIERS:
        # Degrade OTIF for known bad suppliers
        if sid in ("S04", "S08", "S13"):
            otif = round(otif - random.uniform(0, 3), 1)
        rows.append({
            "supplier_id": sid,
            "supplier_name": name,
            "country": country,
            "lead_time_days": lead,
            "otif_pct": round(min(100, max(50, otif + random.uniform(-2, 2))), 1),
            "quality_pct": round(min(100, max(80, quality + random.uniform(-1.5, 1.5))), 1),
        })
    return rows


def generate_inventory() -> list[dict]:
    rows = []
    combos = set()
    # 30 products x 8 warehouses = 240 unique pairs; add historical snapshots to reach 500
    snapshot_dates = [
        TODAY.isoformat(),
        (TODAY - timedelta(days=7)).isoformat(),
        (TODAY - timedelta(days=14)).isoformat(),
    ]

    for snapshot in snapshot_dates:
        for pid, _, _ in PRODUCTS:
            for wid, _, _, _, _ in WAREHOUSES:
                key = (pid, wid, snapshot)
                if key in combos:
                    continue
                combos.add(key)
                tier, _, _ = RISK_PROFILES[pid]
                inv_f, dem_f = tier_multiplier(tier)
                base_demand = random.randint(40, 180)
                daily_demand = int(base_demand * dem_f)
                target_dos = random.uniform(10, 25)
                stock = max(0, int(daily_demand * target_dos * inv_f))

                if pid == "P001" and wid == "W01" and snapshot == TODAY.isoformat():
                    stock = 60
                    daily_demand = 100
                if pid == "P018" and wid == "W04" and snapshot == TODAY.isoformat():
                    stock = random.randint(8000, 12000)
                if pid == "P018" and wid == "W08" and snapshot == TODAY.isoformat():
                    stock = random.randint(80, 200)

                # Historical snapshots have slightly higher stock on average
                if snapshot != TODAY.isoformat():
                    stock = int(stock * random.uniform(1.05, 1.4))

                reserved = min(stock, int(stock * random.uniform(0.05, 0.35)))
                available = max(0, stock - reserved)
                rows.append({
                    "product_id": pid,
                    "warehouse_id": wid,
                    "snapshot_date": snapshot,
                    "stock_qty": stock,
                    "reserved_qty": reserved,
                    "available_qty": available,
                })
                if len(rows) >= 500:
                    return rows
    return rows


def generate_demand() -> list[dict]:
    rows = []
    product_wh_pairs = {(p[0], w[0]) for p in PRODUCTS for w in WAREHOUSES}
    # Use subset aligned with inventory for realism
    active_pairs = list(product_wh_pairs)
    random.shuffle(active_pairs)
    active_pairs = active_pairs[:120]

    for pid, wid in active_pairs:
        tier, _, _ = RISK_PROFILES[pid]
        _, dem_f = tier_multiplier(tier)
        base = random.randint(35, 150)
        if pid == "P001" and wid == "W01":
            base = 100

        for d in daterange(HISTORY_START, FORECAST_END):
            seasonality = 1.0 + 0.1 * ((d.month % 6) / 6)
            noise = random.uniform(0.85, 1.15)
            forecast = int(base * dem_f * seasonality)
            if d <= TODAY:
                actual = max(0, int(forecast * noise * random.uniform(0.9, 1.1)))
                rows.append({
                    "product_id": pid,
                    "warehouse_id": wid,
                    "date": d.isoformat(),
                    "actual_demand": actual,
                    "forecast_demand": forecast,
                })
            else:
                # Forecast only period — actual is null represented as empty
                bump = 1.18 if pid == "P001" and wid == "W01" else 1.0
                rows.append({
                    "product_id": pid,
                    "warehouse_id": wid,
                    "date": d.isoformat(),
                    "actual_demand": "",
                    "forecast_demand": int(forecast * bump),
                })
    return rows


def generate_purchase_orders() -> list[dict]:
    rows = []
    for i in range(1, 501):
        pid = random.choice(PRODUCTS)[0]
        tier, supplier_id, _ = RISK_PROFILES[pid]
        order_date = TODAY - timedelta(days=random.randint(5, 75))
        lead = next(s[3] for s in SUPPLIERS if s[0] == supplier_id)
        expected = order_date + timedelta(days=lead)
        ordered = random.randint(200, 8000)

        status = random.choices(
            PO_STATUSES, weights=[0.2, 0.25, 0.45, 0.1], k=1
        )[0]
        received = 0
        actual = ""

        if tier in ("HIGH_RISK", "CRITICAL"):
            delay = random.randint(3, 12)
            expected = order_date + timedelta(days=lead)
            if status != "CANCELLED":
                status = random.choices(["OPEN", "PARTIAL", "OPEN"], weights=[0.5, 0.35, 0.15])[0]
                if status == "PARTIAL":
                    received = int(ordered * random.uniform(0.2, 0.6))
                actual = ""
            if pid == "P001" and i <= 5:
                status = "OPEN"
                ordered = 5000
                received = 0
                expected = (TODAY - timedelta(days=4)).isoformat()
        else:
            delay = random.randint(0, 2)
            if status == "RECEIVED":
                received = ordered
                actual = (expected + timedelta(days=random.randint(-1, delay))).isoformat()
            elif status == "PARTIAL":
                received = int(ordered * random.uniform(0.4, 0.85))
                actual = (expected + timedelta(days=delay)).isoformat()

        rows.append({
            "po_id": f"PO{i:05d}",
            "product_id": pid,
            "supplier_id": supplier_id,
            "ordered_qty": ordered,
            "received_qty": received,
            "order_date": order_date.isoformat(),
            "expected_date": expected.isoformat() if isinstance(expected, date) else expected,
            "actual_date": actual,
            "status": status,
        })
    return rows


def generate_shipments(purchase_orders: list[dict]) -> list[dict]:
    rows = []
    po_by_id = {p["po_id"]: p for p in purchase_orders}
    po_ids = list(po_by_id.keys())
    for i in range(1, 501):
        po_id = random.choice(po_ids)
        po = po_by_id[po_id]
        pid = po["product_id"]
        tier, _, _ = RISK_PROFILES[pid]
        ship_date = date.fromisoformat(po["order_date"]) + timedelta(days=random.randint(1, 5))
        expected_delivery = date.fromisoformat(po["expected_date"])

        if tier in ("HIGH_RISK", "CRITICAL"):
            delay = random.randint(2, 10)
            status = random.choices(SHIPMENT_STATUSES, weights=[0.35, 0.2, 0.4, 0.05])[0]
        else:
            delay = random.randint(0, 2)
            status = random.choices(SHIPMENT_STATUSES, weights=[0.15, 0.7, 0.1, 0.05])[0]

        if pid == "P001" and i <= 8:
            status = "DELAYED"
            delay = 4
            expected_delivery = TODAY - timedelta(days=6)
            ship_date = TODAY - timedelta(days=14)

        actual = ""
        if status == "DELIVERED":
            actual = (expected_delivery + timedelta(days=delay)).isoformat()
        elif status == "DELAYED":
            actual = ""

        rows.append({
            "shipment_id": f"SHP{i:05d}",
            "po_id": po_id,
            "ship_date": ship_date.isoformat(),
            "expected_delivery": expected_delivery.isoformat(),
            "actual_delivery": actual,
            "status": status,
        })
    return rows


def generate_sales_orders() -> list[dict]:
    rows = []
    for i in range(1, 1001):
        pid = random.choice(PRODUCTS)[0]
        wid = random.choice(WAREHOUSES)[0]
        tier, _, _ = RISK_PROFILES[pid]
        order_date = TODAY - timedelta(days=random.randint(0, 60))
        promised = order_date + timedelta(days=random.randint(3, 14))
        qty = random.randint(10, 800)

        if tier == "CRITICAL":
            status = random.choices(SO_STATUSES, weights=[0.15, 0.2, 0.1, 0.15, 0.35, 0.05])[0]
        elif tier == "HIGH_RISK":
            status = random.choices(SO_STATUSES, weights=[0.1, 0.2, 0.2, 0.25, 0.2, 0.05])[0]
        else:
            status = random.choices(SO_STATUSES, weights=[0.08, 0.15, 0.25, 0.45, 0.05, 0.02])[0]

        delivery = ""
        if status in ("SHIPPED", "DELIVERED"):
            delay = random.randint(0, 5) if tier in ("HIGH_RISK", "CRITICAL") else random.randint(0, 2)
            delivery = (promised + timedelta(days=delay)).isoformat()
        if status == "BACKORDER":
            delivery = ""

        if pid == "P001" and wid == "W01" and i <= 15:
            status = random.choice(["BACKORDER", "OPEN", "CONFIRMED"])
            qty = random.randint(200, 600)
            delivery = ""

        rows.append({
            "order_id": f"SO{i:05d}",
            "product_id": pid,
            "warehouse_id": wid,
            "order_qty": qty,
            "promised_date": promised.isoformat(),
            "delivery_date": delivery,
            "status": status,
        })
    return rows


def main() -> None:
    print("=== Generating AI Supply Chain Control Tower Data ===")
    products = generate_products()
    write_csv(DATA_DIR / "products.csv", list(products[0].keys()), products)

    warehouses = generate_warehouses()
    write_csv(DATA_DIR / "warehouses.csv", list(warehouses[0].keys()), warehouses)

    suppliers = generate_suppliers()
    write_csv(DATA_DIR / "suppliers.csv", list(suppliers[0].keys()), suppliers)

    inventory = generate_inventory()
    write_csv(DATA_DIR / "inventory.csv", list(inventory[0].keys()), inventory)

    demand = generate_demand()
    write_csv(DATA_DIR / "demand.csv", list(demand[0].keys()), demand)

    purchase_orders = generate_purchase_orders()
    write_csv(DATA_DIR / "purchase_orders.csv", list(purchase_orders[0].keys()), purchase_orders)

    shipments = generate_shipments(purchase_orders)
    write_csv(DATA_DIR / "shipments.csv", list(shipments[0].keys()), shipments)

    sales_orders = generate_sales_orders()
    write_csv(DATA_DIR / "sales_orders.csv", list(sales_orders[0].keys()), sales_orders)

    print("\n=== Summary ===")
    print(f"Products:         {len(products)}")
    print(f"Warehouses:       {len(warehouses)}")
    print(f"Suppliers:        {len(suppliers)}")
    print(f"Inventory:        {len(inventory)}")
    print(f"Demand rows:      {len(demand)}")
    print(f"Purchase orders:  {len(purchase_orders)}")
    print(f"Shipments:        {len(shipments)}")
    print(f"Sales orders:     {len(sales_orders)}")
    print("=== Complete ===")


if __name__ == "__main__":
    main()
