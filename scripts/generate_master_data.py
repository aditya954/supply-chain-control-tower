#!/usr/bin/env python3
"""Generate master dimension CSV files for the Supply Chain Control Tower."""

from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

import numpy as np
from faker import Faker

from config import MASTER_DIR, MASTER_ROW_COUNTS, RANDOM_SEED
from config import (
    CARRIER_MODES,
    MATERIAL_CATEGORIES,
    MATERIAL_TYPES,
    PLANT_REGIONS,
)

fake = Faker()
Faker.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows):,} rows -> {path}")


def generate_suppliers() -> None:
    rows = []
    for supplier_id in range(1, MASTER_ROW_COUNTS["supplier"] + 1):
        country = fake.country_code()
        rows.append(
            {
                "supplier_id": supplier_id,
                "supplier_code": f"SUP-{supplier_id:06d}",
                "supplier_name": fake.company(),
                "supplier_tier": np.random.choice(["Tier 1", "Tier 2", "Tier 3"], p=[0.4, 0.4, 0.2]),
                "country_code": country,
                "city": fake.city(),
                "contact_email": fake.company_email(),
                "contact_phone": fake.phone_number()[:20],
                "payment_terms": np.random.choice(["NET30", "NET45", "NET60", "NET90"]),
                "lead_time_days": int(np.random.randint(2, 31)),
                "is_active": np.random.choice(["Y", "N"], p=[0.92, 0.08]),
                "created_at": fake.date_between(date(2018, 1, 1), date(2024, 12, 31)).isoformat(),
                "updated_at": fake.date_between(date(2024, 1, 1), date(2026, 3, 1)).isoformat(),
            }
        )
    write_csv(
        MASTER_DIR / "supplier.csv",
        [
            "supplier_id", "supplier_code", "supplier_name", "supplier_tier",
            "country_code", "city", "contact_email", "contact_phone",
            "payment_terms", "lead_time_days", "is_active", "created_at", "updated_at",
        ],
        rows,
    )


def generate_materials() -> None:
    rows = []
    for material_id in range(1, MASTER_ROW_COUNTS["material"] + 1):
        unit_cost = round(float(np.random.uniform(1.5, 2500.0)), 2)
        rows.append(
            {
                "material_id": material_id,
                "material_code": f"MAT-{material_id:06d}",
                "material_name": f"{np.random.choice(MATERIAL_CATEGORIES)} Component {material_id}",
                "material_type": np.random.choice(MATERIAL_TYPES),
                "material_category": np.random.choice(MATERIAL_CATEGORIES),
                "unit_of_measure": np.random.choice(["EA", "KG", "L", "M"]),
                "unit_cost_usd": unit_cost,
                "shelf_life_days": int(np.random.choice([0, 90, 180, 365, 730])),
                "is_hazardous": np.random.choice(["Y", "N"], p=[0.05, 0.95]),
                "is_active": np.random.choice(["Y", "N"], p=[0.94, 0.06]),
                "created_at": fake.date_between(date(2018, 1, 1), date(2024, 12, 31)).isoformat(),
                "updated_at": fake.date_between(date(2024, 1, 1), date(2026, 3, 1)).isoformat(),
            }
        )
    write_csv(
        MASTER_DIR / "material.csv",
        [
            "material_id", "material_code", "material_name", "material_type",
            "material_category", "unit_of_measure", "unit_cost_usd", "shelf_life_days",
            "is_hazardous", "is_active", "created_at", "updated_at",
        ],
        rows,
    )


def generate_plants() -> None:
    rows = []
    for plant_id in range(1, MASTER_ROW_COUNTS["plant"] + 1):
        region = np.random.choice(PLANT_REGIONS)
        rows.append(
            {
                "plant_id": plant_id,
                "plant_code": f"PLT-{plant_id:04d}",
                "plant_name": f"{region} Manufacturing Plant {plant_id}",
                "region": region,
                "country_code": fake.country_code(),
                "city": fake.city(),
                "capacity_units_per_day": int(np.random.randint(500, 5000)),
                "is_active": "Y" if plant_id <= 48 else np.random.choice(["Y", "N"]),
                "created_at": fake.date_between(date(2015, 1, 1), date(2023, 12, 31)).isoformat(),
                "updated_at": fake.date_between(date(2024, 1, 1), date(2026, 3, 1)).isoformat(),
            }
        )
    write_csv(
        MASTER_DIR / "plant.csv",
        [
            "plant_id", "plant_code", "plant_name", "region", "country_code",
            "city", "capacity_units_per_day", "is_active", "created_at", "updated_at",
        ],
        rows,
    )


