import os
import sqlite3
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "bookstore.db"
print("Using database:", DB_PATH)


DB_PATH = "bookstore.db"
GROUP_ID = "default"


BOOKS_16 = [
    ("Book 00 - Privacy Basics", "book_00_privacy_basics.txt"),
    ("Book 01 - OT Introduction", "book_01_ot_introduction.txt"),
    ("Book 02 - Secure Download", "book_02_secure_download.txt"),
    ("Book 03 - Private Catalog", "book_03_private_catalog.txt"),
    ("Book 04 - AES GCM", "book_04_aes_gcm.txt"),
    ("Book 05 - Key Management", "book_05_key_management.txt"),
    ("Book 06 - Database Security", "book_06_database_security.txt"),
    ("Book 07 - API Privacy", "book_07_api_privacy.txt"),
    ("Book 08 - Client Side Choice", "book_08_client_side_choice.txt"),
    ("Book 09 - Masked Keys", "book_09_masked_keys.txt"),
    ("Book 10 - PRF Design", "book_10_prf_design.txt"),
    ("Book 11 - DH OT Channel", "book_11_dh_ot_channel.txt"),
    ("Book 12 - Privacy Engineering", "book_12_privacy_engineering.txt"),
    ("Book 13 - Secure Backend", "book_13_secure_backend.txt"),
    ("Book 14 - Encrypted Ebook Store", "book_14_encrypted_ebook_store.txt"),
    ("Book 15 - Final OT Demo", "book_15_final_ot_demo.txt"),
]


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
            "Main privacy-preserving OT ebook group with 16 demo books",
            1,
        ),
    )


def clear_default_group_data(cursor):
    """
    Clear old demo data for default group.

    Important:
    This only clears OT book data in default group.
    It does not drop tables.
    """
    cursor.execute("DELETE FROM book_keys WHERE group_id = ?", (GROUP_ID,))
    cursor.execute("DELETE FROM encrypted_books WHERE group_id = ?", (GROUP_ID,))
    cursor.execute("DELETE FROM books WHERE group_id = ?", (GROUP_ID,))


def insert_one_book(cursor, book_index: int, title: str, filename: str):
    author = "Demo Author"
    file_type = "txt"
    price = 9.99
    rating = 4.5

    plaintext = (
        f"This is encrypted demo content for {title}.\n"
        f"This book index is {book_index}.\n"
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

    print(f"Inserted index={book_index:02d}, title={title}, filename={filename}")


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA foreign_keys = ON")

        ensure_default_group(cursor)
        clear_default_group_data(cursor)

        for book_index, (title, filename) in enumerate(BOOKS_16):
            insert_one_book(cursor, book_index, title, filename)

        conn.commit()

        print()
        print("SUCCESS: 16 OT demo books inserted into database.")
        print("Group ID:", GROUP_ID)
        print("Total books:", len(BOOKS_16))

        rows = cursor.execute(
            """
            SELECT book_index, title, filename
            FROM books
            WHERE group_id = ?
            ORDER BY book_index ASC
            """,
            (GROUP_ID,),
        ).fetchall()

        print()
        print("Books in database:")
        for row in rows:
            print(row)

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()