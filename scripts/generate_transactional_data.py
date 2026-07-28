#!/usr/bin/env python3
"""Generate transactional fact CSV files for the Supply Chain Control Tower."""

from __future__ import annotations

import csv
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
from faker import Faker

from config import (
    DEFECT_TYPES,
    MASTER_ROW_COUNTS,
    PO_STATUSES,
    RETURN_REASONS,
    RANDOM_SEED,
    SHIPMENT_STATUSES,
    TRANSACTIONAL_DIR,
    TRANSACTIONAL_ROW_COUNTS,
    WARRANTY_TYPES,
)

fake = Faker()
Faker.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

SUPPLIER_IDS = np.arange(1, MASTER_ROW_COUNTS["supplier"] + 1)
MATERIAL_IDS = np.arange(1, MASTER_ROW_COUNTS["material"] + 1)
PLANT_IDS = np.arange(1, MASTER_ROW_COUNTS["plant"] + 1)
WAREHOUSE_IDS = np.arange(1, MASTER_ROW_COUNTS["warehouse"] + 1)
MACHINE_IDS = np.arange(1, MASTER_ROW_COUNTS["machine"] + 1)
CARRIER_IDS = np.arange(1, MASTER_ROW_COUNTS["carrier"] + 1)
CUSTOMER_IDS = np.arange(1, MASTER_ROW_COUNTS["customer"] + 1)
EMPLOYEE_IDS = np.arange(1, MASTER_ROW_COUNTS["employee"] + 1)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows):,} rows -> {path}")


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=int(np.random.randint(0, delta + 1)))


def generate_purchase_orders() -> list[dict]:
    rows = []
    for po_id in range(1, TRANSACTIONAL_ROW_COUNTS["purchase_orders"] + 1):
        order_date = random_date(date(2023, 1, 1), date(2026, 3, 1))
        expected_delivery = order_date + timedelta(days=int(np.random.randint(2, 31)))
        rows.append(
            {
                "purchase_order_id": po_id,
                "po_number": f"PO-{po_id:08d}",
                "supplier_id": int(np.random.choice(SUPPLIER_IDS)),
                "plant_id": int(np.random.choice(PLANT_IDS)),
                "buyer_employee_id": int(np.random.choice(EMPLOYEE_IDS)),
                "order_date": order_date.isoformat(),
                "expected_delivery_date": expected_delivery.isoformat(),
                "po_status": np.random.choice(PO_STATUSES, p=[0.25, 0.55, 0.05, 0.15]),
                "currency_code": "USD",
                "total_amount_usd": round(float(np.random.uniform(500, 250000)), 2),
                "created_at": order_date.isoformat(),
                "updated_at": (order_date + timedelta(days=int(np.random.randint(0, 30)))).isoformat(),
            }
        )
    return rows


def generate_purchase_order_lines(purchase_orders: list[dict]) -> list[dict]:
    rows = []
    line_id = 1
    po_ids = [row["purchase_order_id"] for row in purchase_orders]
    po_lookup = {row["purchase_order_id"]: row for row in purchase_orders}
    po_line_counts = np.random.choice([1, 2, 3, 4, 5], size=len(po_ids), p=[0.2, 0.3, 0.25, 0.15, 0.1])
    for po_id, line_count in zip(po_ids, po_line_counts):
        po = po_lookup[po_id]
        for line_num in range(1, line_count + 1):
            qty = int(np.random.randint(10, 5000))
            unit_price = round(float(np.random.uniform(5, 500)), 2)
            rows.append(
                {
                    "purchase_order_line_id": line_id,
                    "purchase_order_id": po_id,
                    "line_number": line_num,
                    "material_id": int(np.random.choice(MATERIAL_IDS)),
                    "ordered_quantity": qty,
                    "received_quantity": int(qty * np.random.uniform(0, 1.05)),
                    "unit_price_usd": unit_price,
                    "line_amount_usd": round(qty * unit_price, 2),
                    "requested_delivery_date": po["expected_delivery_date"],
                    "created_at": po["order_date"],
                    "updated_at": po["updated_at"],
                }
            )
            line_id += 1
            if line_id > TRANSACTIONAL_ROW_COUNTS["purchase_order_lines"]:
                return rows
    return rows[: TRANSACTIONAL_ROW_COUNTS["purchase_order_lines"]]


