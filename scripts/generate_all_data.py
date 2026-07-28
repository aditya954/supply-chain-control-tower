#!/usr/bin/env python3
"""Generate all master and transactional CSV files using Python stdlib only."""

from __future__ import annotations

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

from config import (
    CARRIER_MODES,
    DEFECT_TYPES,
    MASTER_DIR,
    MASTER_ROW_COUNTS,
    MATERIAL_CATEGORIES,
    MATERIAL_TYPES,
    PLANT_REGIONS,
    PO_STATUSES,
    RANDOM_SEED,
    RETURN_REASONS,
    SHIPMENT_STATUSES,
    TRANSACTIONAL_DIR,
    TRANSACTIONAL_ROW_COUNTS,
    WARRANTY_TYPES,
)

random.seed(RANDOM_SEED)

COMPANIES = [
    "Apex Automotive", "Vertex Manufacturing", "Summit Parts", "Horizon Logistics",
    "Pinnacle Supply", "Atlas Components", "Nova Industries", "Zenith Motors",
]
FIRST = ["James", "Maria", "Chen", "Priya", "Omar", "Elena", "Raj", "Sophie"]
LAST = ["Patel", "Garcia", "Kim", "Johnson", "Mueller", "Singh", "Brown", "Lee"]
CITIES = ["Detroit", "Stuttgart", "Nagoya", "Chennai", "Monterrey", "Shanghai", "Toronto"]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows):,} rows -> {path}")


def rand_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))


def choice_weighted(options: list, weights: list):
    return random.choices(options, weights=weights, k=1)[0]


