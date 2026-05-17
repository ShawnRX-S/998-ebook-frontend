import os
import sqlite3
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

DB_PATH = "bookstore.db"
GROUP_ID = "default"

DEMO_BOOKS = [
    {
        "book_index": 0,
        "title": "Ot For Ebook Platform",
        "author": "Demo Author",
        "filename": "ot_for_ebook_platform.txt",
        "content": b"Oblivious Transfer for Ebook Platform demo ebook content.\n",
        "price": 12.50,
    },
    {
        "book_index": 1,
        "title": "Privacy By Design",
        "author": "Demo Author",
        "filename": "privacy_by_design.txt",
        "content": b"Privacy by Design demo ebook content.\n",
        "price": 9.99,
    },
    {
        "book_index": 2,
        "title": "Private Catalog Example",
        "author": "Demo Author",
        "filename": "private_catalog_example.txt",
        "content": b"Private Catalog Example ebook content.\n",
        "price": 8.00,
    },
    {
        "book_index": 3,
        "title": "Secure Download Demo",
        "author": "Demo Author",
        "filename": "secure_download_demo.txt",
        "content": b"Secure Download Demo ebook content.\n",
        "price": 10.00,
    },
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("PRAGMA foreign_keys = ON")

    # Clear old demo data
    cur.execute("DELETE FROM order_status")
    cur.execute("DELETE FROM book_keys")
    cur.execute("DELETE FROM encrypted_books")
    cur.execute("DELETE FROM books")
    cur.execute("DELETE FROM book_groups")

    # Insert default group
    cur.execute(
        """
        INSERT INTO book_groups (group_id, name, description, is_active)
        VALUES (?, ?, ?, ?)
        """,
        (
            GROUP_ID,
            "Default OT Book Group",
            "Main privacy-preserving OT ebook group",
            1,
        ),
    )

    for book in DEMO_BOOKS:
        cur.execute(
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
                book["book_index"],
                book["title"],
                book["author"],
                book["filename"],
                "txt",
                book["price"],
                4.5,
                f"Summary for {book['title']}",
                f"Description for {book['title']}",
                f"{book['title']} Cover",
                None,
                1,
                1,
            ),
        )

        book_id = cur.lastrowid

        # AES-256 key = 32 bytes
        aes_key = os.urandom(32)

        aesgcm = AESGCM(aes_key)
        nonce = os.urandom(12)

        encrypted = aesgcm.encrypt(nonce, book["content"], None)

        # cryptography AESGCM returns ciphertext + tag together
        ciphertext = encrypted[:-16]
        tag = encrypted[-16:]

        cur.execute(
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
                book["book_index"],
                aes_key,
            ),
        )

        cur.execute(
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
                book["book_index"],
                nonce,
                ciphertext,
                tag,
                None,
            ),
        )

    conn.commit()

    print("Seed completed.")
    print("Inserted books:", len(DEMO_BOOKS))

    rows = cur.execute(
        """
        SELECT book_index, title, filename
        FROM books
        WHERE group_id = ?
        ORDER BY book_index ASC
        """,
        (GROUP_ID,),
    ).fetchall()

    for row in rows:
        print(row)

    conn.close()


if __name__ == "__main__":
    main()