def generate_inventory() -> list[dict]:
    rows = []
    for inv_id in range(1, TRANSACTIONAL_ROW_COUNTS["inventory"] + 1):
        last_movement = random_date(date(2024, 1, 1), date(2026, 3, 1))
        rows.append(
            {
                "inventory_id": inv_id,
                "material_id": int(np.random.choice(MATERIAL_IDS)),
                "warehouse_id": int(np.random.choice(WAREHOUSE_IDS)),
                "on_hand_quantity": int(np.random.randint(1, 10001)),
                "reserved_quantity": int(np.random.randint(0, 500)),
                "available_quantity": 0,
                "reorder_point": int(np.random.randint(50, 1000)),
                "safety_stock": int(np.random.randint(25, 500)),
                "last_movement_date": last_movement.isoformat(),
                "created_at": last_movement.isoformat(),
                "updated_at": last_movement.isoformat(),
            }
        )
    for row in rows:
        row["available_quantity"] = max(row["on_hand_quantity"] - row["reserved_quantity"], 0)
    return rows


def generate_inventory_transactions(inventory_rows: list[dict]) -> list[dict]:
    rows = []
    txn_types = ["Receipt", "Issue", "Transfer", "Adjustment", "Cycle Count"]
    for txn_id in range(1, TRANSACTIONAL_ROW_COUNTS["inventory_transactions"] + 1):
        inv = inventory_rows[np.random.randint(0, len(inventory_rows))]
        txn_date = random_date(date(2024, 1, 1), date(2026, 3, 1))
        rows.append(
            {
                "inventory_transaction_id": txn_id,
                "inventory_id": inv["inventory_id"],
                "material_id": inv["material_id"],
                "warehouse_id": inv["warehouse_id"],
                "transaction_type": np.random.choice(txn_types),
                "transaction_quantity": int(np.random.randint(1, 500)),
                "transaction_date": txn_date.isoformat(),
                "reference_document": f"REF-{txn_id:08d}",
                "created_at": txn_date.isoformat(),
            }
        )
    return rows


def generate_production_orders() -> list[dict]:
    rows = []
    statuses = ["Planned", "Released", "In Progress", "Completed", "Cancelled"]
    for prod_id in range(1, TRANSACTIONAL_ROW_COUNTS["production_orders"] + 1):
        start_date = random_date(date(2023, 6, 1), date(2026, 2, 1))
        planned_qty = int(np.random.randint(50, 5000))
        completed_qty = int(planned_qty * np.random.uniform(0.7, 1.02))
        rows.append(
            {
                "production_order_id": prod_id,
                "production_order_number": f"PRD-{prod_id:08d}",
                "plant_id": int(np.random.choice(PLANT_IDS)),
                "material_id": int(np.random.choice(MATERIAL_IDS)),
                "machine_id": int(np.random.choice(MACHINE_IDS)),
                "planned_start_date": start_date.isoformat(),
                "planned_end_date": (start_date + timedelta(days=int(np.random.randint(1, 14)))).isoformat(),
                "actual_start_date": start_date.isoformat(),
                "actual_end_date": (start_date + timedelta(days=int(np.random.randint(1, 16)))).isoformat(),
                "planned_quantity": planned_qty,
                "completed_quantity": completed_qty,
                "scrap_quantity": max(planned_qty - completed_qty, 0),
                "production_status": np.random.choice(statuses, p=[0.1, 0.15, 0.2, 0.5, 0.05]),
                "created_at": start_date.isoformat(),
                "updated_at": (start_date + timedelta(days=5)).isoformat(),
            }
        )
    return rows


