import os
import sqlite3
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


DB_PATH = Path(__file__).resolve().parent / "bookstore.db"
GROUP_ID = "default"
TOTAL_BOOKS = 128


def make_book_title(book_index: int) -> str:
    topics = [
        "Privacy Basics",
        "OT Introduction",
        "Secure Download",
        "Private Catalog",
        "AES GCM",
        "Key Management",
        "Database Security",
        "API Privacy",
        "Client Side Choice",
        "Masked Keys",
        "PRF Design",
        "DH OT Channel",
        "Privacy Engineering",
        "Secure Backend",
        "Encrypted Ebook Store",
        "Final OT Demo",
    ]

    topic = topics[book_index % len(topics)]
    return f"Book {book_index:03d} - {topic}"


def make_filename(book_index: int) -> str:
    title = make_book_title(book_index)
    safe = (
        title.lower()
        .replace(" - ", "_")
        .replace(" ", "_")
        .replace("-", "_")
    )
    return f"{safe}.txt"


def ensure_default_group(cursor):
    cursor.execute(
        """
        INSERT OR IGNORE INTO book_groups (
            group_id,
            name,
            description,
            is_active
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            GROUP_ID,
            "Default OT Book Group",
            "Main privacy-preserving OT ebook group with 128 demo books",
            1,
        ),
    )


def clear_default_group_data(cursor):
    """
    Clear old demo data for default group.

    This will remove old default books, keys, and encrypted books,
    then recreate 128 complete OT-compatible records.
    """
    cursor.execute("DELETE FROM book_keys WHERE group_id = ?", (GROUP_ID,))
    cursor.execute("DELETE FROM encrypted_books WHERE group_id = ?", (GROUP_ID,))
    cursor.execute("DELETE FROM books WHERE group_id = ?", (GROUP_ID,))


def insert_one_book(cursor, book_index: int):
    title = make_book_title(book_index)
    filename = make_filename(book_index)

    author = "Demo Author"
    file_type = "txt"
    price = 9.99
    rating = 4.5

    plaintext = (
        f"This is encrypted demo content for {title}.\n"
        f"This book index is {book_index}.\n"
        f"This database contains 128 OT-protected demo books.\n"
        f"It is protected by the old OT + FastAPI + database flow.\n"
    ).encode("utf-8")

    cursor.execute(
        """
        INSERT INTO books (
            group_id,
            book_index,
            title,
            author,
            filename,
            file_type,
            price,
            rating,
            summary,
            description,
            coverText,
            coverPath,
            isPrivacyProtected,
            is_active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            GROUP_ID,
            book_index,
            title,
            author,
            filename,
            file_type,
            price,
            rating,
            f"Summary for {title}",
            f"Description for {title}",
            f"{title} Cover",
            None,
            1,
            1,
        ),
    )

    book_id = cursor.lastrowid

    # AES-256 key = 32 bytes
    aes_key = os.urandom(32)

    # AES-GCM standard package:
    # nonce = 12 bytes
    # tag = 16 bytes
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)
    encrypted = aesgcm.encrypt(nonce, plaintext, None)

    ciphertext = encrypted[:-16]
    tag = encrypted[-16:]

    cursor.execute(
        """
        INSERT INTO book_keys (
            book_id,
            group_id,
            book_index,
            aes_key
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            book_id,
            GROUP_ID,
            book_index,
            aes_key,
        ),
    )

    cursor.execute(
        """
        INSERT INTO encrypted_books (
            book_id,
            group_id,
            book_index,
            nonce,
            ciphertext,
            tag,
            storage_path
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            book_id,
            GROUP_ID,
            book_index,
            nonce,
            ciphertext,
            tag,
            None,
        ),
    )

    print(f"Inserted index={book_index:03d}, title={title}, filename={filename}")


def main():
    print("Using database:", DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA foreign_keys = ON")

        ensure_default_group(cursor)
        clear_default_group_data(cursor)

        for book_index in range(TOTAL_BOOKS):
            insert_one_book(cursor, book_index)

        conn.commit()

        print()
        print("SUCCESS: 128 OT demo books inserted into database.")
        print("Group ID:", GROUP_ID)
        print("Total books:", TOTAL_BOOKS)

        rows = cursor.execute(
            """
            SELECT book_index, title, filename
            FROM books
            WHERE group_id = ?
            ORDER BY book_index ASC
            LIMIT 10
            """,
            (GROUP_ID,),
        ).fetchall()

        print()
        print("First 10 books in database:")
        for row in rows:
            print(row)

        count = cursor.execute(
            """
            SELECT COUNT(*)
            FROM books
            WHERE group_id = ?
            """,
            (GROUP_ID,),
        ).fetchone()[0]

        print()
        print("Book count in DB:", count)

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()