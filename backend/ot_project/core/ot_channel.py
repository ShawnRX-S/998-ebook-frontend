# core/ot_channel.py
import random
import hashlib
from core.utils import xor_bytes
from core.config import P, G


class OTChannel:
     """
    Implements a simplified Diffie-Hellman based Oblivious Transfer (OT) protocol.

    This class defines the interaction between:
    - Receiver (client) → chooses a bit (0 or 1) without revealing it
    - Sender (server) → sends two encrypted messages (m0, m1)

    Security goal:
    - Receiver learns only one message (based on its choice bit)
    - Sender does not learn which message was chosen
    """
    def receiver_step1(self, bit):
        """
        Step 1 (Receiver → Sender)

        Receiver prepares Diffie-Hellman values.

        :param bit: receiver's choice (0 or 1)
        :return: (h0, h1, x)
            h0, h1: DH public values sent to sender
            x: secret exponent (kept by receiver)

        Logic:
        - Generate secret x
        - Compute h = g^x mod P
        - Place h in position corresponding to chosen bit
        - Other position is random (to hide choice)
        """
        x = random.randint(2, P - 2)     # secret exponent
        h = pow(G, x, P)                # DH public value

        if bit == 0:
            return h, random.randint(2, P - 2), x
        else:
            return random.randint(2, P - 2), h, x

    def sender_step2(self, m0, m1, h0, h1):
        """
        Step 1 (Receiver → Sender)

        Receiver prepares Diffie-Hellman values.

        :param bit: receiver's choice (0 or 1)
        :return: (h0, h1, x)
            h0, h1: DH public values sent to sender
            x: secret exponent (kept by receiver)

        Logic:
        - Generate secret x
        - Compute h = g^x mod P
        - Place h in position corresponding to chosen bit
        - Other position is random (to hide choice)
        """
        y = random.randint(2, P - 2)    # sender's secret


         # Diffie-Hellman shared keys
        k0 = pow(h0, y, P)
        k1 = pow(h1, y, P)

         # Diffie-Hellman shared keys
        k0_bytes = hashlib.sha256(str(k0).encode()).digest()[:len(m0)]
        k1_bytes = hashlib.sha256(str(k1).encode()).digest()[:len(m1)]

        # Derive symmetric keys via SHA256
        c0 = xor_bytes(m0, k0_bytes)
        c1 = xor_bytes(m1, k1_bytes)

        gy = pow(G, y, P)     # sender's public value

        return c0, c1, gy

    def receiver_step3(self, c0, c1, gy, x, bit):
        """
        Step 2 (Sender → Receiver)

        Sender encrypts both messages using DH-derived keys.

        :param m0: message 0 (bytes)
        :param m1: message 1 (bytes)
        :param h0, h1: values received from receiver
        :return: (c0, c1, gy)
            c0, c1: encrypted messages
            gy: DH public value

        Process:
        1. Generate secret y
        2. Compute shared keys:
            k0 = h0^y mod P
            k1 = h1^y mod P
        3. Hash keys to derive symmetric keys
        4. Encrypt messages using XOR
        """

         # Compute shared key
        k = pow(gy, x, P)

        # Derive symmetric key
        k_bytes = hashlib.sha256(str(k).encode()).digest()

        # Decrypt based on choice bit
        if bit == 0:
            return xor_bytes(c0, k_bytes[:len(c0)])
        else:
            return xor_bytes(c1, k_bytes[:len(c1)])