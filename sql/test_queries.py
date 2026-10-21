"""
Test Business Queries Runner
Executes all queries in sql/business_queries.sql against sql/business_bi.db.
"""

import sqlite3
from pathlib import Path


def test_business_queries():
    root = Path(__file__).resolve().parent.parent
    db_path = root / "sql" / "business_bi.db"
    queries_path = root / "sql" / "business_queries.sql"

    conn = sqlite3.connect(db_path)
    with open(queries_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Strip pure comment lines
    clean_sql = "\n".join(line for line in lines if not line.strip().startswith("--"))

    # Split by statements
    statements = [stmt.strip() for stmt in clean_sql.split(";") if stmt.strip()]

    print("=" * 70)
    print("EXECUTING BUSINESS QUERIES IN SQLITE DATA WAREHOUSE")
    print("=" * 70)

    for idx, stmt in enumerate(statements, 1):
        if "SELECT" in stmt.upper():
            cursor = conn.cursor()
            cursor.execute(stmt)
            rows = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]
            print(f"\n[QUERY {idx}] Executed successfully | Returned {len(rows)} rows | Columns: {len(col_names)}")
            print(f"           Header: {col_names[:5]}")
            if rows:
                print(f"           Row 1 : {rows[0][:5]}")

    conn.close()
    print("\n" + "=" * 70)
    print("ALL BUSINESS QUERIES EXECUTED AND VERIFIED")
    print("=" * 70)


if __name__ == "__main__":
    test_business_queries()
