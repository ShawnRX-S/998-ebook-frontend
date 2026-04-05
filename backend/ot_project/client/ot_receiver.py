# client/ot_receiver.py
from core.utils import int_to_bitlist, xor_bytes
from core.prf import PRF


class OTReceiver:
    """
    OT Receiver (Client side)

    Responsibilities:
    1. Select a target index (choice_index)
    2. Perform OT protocol to obtain one key per level
    3. Reconstruct the mask using PRF
    4. Recover the correct book encryption key

    Security goal:
    - Receiver learns only the key for the chosen index
    - Server does not know which index was selected
    """

    def __init__(self, choice_index, l):
        """
        :param choice_index: index of the desired book
        :param l: number of bits (log2(N))

        Convert index → binary bits to guide OT choices
        """
        self.choice_index = choice_index 
        self.bits = int_to_bitlist(choice_index, l)   # binary path
        self.selected_keys = []                        # keys obtained via OT

    def obtain_keys(self, key_pairs, channel):
         """
        Perform OT protocol to obtain one key per bit.

        For each bit position j:
            - Choose k0 or k1 via OT
            - Only one key is learned
            - Server does not know which one

        :param key_pairs: list of (k0, k1) from server
        :param channel: OTChannel instance
        """
        for j, bit in enumerate(self.bits):

            # Step 1: Receiver sends (h0, h1)
            h0, h1, x = channel.receiver_step1(bit)
            
            # Server-side messages
            m0, m1 = key_pairs[j]
            
            # Step 2: Sender encrypts both messages
            c0, c1, gy = channel.sender_step2(m0, m1, h0, h1)
            
            # Step 3: Receiver decrypts only chosen message
            k = channel.receiver_step3(c0, c1, gy, x, bit)
            
            self.selected_keys.append(k)

    def recover_key(self, masked_keys):
        """
        Recover the final book key.

        Steps:
        1. Retrieve masked key Y_i from server
        2. Reconstruct mask using selected_keys
        3. Unmask to obtain original key

        :param masked_keys: list of masked keys from server
        :return: recovered book key (bytes)
        """
        # Step 1: get masked key
        Y = masked_keys[self.choice_index]

         # Step 2: rebuild mask
        mask = bytes(len(Y)) # initialize with zeros

        for key in self.selected_keys:
            prf = PRF(key, len(Y))
            mask = xor_bytes(mask, prf.eval(self.choice_index))

        # Step 3: recover original key
        return xor_bytes(Y, mask)