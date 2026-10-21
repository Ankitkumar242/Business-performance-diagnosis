"""
Environment and Dependency Verification Script
Business Performance Diagnosis & Decision Intelligence Platform
"""

import sys
import os
import platform
import sqlite3
from pathlib import Path


def check_python_version():
    print("=" * 70)
    print("STAGE 2 VERIFICATION: ENVIRONMENT & DEPENDENCIES")
    print("=" * 70)
    ver = sys.version_info
    py_ver = f"{ver.major}.{ver.minor}.{ver.micro}"
    print(f"[1/5] Python Version Check: {py_ver} ({platform.python_implementation()}) on {platform.system()} {platform.release()}")
    if ver.major < 3 or (ver.major == 3 and ver.minor < 10):
        print(f"      [FAIL] Python 3.10+ required. Found {py_ver}")
        return False
    print("      [PASS] Python version meets minimum criteria (>= 3.10).")
    return True


def check_packages():
    print("\n[2/5] Package Imports & Version Verification:")
    packages = [
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("matplotlib", "Matplotlib"),
        ("seaborn", "Seaborn"),
        ("sklearn", "Scikit-learn"),
        ("pytest", "Pytest"),
        ("sqlalchemy", "SQLAlchemy"),
        ("openpyxl", "OpenPyXL"),
        ("dateutil", "Python-Dateutil"),
    ]
    all_passed = True
    for mod_name, display_name in packages:
        try:
            mod = __import__(mod_name)
            version = getattr(mod, "__version__", "Available")
            print(f"      [PASS] {display_name:<15}: Version {version}")
        except ImportError as e:
            print(f"      [FAIL] {display_name:<15}: Missing ({e})")
            all_passed = False
    return all_passed


def check_sqlite():
    print("\n[3/5] SQLite Relational Engine Verification:")
    try:
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test_ver (id INTEGER PRIMARY KEY, status TEXT);")
        cursor.execute("INSERT INTO test_ver (status) VALUES ('verified');")
        cursor.execute("SELECT status FROM test_ver;")
        result = cursor.fetchone()[0]
        conn.close()
        if result == "verified":
            print(f"      [PASS] SQLite engine working properly. Version: {sqlite3.sqlite_version}")
            return True
        else:
            print("      [FAIL] SQLite query result mismatch.")
            return False
    except Exception as e:
        print(f"      [FAIL] SQLite error: {e}")
        return False


def check_directories():
    print("\n[4/5] Project Directory Hierarchy Check:")
    required_dirs = [
        "data/raw",
        "data/processed",
        "data/profiling",
        "docs",
        "notebooks",
        "powerbi",
        "reports/figures",
        "sql",
        "src",
        "tests",
    ]
    base_dir = Path(__file__).resolve().parent
    all_exist = True
    for d in required_dirs:
        dir_path = base_dir / d
        if dir_path.is_dir():
            print(f"      [PASS] Found: {d}")
        else:
            print(f"      [FAIL] Missing directory: {d}")
            all_exist = False
    return all_exist


def check_write_permissions():
    print("\n[5/5] Filesystem Write Permission Check:")
    base_dir = Path(__file__).resolve().parent
    test_paths = [
        base_dir / "data" / "raw" / ".write_test.tmp",
        base_dir / "reports" / ".write_test.tmp",
    ]
    all_writable = True
    for p in test_paths:
        try:
            p.write_text("write_test", encoding="utf-8")
            content = p.read_text(encoding="utf-8")
            p.unlink()
            if content == "write_test":
                print(f"      [PASS] Writable: {p.parent.relative_to(base_dir)}")
            else:
                print(f"      [FAIL] Readback mismatch in {p.parent.relative_to(base_dir)}")
                all_writable = False
        except Exception as e:
            print(f"      [FAIL] Write failed for {p.parent.relative_to(base_dir)}: {e}")
            all_writable = False
    return all_writable


def main():
    results = [
        check_python_version(),
        check_packages(),
        check_sqlite(),
        check_directories(),
        check_write_permissions(),
    ]
    print("\n" + "=" * 70)
    if all(results):
        print("STAGE 2 VERIFICATION RESULT: ALL CHECKS PASSED (5/5)")
        print("Project scaffolding and environment are 100% verified and ready.")
        print("=" * 70)
        sys.exit(0)
    else:
        print("STAGE 2 VERIFICATION RESULT: FAILED CHECKS DETECTED")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