def generate_production_transactions(production_orders: list[dict]) -> list[dict]:
    rows = []
    txn_types = ["Start", "Output", "Scrap", "Rework", "Complete"]
    for txn_id in range(1, TRANSACTIONAL_ROW_COUNTS["production_transactions"] + 1):
        po = production_orders[np.random.randint(0, len(production_orders))]
        txn_date = random_date(
            date.fromisoformat(po["planned_start_date"]),
            date.fromisoformat(po["actual_end_date"]),
        )
        rows.append(
            {
                "production_transaction_id": txn_id,
                "production_order_id": po["production_order_id"],
                "plant_id": po["plant_id"],
                "machine_id": po["machine_id"],
                "material_id": po["material_id"],
                "transaction_type": np.random.choice(txn_types),
                "transaction_quantity": int(np.random.randint(1, 200)),
                "transaction_date": txn_date.isoformat(),
                "created_at": txn_date.isoformat(),
            }
        )
    return rows


def generate_machine_sensor_readings() -> list[dict]:
    rows = []
    for reading_id in range(1, TRANSACTIONAL_ROW_COUNTS["machine_sensor_readings"] + 1):
        reading_time = fake.date_time_between(datetime(2025, 1, 1), datetime(2026, 3, 1))
        utilization = round(float(np.random.uniform(60, 100)), 2)
        rows.append(
            {
                "sensor_reading_id": reading_id,
                "machine_id": int(np.random.choice(MACHINE_IDS)),
                "plant_id": int(np.random.choice(PLANT_IDS)),
                "reading_timestamp": reading_time.strftime("%Y-%m-%d %H:%M:%S"),
                "temperature_celsius": round(float(np.random.uniform(18, 85)), 2),
                "vibration_mm_s": round(float(np.random.uniform(0.1, 5.0)), 3),
                "utilization_pct": utilization,
                "error_code": np.random.choice(["", "E101", "E202", "E305"], p=[0.92, 0.03, 0.03, 0.02]),
                "created_at": reading_time.date().isoformat(),
            }
        )
    return rows


def generate_shipments() -> list[dict]:
    rows = []
    for shipment_id in range(1, TRANSACTIONAL_ROW_COUNTS["shipments"] + 1):
        ship_date = random_date(date(2024, 1, 1), date(2026, 3, 1))
        transit_days = int(np.random.randint(1, 15))
        expected = ship_date + timedelta(days=transit_days)
        delay = int(np.random.randint(0, 16))
        actual = expected + timedelta(days=delay)
        status = np.random.choice(SHIPMENT_STATUSES, p=[0.1, 0.25, 0.45, 0.15, 0.05])
        rows.append(
            {
                "shipment_id": shipment_id,
                "shipment_number": f"SHP-{shipment_id:08d}",
                "carrier_id": int(np.random.choice(CARRIER_IDS)),
                "origin_warehouse_id": int(np.random.choice(WAREHOUSE_IDS)),
                "destination_customer_id": int(np.random.choice(CUSTOMER_IDS)),
                "ship_date": ship_date.isoformat(),
                "expected_delivery_date": expected.isoformat(),
                "actual_delivery_date": actual.isoformat() if status == "Delivered" else "",
                "shipment_status": status,
                "weight_kg": round(float(np.random.uniform(10, 5000)), 2),
                "freight_cost_usd": round(float(np.random.uniform(50, 5000)), 2),
                "delay_days": delay if status in ("Delayed", "Delivered") else 0,
                "created_at": ship_date.isoformat(),
                "updated_at": actual.isoformat(),
            }
        )
    return rows


