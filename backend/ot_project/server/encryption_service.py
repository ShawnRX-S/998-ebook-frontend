from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os


# ===== stimulate DB（need to update with the real database）=====
def load_books_from_db(folder_path):
    """
    return: list[dict]
    [
        {
            "book_id": "0000",
            "filename": "book1.pdf",
            "data": bytes
        }
    ]
    """
    books = []

    for idx, filename in enumerate(sorted(os.listdir(folder_path))):
        if filename.endswith(".pdf"):
            path = os.path.join(folder_path, filename)

            with open(path, "rb") as f:
                books.append({
                    "book_id": f"{idx:04}",
                    "filename": filename,
                    "data": f.read()
                })

    return books


# ===== AES encryption（each book from db）=====
def encrypt_book(data: bytes, key: bytes):
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)

    return {
        "nonce": cipher.nonce,
        "ciphertext": ciphertext,
        "tag": tag
    }


# =====  core（copy books, create keys, encryted book list）=====
def prepare_encrypted_books(folder_path):
    """
    return:
        encrypted_books: list[dict]
        book_keys: dict[book_id -> key]
    """

    books = load_books_from_db(folder_path)

    encrypted_books = []
    book_keys = {}

    for book in books:
        key = get_random_bytes(32)

        enc = encrypt_book(book["data"], key)

        encrypted_books.append({
            "book_id": book["book_id"],
            "filename": book["filename"],
            "nonce": enc["nonce"],
            "ciphertext": enc["ciphertext"],
            "tag": enc["tag"]
        })

        book_keys[book["book_id"]] = key

    return encrypted_books, book_keys