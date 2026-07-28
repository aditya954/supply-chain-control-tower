"""Shared configuration for Supply Chain Control Tower sample data generation."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DATA_DIR = PROJECT_ROOT / "sample_data"
MASTER_DIR = SAMPLE_DATA_DIR / "master"
TRANSACTIONAL_DIR = SAMPLE_DATA_DIR / "transactional"

RANDOM_SEED = 42

MASTER_ROW_COUNTS = {
    "supplier": 1000,
    "material": 1000,
    "plant": 50,
    "warehouse": 200,
    "machine": 1000,
    "carrier": 100,
    "customer": 1000,
    "employee": 1000,
}

TRANSACTIONAL_ROW_COUNTS = {
    "purchase_orders": 100_000,
    "purchase_order_lines": 250_000,
    "inventory": 50_000,
    "inventory_transactions": 100_000,
    "production_orders": 100_000,
    "production_transactions": 100_000,
    "machine_sensor_readings": 100_000,
    "shipments": 100_000,
    "shipment_tracking": 300_000,
    "sales_orders": 100_000,
    "sales_order_lines": 250_000,
    "quality_inspection": 100_000,
    "defects": 20_000,
    "returns": 15_000,
    "warranty_claims": 10_000,
    "supplier_deliveries": 100_000,
}

PO_STATUSES = ["Open", "Closed", "Cancelled", "Partial"]
SHIPMENT_STATUSES = ["Created", "In Transit", "Delivered", "Delayed", "Cancelled"]
PAYMENT_TERMS = ["NET30", "NET45", "NET60", "NET90"]
MATERIAL_TYPES = ["Raw", "Semi-Finished", "Finished", "Packaging", "MRO"]
MATERIAL_CATEGORIES = [
    "Powertrain", "Chassis", "Electronics", "Interior", "Exterior",
    "Fasteners", "Fluids", "Tires", "Batteries", "Seating",
]
PLANT_REGIONS = ["NA", "EMEA", "APAC", "LATAM"]
CARRIER_MODES = ["Road", "Rail", "Air", "Ocean"]
DEFECT_TYPES = ["Dimensional", "Surface", "Functional", "Material", "Assembly"]
RETURN_REASONS = ["Defective", "Wrong Part", "Damaged in Transit", "Customer Changed Mind"]
WARRANTY_TYPES = ["Standard", "Extended", "Powertrain"]