def generate_shipment_tracking(shipments: list[dict]) -> list[dict]:
    rows = []
    tracking_id = 1
    event_types = ["Created", "Picked Up", "In Transit", "Customs", "Out for Delivery", "Delivered", "Exception"]
    for shipment in shipments:
        event_count = int(np.random.choice([2, 3, 4, 5], p=[0.2, 0.35, 0.3, 0.15]))
        base_date = date.fromisoformat(shipment["ship_date"])
        for event_num in range(event_count):
            if tracking_id > TRANSACTIONAL_ROW_COUNTS["shipment_tracking"]:
                return rows
            event_date = base_date + timedelta(days=event_num)
            rows.append(
                {
                    "shipment_tracking_id": tracking_id,
                    "shipment_id": shipment["shipment_id"],
                    "tracking_event_sequence": event_num + 1,
                    "event_type": event_types[min(event_num, len(event_types) - 1)],
                    "event_location": fake.city(),
                    "event_timestamp": f"{event_date.isoformat()} {np.random.randint(6, 22):02d}:00:00",
                    "event_description": f"Shipment event {event_num + 1}",
                    "created_at": event_date.isoformat(),
                }
            )
            tracking_id += 1
    return rows


def generate_sales_orders() -> list[dict]:
    rows = []
    statuses = ["Open", "Confirmed", "Shipped", "Delivered", "Cancelled"]
    for so_id in range(1, TRANSACTIONAL_ROW_COUNTS["sales_orders"] + 1):
        order_date = random_date(date(2023, 1, 1), date(2026, 3, 1))
        rows.append(
            {
                "sales_order_id": so_id,
                "sales_order_number": f"SO-{so_id:08d}",
                "customer_id": int(np.random.choice(CUSTOMER_IDS)),
                "order_date": order_date.isoformat(),
                "requested_delivery_date": (order_date + timedelta(days=int(np.random.randint(3, 30)))).isoformat(),
                "sales_order_status": np.random.choice(statuses, p=[0.1, 0.2, 0.25, 0.4, 0.05]),
                "total_amount_usd": round(float(np.random.uniform(1000, 500000)), 2),
                "currency_code": "USD",
                "created_at": order_date.isoformat(),
                "updated_at": (order_date + timedelta(days=10)).isoformat(),
            }
        )
    return rows


def generate_sales_order_lines(sales_orders: list[dict]) -> list[dict]:
    rows = []
    line_id = 1
    for so in sales_orders:
        line_count = int(np.random.choice([1, 2, 3, 4], p=[0.3, 0.35, 0.25, 0.1]))
        for line_num in range(1, line_count + 1):
            if line_id > TRANSACTIONAL_ROW_COUNTS["sales_order_lines"]:
                return rows
            qty = int(np.random.randint(1, 500))
            unit_price = round(float(np.random.uniform(10, 5000)), 2)
            rows.append(
                {
                    "sales_order_line_id": line_id,
                    "sales_order_id": so["sales_order_id"],
                    "line_number": line_num,
                    "material_id": int(np.random.choice(MATERIAL_IDS)),
                    "ordered_quantity": qty,
                    "shipped_quantity": int(qty * np.random.uniform(0.8, 1.0)),
                    "unit_price_usd": unit_price,
                    "line_amount_usd": round(qty * unit_price, 2),
                    "created_at": so["order_date"],
                    "updated_at": so["updated_at"],
                }
            )
            line_id += 1
    return rows


def generate_quality_inspections() -> list[dict]:
    rows = []
    for inspection_id in range(1, TRANSACTIONAL_ROW_COUNTS["quality_inspection"] + 1):
        insp_date = random_date(date(2024, 1, 1), date(2026, 3, 1))
        score = round(float(np.random.uniform(80, 100)), 2)
        rows.append(
            {
                "quality_inspection_id": inspection_id,
                "inspection_number": f"QI-{inspection_id:08d}",
                "material_id": int(np.random.choice(MATERIAL_IDS)),
                "plant_id": int(np.random.choice(PLANT_IDS)),
                "production_order_id": int(np.random.randint(1, TRANSACTIONAL_ROW_COUNTS["production_orders"] + 1)),
                "inspector_employee_id": int(np.random.choice(EMPLOYEE_IDS)),
                "inspection_date": insp_date.isoformat(),
                "inspected_quantity": int(np.random.randint(10, 1000)),
                "passed_quantity": 0,
                "failed_quantity": 0,
                "quality_score": score,
                "inspection_result": "Pass" if score >= 80 else "Fail",
                "created_at": insp_date.isoformat(),
                "updated_at": insp_date.isoformat(),
            }
        )
    for row in rows:
        fail_rate = max(0, (100 - row["quality_score"]) / 100)
        row["failed_quantity"] = int(row["inspected_quantity"] * fail_rate)
        row["passed_quantity"] = row["inspected_quantity"] - row["failed_quantity"]
    return rows