def generate_warehouses() -> None:
    rows = []
    plant_ids = list(range(1, MASTER_ROW_COUNTS["plant"] + 1))
    for warehouse_id in range(1, MASTER_ROW_COUNTS["warehouse"] + 1):
        rows.append(
            {
                "warehouse_id": warehouse_id,
                "warehouse_code": f"WH-{warehouse_id:05d}",
                "warehouse_name": f"Warehouse {warehouse_id}",
                "plant_id": int(np.random.choice(plant_ids)),
                "warehouse_type": np.random.choice(["Raw", "WIP", "Finished Goods", "Spare Parts"]),
                "capacity_pallets": int(np.random.randint(1000, 20000)),
                "is_active": np.random.choice(["Y", "N"], p=[0.95, 0.05]),
                "created_at": fake.date_between(date(2016, 1, 1), date(2024, 6, 30)).isoformat(),
                "updated_at": fake.date_between(date(2024, 1, 1), date(2026, 3, 1)).isoformat(),
            }
        )
    write_csv(
        MASTER_DIR / "warehouse.csv",
        [
            "warehouse_id", "warehouse_code", "warehouse_name", "plant_id",
            "warehouse_type", "capacity_pallets", "is_active", "created_at", "updated_at",
        ],
        rows,
    )


def generate_machines() -> None:
    rows = []
    plant_ids = list(range(1, MASTER_ROW_COUNTS["plant"] + 1))
    for machine_id in range(1, MASTER_ROW_COUNTS["machine"] + 1):
        rows.append(
            {
                "machine_id": machine_id,
                "machine_code": f"MC-{machine_id:06d}",
                "machine_name": f"CNC Line {machine_id % 120 + 1}",
                "plant_id": int(np.random.choice(plant_ids)),
                "machine_type": np.random.choice(["CNC", "Press", "Welding", "Assembly", "Paint"]),
                "rated_capacity_per_hour": int(np.random.randint(20, 500)),
                "commissioned_date": fake.date_between(date(2012, 1, 1), date(2024, 12, 31)).isoformat(),
                "is_active": np.random.choice(["Y", "N"], p=[0.9, 0.1]),
                "created_at": fake.date_between(date(2018, 1, 1), date(2024, 12, 31)).isoformat(),
                "updated_at": fake.date_between(date(2024, 1, 1), date(2026, 3, 1)).isoformat(),
            }
        )
    write_csv(
        MASTER_DIR / "machine.csv",
        [
            "machine_id", "machine_code", "machine_name", "plant_id", "machine_type",
            "rated_capacity_per_hour", "commissioned_date", "is_active",
            "created_at", "updated_at",
        ],
        rows,
    )


def generate_carriers() -> None:
    rows = []
    for carrier_id in range(1, MASTER_ROW_COUNTS["carrier"] + 1):
        rows.append(
            {
                "carrier_id": carrier_id,
                "carrier_code": f"CAR-{carrier_id:04d}",
                "carrier_name": fake.company(),
                "transport_mode": np.random.choice(CARRIER_MODES),
                "service_level": np.random.choice(["Standard", "Express", "Economy"]),
                "country_code": fake.country_code(),
                "is_active": np.random.choice(["Y", "N"], p=[0.93, 0.07]),
                "created_at": fake.date_between(date(2017, 1, 1), date(2024, 12, 31)).isoformat(),
                "updated_at": fake.date_between(date(2024, 1, 1), date(2026, 3, 1)).isoformat(),
            }
        )
    write_csv(
        MASTER_DIR / "carrier.csv",
        [
            "carrier_id", "carrier_code", "carrier_name", "transport_mode",
            "service_level", "country_code", "is_active", "created_at", "updated_at",
        ],
        rows,
    )


