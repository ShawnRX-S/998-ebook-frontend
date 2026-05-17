from server.book_storage_db_service import BookStorageDBService


def main():
    service = BookStorageDBService()

    print("=== Catalog Test ===")
    catalog = service.get_public_catalog("default")
    print("N:", catalog["N"])
    print("Books:")
    for book in catalog["books"]:
        print(book)

    print("\n=== AES Keys Test ===")
    keys = service.get_book_keys_for_group("default")
    print("Keys N:", len(keys))
    print("Key lengths:", [len(k) for k in keys])

    print("\n=== Encrypted Package Test ===")
    package = service.get_encrypted_group_package("default")
    print("Package N:", package["N"])
    print("First book:")
    print(package["books"][0])

    print("\nSUCCESS: DB storage service works.")


if __name__ == "__main__":
    main()