def generate_defects() -> list[dict]:
    rows = []
    for defect_id in range(1, TRANSACTIONAL_ROW_COUNTS["defects"] + 1):
        defect_date = random_date(date(2024, 1, 1), date(2026, 3, 1))
        rows.append(
            {
                "defect_id": defect_id,
                "quality_inspection_id": int(np.random.randint(1, TRANSACTIONAL_ROW_COUNTS["quality_inspection"] + 1)),
                "material_id": int(np.random.choice(MATERIAL_IDS)),
                "plant_id": int(np.random.choice(PLANT_IDS)),
                "defect_type": np.random.choice(DEFECT_TYPES),
                "defect_quantity": int(np.random.randint(1, 50)),
                "severity": np.random.choice(["Low", "Medium", "High", "Critical"], p=[0.4, 0.35, 0.2, 0.05]),
                "defect_date": defect_date.isoformat(),
                "root_cause": np.random.choice(["Supplier", "Process", "Equipment", "Operator", "Design"]),
                "created_at": defect_date.isoformat(),
            }
        )
    return rows


def generate_returns() -> list[dict]:
    rows = []
    for return_id in range(1, TRANSACTIONAL_ROW_COUNTS["returns"] + 1):
        return_date = random_date(date(2024, 1, 1), date(2026, 3, 1))
        rows.append(
            {
                "return_id": return_id,
                "return_number": f"RET-{return_id:07d}",
                "sales_order_id": int(np.random.randint(1, TRANSACTIONAL_ROW_COUNTS["sales_orders"] + 1)),
                "customer_id": int(np.random.choice(CUSTOMER_IDS)),
                "material_id": int(np.random.choice(MATERIAL_IDS)),
                "return_quantity": int(np.random.randint(1, 20)),
                "return_reason": np.random.choice(RETURN_REASONS),
                "return_date": return_date.isoformat(),
                "return_amount_usd": round(float(np.random.uniform(50, 10000)), 2),
                "return_status": np.random.choice(["Requested", "Approved", "Received", "Rejected"]),
                "created_at": return_date.isoformat(),
            }
        )
    return rows


def generate_warranty_claims() -> list[dict]:
    rows = []
    for claim_id in range(1, TRANSACTIONAL_ROW_COUNTS["warranty_claims"] + 1):
        claim_date = random_date(date(2024, 1, 1), date(2026, 3, 1))
        rows.append(
            {
                "warranty_claim_id": claim_id,
                "claim_number": f"WC-{claim_id:07d}",
                "customer_id": int(np.random.choice(CUSTOMER_IDS)),
                "material_id": int(np.random.choice(MATERIAL_IDS)),
                "sales_order_id": int(np.random.randint(1, TRANSACTIONAL_ROW_COUNTS["sales_orders"] + 1)),
                "warranty_type": np.random.choice(WARRANTY_TYPES),
                "claim_date": claim_date.isoformat(),
                "claim_amount_usd": round(float(np.random.uniform(100, 25000)), 2),
                "claim_status": np.random.choice(["Submitted", "Under Review", "Approved", "Denied", "Paid"]),
                "mileage_at_claim": int(np.random.randint(1000, 150000)),
                "created_at": claim_date.isoformat(),
            }
        )
    return rows


