import sqlite3
import base64
from typing import List, Dict, Any


# =========================================
# Database Connection
# =========================================

class DB:

    def __init__(self, db_path="ebook_ot.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def execute(self, sql: str, params: tuple = ()):
        cur = self.cursor.execute(sql, params)
        self.conn.commit()
        return cur

    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        cur = self.cursor.execute(sql, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]


db = DB()


# =========================================
# 1. book_groups
# =========================================

class BookGroupDAO:

    @staticmethod
    def create(group_id, name, description=""):
        db.execute("""
        INSERT INTO book_groups
        (group_id, name, description)
        VALUES (?, ?, ?)
        """, (group_id, name, description))

    @staticmethod
    def get_all():
        return db.query("""
        SELECT * FROM book_groups
        WHERE is_active = 1
        ORDER BY created_at DESC
        """)

    @staticmethod
    def get_by_group_id(group_id):
        result = db.query("""
        SELECT * FROM book_groups
        WHERE group_id = ?
        """, (group_id,))
        return result[0] if result else None


# =========================================
# 2. books
# =========================================

class BookDAO:

    @staticmethod
    def create(data: dict):

        db.execute("""
        INSERT INTO books
        (
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
            isPrivacyProtected
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["group_id"],
            data["book_index"],
            data["title"],
            data.get("author"),
            data["filename"],
            data.get("file_type"),
            data.get("price", 0),
            data.get("rating", 0),
            data.get("summary"),
            data.get("description"),
            data.get("coverText"),
            data.get("coverPath"),
            data.get("isPrivacyProtected", 1)
        ))

    @staticmethod
    def get_by_id(book_id):
        result = db.query("""
        SELECT * FROM books
        WHERE id = ?
        """, (book_id,))
        return result[0] if result else None

    @staticmethod
    def delete(book_id):
        db.execute("""
        DELETE FROM books
        WHERE id = ?
        """, (book_id,))

    @staticmethod
    def update(book_id, data: dict):

        db.execute("""
        UPDATE books
        SET
            title=?,
            author=?,
            price=?,
            rating=?,
            summary=?,
            description=?,
            coverText=?,
            coverPath=?
        WHERE id=?
        """, (
            data["title"],
            data.get("author"),
            data.get("price", 0),
            data.get("rating", 0),
            data.get("summary"),
            data.get("description"),
            data.get("coverText"),
            data.get("coverPath"),
            book_id
        ))

    # =====================================
    # 前端 Books.vue 搜索接口
    # =====================================

    @staticmethod
    def search_books(
            page=1,
            pageSize=9,
            keyword="",
            sort="NONE",
            group_id="default"
    ):

        offset = (page - 1) * pageSize

        where_clauses = [
            "b.is_active = 1",
            "b.group_id = ?"
        ]

        params = [group_id]

        # keyword search
        if keyword and keyword.strip():

            kw = f"%{keyword.strip()}%"

            where_clauses.append("""
            (
                b.title LIKE ?
                OR b.author LIKE ?
                OR b.summary LIKE ?
                OR b.description LIKE ?
            )
            """)

            params.extend([kw, kw, kw, kw])

        where_sql = "WHERE " + " AND ".join(where_clauses)

        # sort
        sort_map = {
            "PRICE_ASC": "ORDER BY b.price ASC",
            "PRICE_DESC": "ORDER BY b.price DESC",
            "NONE": "ORDER BY b.book_index ASC"
        }

        order_sql = sort_map.get(sort, "ORDER BY b.book_index ASC")

        # total
        count_sql = f"""
        SELECT COUNT(*) AS total
        FROM books b
        {where_sql}
        """

        total_result = db.query(count_sql, tuple(params))
        total = total_result[0]["total"] if total_result else 0

        # current page data
        data_sql = f"""
        SELECT
            b.id,
            b.book_index AS `index`,
            b.title,
            b.author,
            b.filename,
            b.price,
            b.rating,
            b.summary,
            b.description,
            b.coverText,
            b.coverPath,
            b.isPrivacyProtected
        FROM books b
        {where_sql}
        {order_sql}
        LIMIT ? OFFSET ?
        """

        rows = db.query(
            data_sql,
            tuple(params + [pageSize, offset])
        )

        # sqlite bool convert
        for row in rows:
            row["isPrivacyProtected"] = bool(
                row["isPrivacyProtected"]
            )

        return {
            "list": rows,
            "total": total,
            "page": page,
            "pageSize": pageSize,
            "totalPages": (total + pageSize - 1) // pageSize
        }


# =========================================
# 3. encrypted_books
# =========================================

class EncryptedBookDAO:

    @staticmethod
    def create(
            book_id,
            group_id,
            book_index,
            nonce,
            ciphertext,
            tag,
            storage_path=None
    ):

        db.execute("""
        INSERT INTO encrypted_books
        (
            book_id,
            group_id,
            book_index,
            nonce,
            ciphertext,
            tag,
            storage_path
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            book_id,
            group_id,
            book_index,
            nonce,
            ciphertext,
            tag,
            storage_path
        ))

    @staticmethod
    def get_by_group(group_id):

        return db.query("""
        SELECT *
        FROM encrypted_books
        WHERE group_id = ?
        ORDER BY book_index ASC
        """, (group_id,))


# =========================================
# 4. book_keys (DEMO VERSION)
# =========================================

class BookKeyDAO:

    @staticmethod
    def create(
            book_id,
            group_id,
            book_index,
            aes_key
    ):

        db.execute("""
        INSERT INTO book_keys
        (
            book_id,
            group_id,
            book_index,
            aes_key
        )
        VALUES (?, ?, ?, ?)
        """, (
            book_id,
            group_id,
            book_index,
            aes_key
        ))

    @staticmethod
    def get_keys_for_group(group_id):

        rows = db.query("""
        SELECT aes_key
        FROM book_keys
        WHERE group_id = ?
        ORDER BY book_index ASC
        """, (group_id,))

        return [row["aes_key"] for row in rows]


# =========================================
# 5. order_status
# =========================================

class OrderStatusDAO:

    @staticmethod
    def create(
            order_id,
            user_id,
            group_id,
            payment_status="paid"
    ):

        db.execute("""
        INSERT INTO order_status
        (
            order_id,
            user_id,
            group_id,
            payment_status
        )
        VALUES (?, ?, ?, ?)
        """, (
            order_id,
            user_id,
            group_id,
            payment_status
        ))

    @staticmethod
    def get_user_orders(user_id):

        return db.query("""
        SELECT *
        FROM order_status
        WHERE user_id = ?
        ORDER BY created_at DESC
        """, (user_id,))

    @staticmethod
    def has_group_access(user_id, group_id):

        rows = db.query("""
        SELECT *
        FROM order_status
        WHERE user_id = ?
        AND group_id = ?
        AND payment_status = 'paid'
        """, (user_id, group_id))

        return len(rows) > 0


# =========================================
# 6. cart
# =========================================

class CartDAO:

    @staticmethod
    def add(
            user_id,
            group_id,
            book_index,
            qty=1
    ):

        db.execute("""
        INSERT INTO cart
        (
            user_id,
            group_id,
            book_index,
            qty
        )
        VALUES (?, ?, ?, ?)

        ON CONFLICT(user_id, group_id, book_index)

        DO UPDATE SET
            qty = qty + excluded.qty
        """, (
            user_id,
            group_id,
            book_index,
            qty
        ))

    @staticmethod
    def get_user_cart(user_id):

        return db.query("""
        SELECT
            c.id AS cart_id,
            c.qty,
            b.book_index AS `index`,
            b.title,
            b.author,
            b.price,
            b.rating,
            b.summary,
            b.coverPath,
            b.group_id
        FROM cart c

        JOIN books b
        ON c.group_id = b.group_id
        AND c.book_index = b.book_index

        WHERE c.user_id = ?

        ORDER BY c.created_at DESC
        """, (user_id,))

    @staticmethod
    def update_qty(cart_id, qty):

        db.execute("""
        UPDATE cart
        SET qty = ?
        WHERE id = ?
        """, (qty, cart_id))

    @staticmethod
    def remove(cart_id):

        db.execute("""
        DELETE FROM cart
        WHERE id = ?
        """, (cart_id,))

    @staticmethod
    def clear(user_id):

        db.execute("""
        DELETE FROM cart
        WHERE user_id = ?
        """, (user_id,))


# =========================================
# 7. OT DB Service
# =========================================

class BookStorageDBService:

    # =====================================
    # Public Catalog
    # =====================================

    @staticmethod
    def get_public_catalog(
            group_id: str = "default"
    ) -> dict:

        books = db.query("""
        SELECT
            book_index,
            title,
            author,
            filename
        FROM books
        WHERE group_id = ?
        AND is_active = 1
        ORDER BY book_index ASC
        """, (group_id,))

        result = []

        for book in books:

            result.append({
                "index": book["book_index"],
                "title": book["title"],
                "author": book["author"],
                "filename": book["filename"]
            })

        return {
            "group_id": group_id,
            "N": len(result),
            "books": result,
            "privacy_note":
                "Use index only on the client side. "
                "Do not send choice_index to the server."
        }

    # =====================================
    # AES Keys
    # =====================================

    @staticmethod
    def get_book_keys_for_group(
            group_id: str = "default"
    ) -> list[bytes]:

        rows = db.query("""
        SELECT aes_key
        FROM book_keys
        WHERE group_id = ?
        ORDER BY book_index ASC
        """, (group_id,))

        return [
            row["aes_key"]
            for row in rows
        ]

    # =====================================
    # Encrypted Package
    # =====================================

    @staticmethod
    def get_encrypted_group_package(
            group_id: str = "default"
    ) -> dict:

        rows = db.query("""
        SELECT
            b.book_index,
            b.filename,
            b.title,
            e.nonce,
            e.ciphertext,
            e.tag
        FROM books b

        JOIN encrypted_books e
        ON b.id = e.book_id

        WHERE b.group_id = ?

        ORDER BY b.book_index ASC
        """, (group_id,))

        books = []

        for row in rows:

            books.append({
                "index": row["book_index"],
                "filename": row["filename"],
                "title": row["title"],
                "nonce": base64.b64encode(
                    row["nonce"]
                ).decode(),

                "ciphertext": base64.b64encode(
                    row["ciphertext"]
                ).decode(),

                "tag": base64.b64encode(
                    row["tag"]
                ).decode()
            })

        return {
            "group_id": group_id,
            "N": len(books),
            "books": books
        }