def generate_customers() -> None:
    rows = []
    for customer_id in range(1, MASTER_ROW_COUNTS["customer"] + 1):
        rows.append(
            {
                "customer_id": customer_id,
                "customer_code": f"CUS-{customer_id:06d}",
                "customer_name": fake.company(),
                "customer_segment": np.random.choice(["OEM", "Dealer", "Fleet", "Aftermarket"], p=[0.35, 0.35, 0.15, 0.15]),
                "country_code": fake.country_code(),
                "city": fake.city(),
                "credit_limit_usd": int(np.random.randint(50000, 5000000)),
                "is_active": np.random.choice(["Y", "N"], p=[0.91, 0.09]),
                "created_at": fake.date_between(date(2016, 1, 1), date(2024, 12, 31)).isoformat(),
                "updated_at": fake.date_between(date(2024, 1, 1), date(2026, 3, 1)).isoformat(),
            }
        )
    write_csv(
        MASTER_DIR / "customer.csv",
        [
            "customer_id", "customer_code", "customer_name", "customer_segment",
            "country_code", "city", "credit_limit_usd", "is_active",
            "created_at", "updated_at",
        ],
        rows,
    )


def generate_employees() -> None:
    rows = []
    plant_ids = list(range(1, MASTER_ROW_COUNTS["plant"] + 1))
    for employee_id in range(1, MASTER_ROW_COUNTS["employee"] + 1):
        rows.append(
            {
                "employee_id": employee_id,
                "employee_code": f"EMP-{employee_id:06d}",
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": fake.email(),
                "department": np.random.choice(
                    ["Procurement", "Production", "Quality", "Logistics", "Planning", "Maintenance"]
                ),
                "plant_id": int(np.random.choice(plant_ids)),
                "hire_date": fake.date_between(date(2010, 1, 1), date(2025, 6, 30)).isoformat(),
                "is_active": np.random.choice(["Y", "N"], p=[0.88, 0.12]),
                "created_at": fake.date_between(date(2018, 1, 1), date(2024, 12, 31)).isoformat(),
                "updated_at": fake.date_between(date(2024, 1, 1), date(2026, 3, 1)).isoformat(),
            }
        )
    write_csv(
        MASTER_DIR / "employee.csv",
        [
            "employee_id", "employee_code", "first_name", "last_name", "email",
            "department", "plant_id", "hire_date", "is_active", "created_at", "updated_at",
        ],
        rows,
    )


def generate_calendar() -> None:
    rows = []
    start = date(2020, 1, 1)
    end = date(2030, 12, 31)
    current = start
    while current <= end:
        fiscal_year = current.year if current.month >= 4 else current.year - 1
        fiscal_quarter = ((current.month - 4) % 12) // 3 + 1
        rows.append(
            {
                "date_key": int(current.strftime("%Y%m%d")),
                "calendar_date": current.isoformat(),
                "year": current.year,
                "quarter": (current.month - 1) // 3 + 1,
                "month": current.month,
                "month_name": current.strftime("%B"),
                "day_of_month": current.day,
                "day_of_week": current.isoweekday(),
                "day_name": current.strftime("%A"),
                "week_of_year": current.isocalendar().week,
                "is_weekend": "Y" if current.weekday() >= 5 else "N",
                "is_holiday": "N",
                "fiscal_year": fiscal_year,
                "fiscal_quarter": fiscal_quarter,
            }
        )
        current += timedelta(days=1)
    write_csv(
        MASTER_DIR / "calendar.csv",
        [
            "date_key", "calendar_date", "year", "quarter", "month", "month_name",
            "day_of_month", "day_of_week", "day_name", "week_of_year",
            "is_weekend", "is_holiday", "fiscal_year", "fiscal_quarter",
        ],
        rows,
    )


def main() -> None:
    print("Generating master data...")
    generate_suppliers()
    generate_materials()
    generate_plants()
    generate_warehouses()
    generate_machines()
    generate_carriers()
    generate_customers()
    generate_employees()
    generate_calendar()
    print("Master data generation complete.")


if __name__ == "__main__":
    main()