def generate_supplier_deliveries(purchase_orders: list[dict]) -> list[dict]:
    rows = []
    for delivery_id in range(1, TRANSACTIONAL_ROW_COUNTS["supplier_deliveries"] + 1):
        po = purchase_orders[np.random.randint(0, len(purchase_orders))]
        expected = date.fromisoformat(po["expected_delivery_date"])
        delay = int(np.random.randint(0, 16))
        actual = expected + timedelta(days=delay)
        rows.append(
            {
                "supplier_delivery_id": delivery_id,
                "purchase_order_id": po["purchase_order_id"],
                "supplier_id": po["supplier_id"],
                "plant_id": po["plant_id"],
                "delivery_number": f"DLV-{delivery_id:08d}",
                "scheduled_delivery_date": expected.isoformat(),
                "actual_delivery_date": actual.isoformat(),
                "delivery_delay_days": delay,
                "delivered_quantity": int(np.random.randint(10, 5000)),
                "is_on_time": "Y" if delay <= 0 else "N",
                "created_at": actual.isoformat(),
                "updated_at": actual.isoformat(),
            }
        )
    return rows


def main() -> None:
    print("Generating transactional data...")
    purchase_orders = generate_purchase_orders()
    write_csv(
        TRANSACTIONAL_DIR / "purchase_orders.csv",
        list(purchase_orders[0].keys()),
        purchase_orders,
    )

    po_lines = generate_purchase_order_lines(purchase_orders)
    write_csv(TRANSACTIONAL_DIR / "purchase_order_lines.csv", list(po_lines[0].keys()), po_lines)

    inventory = generate_inventory()
    write_csv(TRANSACTIONAL_DIR / "inventory.csv", list(inventory[0].keys()), inventory)

    inv_txn = generate_inventory_transactions(inventory)
    write_csv(TRANSACTIONAL_DIR / "inventory_transactions.csv", list(inv_txn[0].keys()), inv_txn)

    production_orders = generate_production_orders()
    write_csv(TRANSACTIONAL_DIR / "production_orders.csv", list(production_orders[0].keys()), production_orders)

    prod_txn = generate_production_transactions(production_orders)
    write_csv(TRANSACTIONAL_DIR / "production_transactions.csv", list(prod_txn[0].keys()), prod_txn)

    sensor = generate_machine_sensor_readings()
    write_csv(TRANSACTIONAL_DIR / "machine_sensor_readings.csv", list(sensor[0].keys()), sensor)

    shipments = generate_shipments()
    write_csv(TRANSACTIONAL_DIR / "shipments.csv", list(shipments[0].keys()), shipments)

    tracking = generate_shipment_tracking(shipments)
    write_csv(TRANSACTIONAL_DIR / "shipment_tracking.csv", list(tracking[0].keys()), tracking)

    sales_orders = generate_sales_orders()
    write_csv(TRANSACTIONAL_DIR / "sales_orders.csv", list(sales_orders[0].keys()), sales_orders)

    so_lines = generate_sales_order_lines(sales_orders)
    write_csv(TRANSACTIONAL_DIR / "sales_order_lines.csv", list(so_lines[0].keys()), so_lines)

    quality = generate_quality_inspections()
    write_csv(TRANSACTIONAL_DIR / "quality_inspection.csv", list(quality[0].keys()), quality)

    defects = generate_defects()
    write_csv(TRANSACTIONAL_DIR / "defects.csv", list(defects[0].keys()), defects)

    returns = generate_returns()
    write_csv(TRANSACTIONAL_DIR / "returns.csv", list(returns[0].keys()), returns)

    warranty = generate_warranty_claims()
    write_csv(TRANSACTIONAL_DIR / "warranty_claims.csv", list(warranty[0].keys()), warranty)

    deliveries = generate_supplier_deliveries(purchase_orders)
    write_csv(TRANSACTIONAL_DIR / "supplier_deliveries.csv", list(deliveries[0].keys()), deliveries)

    print("Transactional data generation complete.")


if __name__ == "__main__":
    main()
