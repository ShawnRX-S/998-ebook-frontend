"""Client demo that talks to a running FastAPI server over HTTP.

Start server first:
    uvicorn main:app --reload

Then run:
    python client_api_demo.py
"""

import base64

import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from client.ot_receiver import OTReceiver


BASE_URL = "http://127.0.0.1:8000"


def b64_decode(data: str) -> bytes:
    return base64.b64decode(data.encode("utf-8"))


def main():
    catalog = requests.get(f"{BASE_URL}/api/books/catalog", timeout=10).json()
    print("Catalog:", [(b["index"], b["title"]) for b in catalog["books"]])

    # Change this locally. Do not send this value to the server.
    choice_index = 1
    print("Local choice_index:", choice_index)

    session = requests.post(
        f"{BASE_URL}/api/ot/session",
        json={"group_id": "default"},
        timeout=10,
    ).json()

    receiver = OTReceiver(choice_index=choice_index, level_count=session["l"])

    for level in range(session["l"]):
        h0, h1 = receiver.start_level(level)
        step = requests.post(
            f"{BASE_URL}/api/ot/step",
            json={
                "session_id": session["session_id"],
                "level": level,
                "h0": h0,
                "h1": h1,
            },
            timeout=10,
        ).json()
        receiver.finish_level(level, b64_decode(step["c0"]), b64_decode(step["c1"]), step["gy"])

    masked_keys = [b64_decode(x) for x in session["masked_keys"]]
    aes_key = receiver.recover_key(masked_keys)

    package = requests.get(f"{BASE_URL}/api/books/encrypted-package/default", timeout=10).json()
    selected = package["books"][choice_index]
    plaintext = AESGCM(aes_key).decrypt(
        b64_decode(selected["nonce"]),
        b64_decode(selected["ciphertext"]) + b64_decode(selected["tag"]),
        None,
    )

    print("Decrypted:", selected["filename"])
    print(plaintext.decode("utf-8", errors="replace"))

    requests.post(
        f"{BASE_URL}/api/ot/session/clear",
        json={"session_id": session["session_id"]},
        timeout=10,
    )


if __name__ == "__main__":
    main()
