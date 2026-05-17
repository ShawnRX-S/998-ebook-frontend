import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "bookstore.db"
print("Checking database:", DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

tables = ["book_groups", "books", "book_keys", "encrypted_books", "order_status", "cart"]

for table in tables:
    try:
        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(table, "=", count)
    except Exception as e:
        print(table, "ERROR:", e)

print("\nBooks:")
try:
    rows = cur.execute("""
        SELECT book_index, title, filename
        FROM books
        WHERE group_id = 'default'
        ORDER BY book_index
    """).fetchall()

    for row in rows:
        print(row)
except Exception as e:
    print("books query error:", e)

conn.close()