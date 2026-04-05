# core/prf.py
import hashlib


class PRF:
     """
    Pseudo-Random Function (PRF) using SHA-256.

    This class generates deterministic pseudo-random outputs based on:
    - a secret key
    - an input value x

    In the OT protocol:
    - The key is derived from OT (k0/k1)
    - The input x is typically the book index
    - The output is used to construct a mask for encryption/decryption

    Output is truncated to a fixed length to match AES key size (e.g., 32 bytes).
    """
    def __init__(self, key, length):

        """
        Initialize PRF with:
        :param key: secret key (bytes)
        :param length: output length in bytes
        """

        self.key = key
        self.length = length

    def eval(self, x):
         """
        Evaluate the PRF at input x.

        :param x: integer input (e.g., book index)
        :return: pseudo-random bytes of specified length

        Process:
        1. Convert x → 2-byte big-endian format
        2. Concatenate with secret key
        3. Hash using SHA-256
        4. Truncate to desired length
        """
        
        return hashlib.sha256(
            self.key + x.to_bytes(2, 'big')
        ).digest()[:self.length]