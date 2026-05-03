import sqlite3
from typing import List, Dict, Any

# basictool
class DB:
    def __init__(self, db_path="bookstore.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def execute(self, sql: str, params: tuple = ()):
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor

    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        cur = self.cursor.execute(sql, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]

db = DB()



#User
class UserDAO:

    @staticmethod
    def create(username, password_hash, role="user"):
        db.execute("""
        INSERT INTO users (username, password_hash, role)
        VALUES (?, ?, ?)
        """, (username, password_hash, role))

    @staticmethod
    def get_by_id(user_id):
        return db.query("SELECT * FROM users WHERE id = ?", (user_id,))

    @staticmethod
    def get_by_username(username):
        return db.query("SELECT * FROM users WHERE username = ?", (username,))

    @staticmethod
    def update_role(user_id, role):
        db.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))

    @staticmethod
    def delete(user_id):
        db.execute("DELETE FROM users WHERE id = ?", (user_id,))


#Books
class BookDAO:

    @staticmethod
    def create(data: dict):
        db.execute("""
        INSERT INTO books 
        (title, author, price, rating, summary, description, coverText, isPrivacyProtected, category_id, cover_path, file_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["title"], data.get("author"), data["price"],
            data.get("rating", 0), data.get("summary"),
            data.get("description"), data.get("coverText"),
            data.get("isPrivacyProtected", 0),
            data.get("category_id"),
            data.get("cover_path"), data.get("file_path")
        ))

    @staticmethod
    def get_all():
        return db.query("""
        SELECT b.*, c.name AS category
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.id
        """)

    @staticmethod
    def get_by_id(book_id):
        return db.query("SELECT * FROM books WHERE id = ?", (book_id,))

    @staticmethod
    def update(book_id, data: dict):
        db.execute("""
        UPDATE books
        SET title=?, author=?, price=?, rating=?, summary=?, description=?, 
            coverText=?, isPrivacyProtected=?, category_id=?
        WHERE id=?
        """, (
            data["title"], data.get("author"), data["price"],
            data.get("rating", 0), data.get("summary"),
            data.get("description"), data.get("coverText"),
            data.get("isPrivacyProtected", 0),
            data.get("category_id"),
            book_id
        ))

    @staticmethod
    def delete(book_id):
        db.execute("DELETE FROM books WHERE id = ?", (book_id,))


    #Search function special-----------------------------------
    @staticmethod
    def search_books(page=1, pageSize=9, category="ALL", keyword="", sort="NONE"):
        offset = (page - 1) * pageSize

        where_clauses = []
        params = []

        # category
        if category and category != "ALL":
            where_clauses.append("c.name = ?")
            params.append(category)

        # keyword
        if keyword and keyword.strip():
            kw = f"%{keyword.strip()}%"
            where_clauses.append("""
            (b.title LIKE ? OR b.author LIKE ? 
            OR b.summary LIKE ? OR b.description LIKE ?)
            """)
            params.extend([kw, kw, kw, kw])

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        # srot
        sort_map = {
            "PRICE_ASC": "ORDER BY b.price ASC",
            "PRICE_DESC": "ORDER BY b.price DESC",
            "NONE": "ORDER BY b.id ASC"
        }
        order_sql = sort_map.get(sort, "ORDER BY b.id ASC")

        # total
        count_sql = f"""
        SELECT COUNT(*) AS total
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.id
        {where_sql}
        """
        total = db.query(count_sql, tuple(params))[0]["total"]

        # data
        data_sql = f"""
        SELECT 
            b.id,
            b.title,
            b.author,
            b.price,
            b.rating,
            b.summary,
            b.description,
            b.coverText,
            b.isPrivacyProtected,
            b.category_id AS categoryId,
            c.name AS category,
            b.cover_path AS coverPath
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.id
        {where_sql}
        {order_sql}
        LIMIT ? OFFSET ?
        """

        rows = db.query(data_sql, tuple(params + [pageSize, offset]))

        for row in rows:
            row["isPrivacyProtected"] = bool(row["isPrivacyProtected"])

        return {
            "list": rows,
            "total": total,
            "page": page,
            "pageSize": pageSize,
            "totalPages": (total + pageSize - 1) // pageSize
    }

    #sample of Search Function：

#     if receive from front end:
#         {
#         "page": 1,
#         "pageSize": 9,
#         "category": "ALL",
#         "keyword": "",
#         "sort": "PRICE_ASC"
#         }

    #   to use this function:
    #     params = {
    #         "page": 1,
    #         "pageSize": 9,
    #         "category": "Privacy",
    #         "keyword": "design",
    #         "sort": "PRICE_ASC"
    #     }

    #     result = BookDAO.search_books(
    #         page=params["page"],
    #         pageSize=params["pageSize"],
    #         category=params["category"],
    #         keyword=params["keyword"],
    #         sort=params["sort"]
    #     )
    #     result will be like:
    
    # {
    # "list": [
    #     {
    #         "id": 1,
    #         "title": "Privacy by Design",
    #         "author": "Author A",
    #         "price": 9.99,
    #         "rating": 4.5,
    #         "summary": "Intro to privacy-preserving design",
    #         "description": "This is a demo privacy book.",
    #         "coverText": "Privacy Book Cover",
    #         "isPrivacyProtected": True,
    #         "categoryId": 1,
    #         "category": "Privacy",
    #         "coverPath": "/storage/covers/cover_1.jpg"
    #     }
    # ],
    # "total": 100,
    # "page": 1,
    # "pageSize": 9,
    # "totalPages": 12
    # }




#Cart
class CartDAO:

    @staticmethod
    def add(user_id, book_id, qty=1):
        db.execute("""
        INSERT INTO cart (user_id, book_id, qty)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, book_id)
        DO UPDATE SET qty = qty + excluded.qty
        """, (user_id, book_id, qty))

    @staticmethod
    def get_by_user(user_id):
        return db.query("""
        SELECT 
            cart.id AS cart_id,
            cart.qty,
            books.title,
            books.price,
            books.cover_path,
            categories.name AS category
        FROM cart
        JOIN books ON cart.book_id = books.id
        LEFT JOIN categories ON books.category_id = categories.id
        WHERE cart.user_id = ?
        """, (user_id,))

    @staticmethod
    def update_qty(cart_id, qty):
        db.execute("UPDATE cart SET qty = ? WHERE id = ?", (qty, cart_id))

    @staticmethod
    def remove(cart_id):
        db.execute("DELETE FROM cart WHERE id = ?", (cart_id,))

    @staticmethod
    def clear(user_id):
        db.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))



#Orders + Orderitems
class OrderDAO:

    @staticmethod
    def create_order(user_id, items: list, total_amount):
        cursor = db.execute("""
        INSERT INTO orders (order_no, user_id, total_amount, status)
        VALUES (?, ?, ?, ?)
        """, ("ORD_" + str(user_id), user_id, total_amount, "paid"))

        order_id = cursor.lastrowid

        for item in items:
            db.execute("""
            INSERT INTO order_items (order_id, book_id, bookTitle, price, qty)
            VALUES (?, ?, ?, ?, ?)
            """, (
                order_id,
                item["book_id"],
                item["title"],
                item["price"],
                item["qty"]
            ))

        return order_id

    @staticmethod
    def get_orders_by_user(user_id):
        return db.query("""
        SELECT * FROM orders WHERE user_id = ?
        """, (user_id,))

    @staticmethod
    def get_items(order_id):
        return db.query("""
        SELECT * FROM order_items WHERE order_id = ?
        """, (order_id,))

    @staticmethod
    def delete(order_id):
        db.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
        db.execute("DELETE FROM orders WHERE id = ?", (order_id,))


#Categories

class CategoryDAO:

    @staticmethod
    def create(name):
        db.execute("INSERT INTO categories (name) VALUES (?)", (name,))

    @staticmethod
    def get_all():
        return db.query("SELECT * FROM categories")

    @staticmethod
    def delete(category_id):
        db.execute("DELETE FROM categories WHERE id = ?", (category_id,))




# Samples
# add new user
UserDAO.create("tom", "hashed_pw")

# add new book
BookDAO.create({
    "title": "Python 101",
    "price": 29.9,
    "file_path": "books/python.pdf"
})

# add to cart
CartDAO.add(user_id=1, book_id=1, qty=1)

# check cart
print(CartDAO.get_by_user(1))

# creat orders
items = [
    {"book_id": 1, "title": "Python 101", "price": 29.9, "qty": 1}
]
OrderDAO.create_order(1, items, 29.9)