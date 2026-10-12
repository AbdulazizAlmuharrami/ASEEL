from database import get_db, now_iso


SEED_PERFUMES = [
    {
        "unique_code": "ASEEL-ROYAL-OUD-001",
        "perfume_name": "Royal Oud",
        "brand_name": "Super Oud",
        "batch_number": "B240926",
        "box_serial_number": "SO-000001",
        "manufacturing_date": "2026-09-24",
        "authorized_seller": "Super Oud",
        "place_of_sale": "Yas Mall, Abu Dhabi",
        "status": "Genuine",
        "scan_threshold": 5,
        "notes": "Seed record for capstone demonstration.",
    },
    {
        "unique_code": "ASEEL-DESERT-MUSK-002",
        "perfume_name": "Desert Musk",
        "brand_name": "Al Noor Perfumes",
        "batch_number": "B250926",
        "box_serial_number": "AN-000002",
        "manufacturing_date": "2026-09-25",
        "authorized_seller": "Al Noor Perfumes",
        "place_of_sale": "Dubai Mall, Dubai",
        "status": "Genuine",
        "scan_threshold": 5,
        "notes": "Seed record for capstone demonstration.",
    },
    {
        "unique_code": "ASEEL-AMBER-NIGHT-003",
        "perfume_name": "Amber Night",
        "brand_name": "Oud House",
        "batch_number": "B260926",
        "box_serial_number": "OH-000003",
        "manufacturing_date": "2026-09-26",
        "authorized_seller": "Oud House",
        "place_of_sale": "Marina Mall, Abu Dhabi",
        "status": "Genuine",
        "scan_threshold": 5,
        "notes": "Seed record for capstone demonstration.",
    },
]


def seed_if_empty():
    db = get_db()
    count = db.execute("SELECT COUNT(*) AS n FROM perfumes").fetchone()["n"]
    if count > 0:
        return

    timestamp = now_iso()
    for item in SEED_PERFUMES:
        db.execute(
            """
            INSERT INTO perfumes (
                unique_code, perfume_name, brand_name, batch_number,
                box_serial_number, manufacturing_date, authorized_seller,
                place_of_sale, status, scan_count, scan_threshold, notes,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?)
            """,
            (
                item["unique_code"],
                item["perfume_name"],
                item["brand_name"],
                item["batch_number"],
                item["box_serial_number"],
                item["manufacturing_date"],
                item["authorized_seller"],
                item["place_of_sale"],
                item["status"],
                item["scan_threshold"],
                item["notes"],
                timestamp,
                timestamp,
            ),
        )
    db.commit()