def gen_master() -> None:
    suppliers, materials, plants, warehouses, machines, carriers, customers, employees = [], [], [], [], [], [], [], []

    for i in range(1, MASTER_ROW_COUNTS["supplier"] + 1):
        suppliers.append({
            "supplier_id": i, "supplier_code": f"SUP-{i:06d}",
            "supplier_name": f"{random.choice(COMPANIES)} {i}",
            "supplier_tier": choice_weighted(["Tier 1", "Tier 2", "Tier 3"], [0.4, 0.4, 0.2]),
            "country_code": choice_weighted(["US", "DE", "JP", "IN", "MX", "CN"], [0.3, 0.2, 0.15, 0.15, 0.1, 0.1]),
            "city": random.choice(CITIES), "contact_email": f"contact{i}@supplier.com",
            "contact_phone": f"+1-555-{random.randint(100,999):03d}-{random.randint(1000,9999):04d}",
            "payment_terms": random.choice(["NET30", "NET45", "NET60", "NET90"]),
            "lead_time_days": random.randint(2, 30), "is_active": choice_weighted(["Y", "N"], [0.92, 0.08]),
            "created_at": rand_date(date(2018, 1, 1), date(2024, 12, 31)).isoformat(),
            "updated_at": rand_date(date(2024, 1, 1), date(2026, 3, 1)).isoformat(),
        })

    for i in range(1, MASTER_ROW_COUNTS["material"] + 1):
        materials.append({
            "material_id": i, "material_code": f"MAT-{i:06d}",
            "material_name": f"{random.choice(MATERIAL_CATEGORIES)} Component {i}",
            "material_type": random.choice(MATERIAL_TYPES),
            "material_category": random.choice(MATERIAL_CATEGORIES),
            "unit_of_measure": random.choice(["EA", "KG", "L", "M"]),
            "unit_cost_usd": round(random.uniform(1.5, 2500.0), 2),
            "shelf_life_days": random.choice([0, 90, 180, 365, 730]),
            "is_hazardous": choice_weighted(["Y", "N"], [0.05, 0.95]),
            "is_active": choice_weighted(["Y", "N"], [0.94, 0.06]),
            "created_at": rand_date(date(2018, 1, 1), date(2024, 12, 31)).isoformat(),
            "updated_at": rand_date(date(2024, 1, 1), date(2026, 3, 1)).isoformat(),
        })

    for i in range(1, MASTER_ROW_COUNTS["plant"] + 1):
        region = random.choice(PLANT_REGIONS)
        plants.append({
            "plant_id": i, "plant_code": f"PLT-{i:04d}",
            "plant_name": f"{region} Plant {i}", "region": region,
            "country_code": random.choice(["US", "DE", "JP", "IN", "MX"]),
            "city": random.choice(CITIES), "capacity_units_per_day": random.randint(500, 5000),
            "is_active": "Y" if i <= 48 else choice_weighted(["Y", "N"], [0.9, 0.1]),
            "created_at": rand_date(date(2015, 1, 1), date(2023, 12, 31)).isoformat(),
            "updated_at": rand_date(date(2024, 1, 1), date(2026, 3, 1)).isoformat(),
        })

    plant_ids = list(range(1, MASTER_ROW_COUNTS["plant"] + 1))
    for i in range(1, MASTER_ROW_COUNTS["warehouse"] + 1):
        warehouses.append({
            "warehouse_id": i, "warehouse_code": f"WH-{i:05d}",
            "warehouse_name": f"Warehouse {i}", "plant_id": random.choice(plant_ids),
            "warehouse_type": random.choice(["Raw", "WIP", "Finished Goods", "Spare Parts"]),
            "capacity_pallets": random.randint(1000, 20000),
            "is_active": choice_weighted(["Y", "N"], [0.95, 0.05]),
            "created_at": rand_date(date(2016, 1, 1), date(2024, 6, 30)).isoformat(),
            "updated_at": rand_date(date(2024, 1, 1), date(2026, 3, 1)).isoformat(),
        })

    for i in range(1, MASTER_ROW_COUNTS["machine"] + 1):
        machines.append({
            "machine_id": i, "machine_code": f"MC-{i:06d}",
            "machine_name": f"CNC Line {i % 120 + 1}", "plant_id": random.choice(plant_ids),
            "machine_type": random.choice(["CNC", "Press", "Welding", "Assembly", "Paint"]),
            "rated_capacity_per_hour": random.randint(20, 500),
            "commissioned_date": rand_date(date(2012, 1, 1), date(2024, 12, 31)).isoformat(),
            "is_active": choice_weighted(["Y", "N"], [0.9, 0.1]),
            "created_at": rand_date(date(2018, 1, 1), date(2024, 12, 31)).isoformat(),
            "updated_at": rand_date(date(2024, 1, 1), date(2026, 3, 1)).isoformat(),
        })

    for i in range(1, MASTER_ROW_COUNTS["carrier"] + 1):
        carriers.append({
            "carrier_id": i, "carrier_code": f"CAR-{i:04d}",
            "carrier_name": f"{random.choice(COMPANIES)} Logistics",
            "transport_mode": random.choice(CARRIER_MODES),
            "service_level": random.choice(["Standard", "Express", "Economy"]),
            "country_code": random.choice(["US", "DE", "JP", "IN"]),
            "is_active": choice_weighted(["Y", "N"], [0.93, 0.07]),
            "created_at": rand_date(date(2017, 1, 1), date(2024, 12, 31)).isoformat(),
            "updated_at": rand_date(date(2024, 1, 1), date(2026, 3, 1)).isoformat(),
        })

    for i in range(1, MASTER_ROW_COUNTS["customer"] + 1):
        customers.append({
            "customer_id": i, "customer_code": f"CUS-{i:06d}",
            "customer_name": f"{random.choice(COMPANIES)} Dealer {i}",
            "customer_segment": choice_weighted(["OEM", "Dealer", "Fleet", "Aftermarket"], [0.35, 0.35, 0.15, 0.15]),
            "country_code": random.choice(["US", "DE", "JP", "IN", "MX", "CN"]),
            "city": random.choice(CITIES), "credit_limit_usd": random.randint(50000, 5000000),
            "is_active": choice_weighted(["Y", "N"], [0.91, 0.09]),
            "created_at": rand_date(date(2016, 1, 1), date(2024, 12, 31)).isoformat(),
            "updated_at": rand_date(date(2024, 1, 1), date(2026, 3, 1)).isoformat(),
        })

    for i in range(1, MASTER_ROW_COUNTS["employee"] + 1):
        employees.append({
            "employee_id": i, "employee_code": f"EMP-{i:06d}",
            "first_name": random.choice(FIRST), "last_name": random.choice(LAST),
            "email": f"{random.choice(FIRST).lower()}.{random.choice(LAST).lower()}{i}@company.com",
            "department": random.choice(["Procurement", "Production", "Quality", "Logistics", "Planning", "Maintenance"]),
            "plant_id": random.choice(plant_ids),
            "hire_date": rand_date(date(2010, 1, 1), date(2025, 6, 30)).isoformat(),
            "is_active": choice_weighted(["Y", "N"], [0.88, 0.12]),
            "created_at": rand_date(date(2018, 1, 1), date(2024, 12, 31)).isoformat(),
            "updated_at": rand_date(date(2024, 1, 1), date(2026, 3, 1)).isoformat(),
        })

    calendar = []
    d = date(2020, 1, 1)
    while d <= date(2030, 12, 31):
        fy = d.year if d.month >= 4 else d.year - 1
        calendar.append({
            "date_key": int(d.strftime("%Y%m%d")), "calendar_date": d.isoformat(),
            "year": d.year, "quarter": (d.month - 1) // 3 + 1, "month": d.month,
            "month_name": d.strftime("%B"), "day_of_month": d.day,
            "day_of_week": d.isoweekday(), "day_name": d.strftime("%A"),
            "week_of_year": d.isocalendar()[1], "is_weekend": "Y" if d.weekday() >= 5 else "N",
            "is_holiday": "N", "fiscal_year": fy, "fiscal_quarter": ((d.month - 4) % 12) // 3 + 1,
        })
        d += timedelta(days=1)

    write_csv(MASTER_DIR / "supplier.csv", list(suppliers[0].keys()), suppliers)
    write_csv(MASTER_DIR / "material.csv", list(materials[0].keys()), materials)
    write_csv(MASTER_DIR / "plant.csv", list(plants[0].keys()), plants)
    write_csv(MASTER_DIR / "warehouse.csv", list(warehouses[0].keys()), warehouses)
    write_csv(MASTER_DIR / "machine.csv", list(machines[0].keys()), machines)
    write_csv(MASTER_DIR / "carrier.csv", list(carriers[0].keys()), carriers)
    write_csv(MASTER_DIR / "customer.csv", list(customers[0].keys()), customers)
    write_csv(MASTER_DIR / "employee.csv", list(employees[0].keys()), employees)
    write_csv(MASTER_DIR / "calendar.csv", list(calendar[0].keys()), calendar)
    return suppliers, materials, plants, warehouses, machines, carriers, customers, employees


