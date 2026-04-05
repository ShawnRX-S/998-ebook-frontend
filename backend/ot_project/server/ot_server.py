# server/ot_server.py
import os
from core.utils import xor_bytes, int_to_bitlist
from core.prf import PRF


class OTServer:
     """
    OT Server component responsible for:
    1. Holding all book encryption keys (book_keys)
    2. Generating random key pairs for each OT layer
    3. Masking all book keys using PRF and XOR

    Security goal:
    - The server prepares masked keys for ALL books
    - The client can only recover ONE key via OT
    - The server does not know which key the client reconstructs
    """

    def __init__(self, book_keys):
         """
        :param book_keys: list of AES keys (bytes), one per book

        Example:
        book_keys[i] = AES key for book i
        """
        self.book_keys = book_keys
        self.N = len(book_keys)             # number of books
        self.key_len = len(book_keys[0])    # key length (e.g., 32 bytes for AES-256)

    def generate_key_pairs(self, l):
        """
        Generate OT key pairs for each level.

        :param l: number of bits (log2(N))
        :return: list of (k0, k1)

        Each level corresponds to one bit in the binary index.
        For each level:
            k0 = random key for bit 0
            k1 = random key for bit 1
        """
        key_pairs = []
        for _ in range(l):
            k0 = os.urandom(self.key_len)  # secure random key
            k1 = os.urandom(self.key_len)  # secure random key
            key_pairs.append((k0, k1)) 

        return key_pairs

    def compute_masked_keys(self, key_pairs):
        """
        Compute masked keys for ALL books.

        :param key_pairs: list of (k0, k1) per bit position
        :return: masked_keys (list of bytes)

        For each book index i:
            1. Convert i → binary bits
            2. For each bit position j:
                select key_pairs[j][bit]
                apply PRF(key, i)
                XOR into mask
            3. Final masked key:
                Y_i = book_key[i] XOR mask

        Result:
            masked_keys[i] = Y_i

        Security:
        - Only the correct combination of keys (from OT) can reconstruct the mask
        - Without all correct keys, the mask is incomplete → cannot recover book key
        """

        l = len(key_pairs)
        masked_keys = []

        # iterate over all books
        for i in range(self.N): 

            mask = bytes(self.key_len)   # initialize mask = 0...0

            # convert index i → binary representation
            bits = int_to_bitlist(i, l)

            # convert index i → binary representation
            for j, bit in enumerate(bits):

                # select corresponding key (k0 or k1)
                key = key_pairs[j][bit]

                # select corresponding key (k0 or k1)
                prf = PRF(key, self.key_len)

                # generate pseudo-random value
                mask = xor_bytes(mask, prf.eval(i))

             # apply mask to actual book key
            Y = xor_bytes(self.book_keys[i], mask)
            masked_keys.append(Y)

        return masked_keys