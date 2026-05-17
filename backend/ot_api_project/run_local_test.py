"""End-to-end local test without starting a real HTTP server.

It uses FastAPI TestClient to prove the API wrapper works and that the client
can recover exactly one selected book AES key, then decrypt that book.
"""

import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi.testclient import TestClient

from client.ot_receiver import OTReceiver
from main import app


def b64_decode(data: str) -> bytes:
    return base64.b64decode(data.encode("utf-8"))


def main():
    client = TestClient(app)

    catalog = client.get("/api/books/catalog").json()
    print("Catalog N:", catalog["N"])
    print("Books:", [(b["index"], b["title"]) for b in catalog["books"]])

    # Client chooses locally. This value is NEVER sent to the server.
    choice_index = min(2, catalog["N"] - 1)
    print("Local client choice_index:", choice_index)

    session = client.post("/api/ot/session", json={"group_id": "default"}).json()
    print("OT session created. l =", session["l"])

    receiver = OTReceiver(choice_index=choice_index, level_count=session["l"])

    for level in range(session["l"]):
        h0, h1 = receiver.start_level(level)
        response = client.post(
            "/api/ot/step",
            json={
                "session_id": session["session_id"],
                "level": level,
                "h0": h0,
                "h1": h1,
            },
        ).json()
        receiver.finish_level(
            level=level,
            c0=b64_decode(response["c0"]),
            c1=b64_decode(response["c1"]),
            gy=response["gy"],
        )

    masked_keys = [b64_decode(x) for x in session["masked_keys"]]
    recovered_aes_key = receiver.recover_key(masked_keys)
    print("Recovered AES key length:", len(recovered_aes_key), "bytes")

    package = client.get("/api/books/encrypted-package/default").json()
    encrypted_book = package["books"][choice_index]

    nonce = b64_decode(encrypted_book["nonce"])
    ciphertext = b64_decode(encrypted_book["ciphertext"])
    tag = b64_decode(encrypted_book["tag"])

    plaintext = AESGCM(recovered_aes_key).decrypt(nonce, ciphertext + tag, None)
    print("Decrypted filename:", encrypted_book["filename"])
    print("Decrypted content preview:", plaintext[:80].decode("utf-8", errors="replace"))

    client.post("/api/ot/session/clear", json={"session_id": session["session_id"]})
    print("SUCCESS: old OT core works through the API wrapper.")


if __name__ == "__main__":
    main()
