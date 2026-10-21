"""
Apply Views Script
Applies sql/views.sql to sql/business_bi.db and verifies view row counts.
"""

import sqlite3
from pathlib import Path


def apply_views():
    root = Path(__file__).resolve().parent.parent
    db_path = root / "sql" / "business_bi.db"
    views_path = root / "sql" / "views.sql"

    conn = sqlite3.connect(db_path)
    with open(views_path, "r", encoding="utf-8") as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;")
    views = [r[0] for r in cursor.fetchall()]

    print("=" * 70)
    print("BI VIEWS INSTALLED SUCCESSFULLY IN SQLITE WAREHOUSE")
    print("=" * 70)
    for v in views:
        cursor.execute(f"SELECT COUNT(*) FROM {v};")
        count = cursor.fetchone()[0]
        print(f"  [VIEW] {v:<35}: {count:,} rows")
    conn.close()


if __name__ == "__main__":
    apply_views()
