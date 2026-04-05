# demo/run_demo.py
import os
import math

from server.ot_server import OTServer
from client.ot_receiver import OTReceiver
from core.ot_channel import OTChannel


def run_demo():
    print("=== OT Demo ===\n")

    N = 1024
    l = math.ceil(math.log2(N))

    book_keys = [os.urandom(32) for _ in range(N)]

    server = OTServer(book_keys)
    key_pairs = server.generate_key_pairs(l)
    masked_keys = server.compute_masked_keys(key_pairs)

    choice = 777

    receiver = OTReceiver(choice, l)
    channel = OTChannel()

    receiver.obtain_keys(key_pairs, channel)
    recovered_key = receiver.recover_key(masked_keys)

    print("Chosen index:", choice)
    print("Match:", recovered_key == book_keys[choice])


if __name__ == "__main__":
    run_demo()