def gen_transactional(suppliers, materials, plants, warehouses, machines, carriers, customers, employees) -> None:
    supplier_ids = [s["supplier_id"] for s in suppliers]
    material_ids = [m["material_id"] for m in materials]
    plant_ids = [p["plant_id"] for p in plants]
    warehouse_ids = [w["warehouse_id"] for w in warehouses]
    machine_ids = [m["machine_id"] for m in machines]
    carrier_ids = [c["carrier_id"] for c in carriers]
    customer_ids = [c["customer_id"] for c in customers]
    employee_ids = [e["employee_id"] for e in employees]

    pos = []
    for i in range(1, TRANSACTIONAL_ROW_COUNTS["purchase_orders"] + 1):
        od = rand_date(date(2023, 1, 1), date(2026, 3, 1))
        ed = od + timedelta(days=random.randint(2, 30))
        pos.append({
            "purchase_order_id": i, "po_number": f"PO-{i:08d}",
            "supplier_id": random.choice(supplier_ids), "plant_id": random.choice(plant_ids),
            "buyer_employee_id": random.choice(employee_ids), "order_date": od.isoformat(),
            "expected_delivery_date": ed.isoformat(),
            "po_status": choice_weighted(PO_STATUSES, [0.25, 0.55, 0.05, 0.15]),
            "currency_code": "USD", "total_amount_usd": round(random.uniform(500, 250000), 2),
            "created_at": od.isoformat(), "updated_at": (od + timedelta(days=random.randint(0, 30))).isoformat(),
        })
    write_csv(TRANSACTIONAL_DIR / "purchase_orders.csv", list(pos[0].keys()), pos)

    po_lines, lid = [], 1
    po_lookup = {p["purchase_order_id"]: p for p in pos}
    for po in pos:
        for ln in range(1, random.choices([1, 2, 3, 4, 5], weights=[0.2, 0.3, 0.25, 0.15, 0.1])[0] + 1):
            if lid > TRANSACTIONAL_ROW_COUNTS["purchase_order_lines"]:
                break
            qty = random.randint(10, 5000)
            up = round(random.uniform(5, 500), 2)
            po_lines.append({
                "purchase_order_line_id": lid, "purchase_order_id": po["purchase_order_id"],
                "line_number": ln, "material_id": random.choice(material_ids),
                "ordered_quantity": qty, "received_quantity": int(qty * random.uniform(0, 1.05)),
                "unit_price_usd": up, "line_amount_usd": round(qty * up, 2),
                "requested_delivery_date": po["expected_delivery_date"],
                "created_at": po["order_date"], "updated_at": po["updated_at"],
            })
            lid += 1
    write_csv(TRANSACTIONAL_DIR / "purchase_order_lines.csv", list(po_lines[0].keys()), po_lines[:TRANSACTIONAL_ROW_COUNTS["purchase_order_lines"]])

    inv = []
    for i in range(1, TRANSACTIONAL_ROW_COUNTS["inventory"] + 1):
        oh = random.randint(1, 10000)
        res = random.randint(0, min(500, oh))
        lm = rand_date(date(2024, 1, 1), date(2026, 3, 1))
        inv.append({
            "inventory_id": i, "material_id": random.choice(material_ids),
            "warehouse_id": random.choice(warehouse_ids), "on_hand_quantity": oh,
            "reserved_quantity": res, "available_quantity": oh - res,
            "reorder_point": random.randint(50, 1000), "safety_stock": random.randint(25, 500),
            "last_movement_date": lm.isoformat(), "created_at": lm.isoformat(), "updated_at": lm.isoformat(),
        })
    write_csv(TRANSACTIONAL_DIR / "inventory.csv", list(inv[0].keys()), inv)

    inv_txn = []
    for i in range(1, TRANSACTIONAL_ROW_COUNTS["inventory_transactions"] + 1):
        row = inv[random.randint(0, len(inv) - 1)]
        td = rand_date(date(2024, 1, 1), date(2026, 3, 1))
        inv_txn.append({
            "inventory_transaction_id": i, "inventory_id": row["inventory_id"],
            "material_id": row["material_id"], "warehouse_id": row["warehouse_id"],
            "transaction_type": random.choice(["Receipt", "Issue", "Transfer", "Adjustment", "Cycle Count"]),
            "transaction_quantity": random.randint(1, 500), "transaction_date": td.isoformat(),
            "reference_document": f"REF-{i:08d}", "created_at": td.isoformat(),
        })
    write_csv(TRANSACTIONAL_DIR / "inventory_transactions.csv", list(inv_txn[0].keys()), inv_txn)

    prod = []
    for i in range(1, TRANSACTIONAL_ROW_COUNTS["production_orders"] + 1):
        sd = rand_date(date(2023, 6, 1), date(2026, 2, 1))
        pq = random.randint(50, 5000)
        cq = int(pq * random.uniform(0.7, 1.02))
        prod.append({
            "production_order_id": i, "production_order_number": f"PRD-{i:08d}",
            "plant_id": random.choice(plant_ids), "material_id": random.choice(material_ids),
            "machine_id": random.choice(machine_ids), "planned_start_date": sd.isoformat(),
            "planned_end_date": (sd + timedelta(days=random.randint(1, 14))).isoformat(),
            "actual_start_date": sd.isoformat(),
            "actual_end_date": (sd + timedelta(days=random.randint(1, 16))).isoformat(),
            "planned_quantity": pq, "completed_quantity": cq, "scrap_quantity": max(pq - cq, 0),
            "production_status": choice_weighted(["Planned", "Released", "In Progress", "Completed", "Cancelled"], [0.1, 0.15, 0.2, 0.5, 0.05]),
            "created_at": sd.isoformat(), "updated_at": (sd + timedelta(days=5)).isoformat(),
        })
    write_csv(TRANSACTIONAL_DIR / "production_orders.csv", list(prod[0].keys()), prod)

    pt = []
    for i in range(1, TRANSACTIONAL_ROW_COUNTS["production_transactions"] + 1):
        po = prod[random.randint(0, len(prod) - 1)]
        td = rand_date(date.fromisoformat(po["planned_start_date"]), date.fromisoformat(po["actual_end_date"]))
        pt.append({
            "production_transaction_id": i, "production_order_id": po["production_order_id"],
            "plant_id": po["plant_id"], "machine_id": po["machine_id"], "material_id": po["material_id"],
            "transaction_type": random.choice(["Start", "Output", "Scrap", "Rework", "Complete"]),
            "transaction_quantity": random.randint(1, 200), "transaction_date": td.isoformat(), "created_at": td.isoformat(),
        })
    write_csv(TRANSACTIONAL_DIR / "production_transactions.csv", list(pt[0].keys()), pt)

    sensor = []
    for i in range(1, TRANSACTIONAL_ROW_COUNTS["machine_sensor_readings"] + 1):
        ts = datetime(2025, 1, 1) + timedelta(seconds=random.randint(0, 400 * 86400))
        util = round(random.uniform(60, 100), 2)
        sensor.append({
            "sensor_reading_id": i, "machine_id": random.choice(machine_ids), "plant_id": random.choice(plant_ids),
            "reading_timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature_celsius": round(random.uniform(18, 85), 2),
            "vibration_mm_s": round(random.uniform(0.1, 5.0), 3), "utilization_pct": util,
            "error_code": choice_weighted(["", "E101", "E202", "E305"], [0.92, 0.03, 0.03, 0.02]),
            "created_at": ts.date().isoformat(),
        })
    write_csv(TRANSACTIONAL_DIR / "machine_sensor_readings.csv", list(sensor[0].keys()), sensor)

    ships = []
    for i in range(1, TRANSACTIONAL_ROW_COUNTS["shipments"] + 1):
        sd = rand_date(date(2024, 1, 1), date(2026, 3, 1))
        delay = random.randint(0, 15)
        exp = sd + timedelta(days=random.randint(1, 15))
        act = exp + timedelta(days=delay)
        st = choice_weighted(SHIPMENT_STATUSES, [0.1, 0.25, 0.45, 0.15, 0.05])
        ships.append({
            "shipment_id": i, "shipment_number": f"SHP-{i:08d}", "carrier_id": random.choice(carrier_ids),
            "origin_warehouse_id": random.choice(warehouse_ids), "destination_customer_id": random.choice(customer_ids),
            "ship_date": sd.isoformat(), "expected_delivery_date": exp.isoformat(),
            "actual_delivery_date": act.isoformat() if st == "Delivered" else "",
            "shipment_status": st, "weight_kg": round(random.uniform(10, 5000), 2),
            "freight_cost_usd": round(random.uniform(50, 5000), 2),
            "delay_days": delay if st in ("Delayed", "Delivered") else 0,
            "created_at": sd.isoformat(), "updated_at": act.isoformat(),
        })
    write_csv(TRANSACTIONAL_DIR / "shipments.csv", list(ships[0].keys()), ships)

    track, tid = [], 1
    events = ["Created", "Picked Up", "In Transit", "Customs", "Out for Delivery", "Delivered", "Exception"]
    for sh in ships:
        for n in range(random.choices([2, 3, 4, 5], weights=[0.2, 0.35, 0.3, 0.15])[0]):
            if tid > TRANSACTIONAL_ROW_COUNTS["shipment_tracking"]:
                break
            ed = date.fromisoformat(sh["ship_date"]) + timedelta(days=n)
            track.append({
                "shipment_tracking_id": tid, "shipment_id": sh["shipment_id"],
                "tracking_event_sequence": n + 1, "event_type": events[min(n, len(events) - 1)],
                "event_location": random.choice(CITIES),
                "event_timestamp": f"{ed.isoformat()} {random.randint(6, 22):02d}:00:00",
                "event_description": f"Shipment event {n + 1}", "created_at": ed.isoformat(),
            })
            tid += 1
    write_csv(TRANSACTIONAL_DIR / "shipment_tracking.csv", list(track[0].keys()), track)

    so = []
    for i in range(1, TRANSACTIONAL_ROW_COUNTS["sales_orders"] + 1):
        od = rand_date(date(2023, 1, 1), date(2026, 3, 1))
        so.append({
            "sales_order_id": i, "sales_order_number": f"SO-{i:08d}",
            "customer_id": random.choice(customer_ids), "order_date": od.isoformat(),
            "requested_delivery_date": (od + timedelta(days=random.randint(3, 30))).isoformat(),
            "sales_order_status": choice_weighted(["Open", "Confirmed", "Shipped", "Delivered", "Cancelled"], [0.1, 0.2, 0.25, 0.4, 0.05]),
            "total_amount_usd": round(random.uniform(1000, 500000), 2), "currency_code": "USD",
            "created_at": od.isoformat(), "updated_at": (od + timedelta(days=10)).isoformat(),
        })
    write_csv(TRANSACTIONAL_DIR / "sales_orders.csv", list(so[0].keys()), so)

    sol, slid = [], 1
    for s in so:
        for ln in range(1, random.choices([1, 2, 3, 4], weights=[0.3, 0.35, 0.25, 0.1])[0] + 1):
            if slid > TRANSACTIONAL_ROW_COUNTS["sales_order_lines"]:
                break
            qty = random.randint(1, 500)
            up = round(random.uniform(10, 5000), 2)
            sol.append({
                "sales_order_line_id": slid, "sales_order_id": s["sales_order_id"],
                "line_number": ln, "material_id": random.choice(material_ids),
                "ordered_quantity": qty, "shipped_quantity": int(qty * random.uniform(0.8, 1.0)),
                "unit_price_usd": up, "line_amount_usd": round(qty * up, 2),
                "created_at": s["order_date"], "updated_at": s["updated_at"],
            })
            slid += 1
    write_csv(TRANSACTIONAL_DIR / "sales_order_lines.csv", list(sol[0].keys()), sol[:TRANSACTIONAL_ROW_COUNTS["sales_order_lines"]])

    qi = []
    for i in range(1, TRANSACTIONAL_ROW_COUNTS["quality_inspection"] + 1):
        idate = rand_date(date(2024, 1, 1), date(2026, 3, 1))
        score = round(random.uniform(80, 100), 2)
        iq = random.randint(10, 1000)
        fq = int(iq * max(0, (100 - score) / 100))
        qi.append({
            "quality_inspection_id": i, "inspection_number": f"QI-{i:08d}",
            "material_id": random.choice(material_ids), "plant_id": random.choice(plant_ids),
            "production_order_id": random.randint(1, TRANSACTIONAL_ROW_COUNTS["production_orders"]),
            "inspector_employee_id": random.choice(employee_ids), "inspection_date": idate.isoformat(),
            "inspected_quantity": iq, "passed_quantity": iq - fq, "failed_quantity": fq,
            "quality_score": score, "inspection_result": "Pass" if score >= 80 else "Fail",
            "created_at": idate.isoformat(), "updated_at": idate.isoformat(),
        })
    write_csv(TRANSACTIONAL_DIR / "quality_inspection.csv", list(qi[0].keys()), qi)

    defects = []
    for i in range(1, TRANSACTIONAL_ROW_COUNTS["defects"] + 1):
        dd = rand_date(date(2024, 1, 1), date(2026, 3, 1))
        defects.append({
            "defect_id": i, "quality_inspection_id": random.randint(1, TRANSACTIONAL_ROW_COUNTS["quality_inspection"]),
            "material_id": random.choice(material_ids), "plant_id": random.choice(plant_ids),
            "defect_type": random.choice(DEFECT_TYPES), "defect_quantity": random.randint(1, 50),
            "severity": choice_weighted(["Low", "Medium", "High", "Critical"], [0.4, 0.35, 0.2, 0.05]),
            "defect_date": dd.isoformat(),
            "root_cause": random.choice(["Supplier", "Process", "Equipment", "Operator", "Design"]),
            "created_at": dd.isoformat(),
        })
    write_csv(TRANSACTIONAL_DIR / "defects.csv", list(defects[0].keys()), defects)

    returns = []
    for i in range(1, TRANSACTIONAL_ROW_COUNTS["returns"] + 1):
        rd = rand_date(date(2024, 1, 1), date(2026, 3, 1))
        returns.append({
            "return_id": i, "return_number": f"RET-{i:07d}",
            "sales_order_id": random.randint(1, TRANSACTIONAL_ROW_COUNTS["sales_orders"]),
            "customer_id": random.choice(customer_ids), "material_id": random.choice(material_ids),
            "return_quantity": random.randint(1, 20), "return_reason": random.choice(RETURN_REASONS),
            "return_date": rd.isoformat(), "return_amount_usd": round(random.uniform(50, 10000), 2),
            "return_status": random.choice(["Requested", "Approved", "Received", "Rejected"]),
            "created_at": rd.isoformat(),
        })
    write_csv(TRANSACTIONAL_DIR / "returns.csv", list(returns[0].keys()), returns)

    wc = []
    for i in range(1, TRANSACTIONAL_ROW_COUNTS["warranty_claims"] + 1):
        cd = rand_date(date(2024, 1, 1), date(2026, 3, 1))
        wc.append({
            "warranty_claim_id": i, "claim_number": f"WC-{i:07d}",
            "customer_id": random.choice(customer_ids), "material_id": random.choice(material_ids),
            "sales_order_id": random.randint(1, TRANSACTIONAL_ROW_COUNTS["sales_orders"]),
            "warranty_type": random.choice(WARRANTY_TYPES), "claim_date": cd.isoformat(),
            "claim_amount_usd": round(random.uniform(100, 25000), 2),
            "claim_status": random.choice(["Submitted", "Under Review", "Approved", "Denied", "Paid"]),
            "mileage_at_claim": random.randint(1000, 150000), "created_at": cd.isoformat(),
        })
    write_csv(TRANSACTIONAL_DIR / "warranty_claims.csv", list(wc[0].keys()), wc)

    deliveries = []
    for i in range(1, TRANSACTIONAL_ROW_COUNTS["supplier_deliveries"] + 1):
        po = pos[random.randint(0, len(pos) - 1)]
        exp = date.fromisoformat(po["expected_delivery_date"])
        delay = random.randint(0, 15)
        act = exp + timedelta(days=delay)
        deliveries.append({
            "supplier_delivery_id": i, "purchase_order_id": po["purchase_order_id"],
            "supplier_id": po["supplier_id"], "plant_id": po["plant_id"],
            "delivery_number": f"DLV-{i:08d}", "scheduled_delivery_date": exp.isoformat(),
            "actual_delivery_date": act.isoformat(), "delivery_delay_days": delay,
            "delivered_quantity": random.randint(10, 5000),
            "is_on_time": "Y" if delay <= 0 else "N",
            "created_at": act.isoformat(), "updated_at": act.isoformat(),
        })
    write_csv(TRANSACTIONAL_DIR / "supplier_deliveries.csv", list(deliveries[0].keys()), deliveries)


if __name__ == "__main__":
    print("=== Generating Supply Chain Control Tower Data ===")
    masters = gen_master()
    gen_transactional(*masters)
    print("=== Complete ===")
