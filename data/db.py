import sqlite3
from pathlib import Path

DB_PATH = Path("data/domains.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS domains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT NOT NULL UNIQUE,
        brand_score INTEGER NOT NULL DEFAULT 0,
        seo_score INTEGER NOT NULL DEFAULT 0,
        final_score INTEGER NOT NULL DEFAULT 0,
        availability_status TEXT,
        action TEXT,
        is_premium INTEGER,
        registration_price REAL,
        renew_price REAL,
        last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def upsert_domain_result(result: dict):
    availability = result.get("availability", {})

    available = availability.get("available")
    if available is True:
        availability_status = "AVAILABLE"
    elif available is False:
        availability_status = "NOT_AVAILABLE"
    else:
        availability_status = "UNKNOWN"

    is_premium = availability.get("is_premium")
    if is_premium is True:
        is_premium_value = 1
    elif is_premium is False:
        is_premium_value = 0
    else:
        is_premium_value = None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO domains (
        domain,
        brand_score,
        seo_score,
        final_score,
        availability_status,
        action,
        is_premium,
        registration_price,
        renew_price,
        created_at,
        last_seen_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    ON CONFLICT(domain) DO UPDATE SET
        brand_score = excluded.brand_score,
        seo_score = excluded.seo_score,
        final_score = excluded.final_score,
        availability_status = excluded.availability_status,
        action = excluded.action,
        is_premium = excluded.is_premium,
        registration_price = excluded.registration_price,
        renew_price = excluded.renew_price,
        last_seen_at = CURRENT_TIMESTAMP
    """, (
        result["domain"],
        result["brand_score"],
        result["seo_score"],
        result["score"],
        availability_status,
        result.get("action"),
        is_premium_value,
        availability.get("registration_price"),
        availability.get("renew_price"),
    ))

    conn.commit()
    conn.close()


def fetch_domains_by_action(action: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT domain, brand_score, seo_score, final_score, availability_status, action,
           is_premium, registration_price, renew_price, created_at, last_seen_at
    FROM domains
    WHERE action = ?
    ORDER BY final_score DESC, brand_score DESC
    """, (action,))

    rows = cursor.fetchall()
    conn.close()
    return rows