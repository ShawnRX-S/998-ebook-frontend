"""Small helper functions used by OT and masking."""


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte strings up to the shorter length."""
    return bytes(x ^ y for x, y in zip(a, b))


def int_to_bitlist(n: int, length: int) -> list[int]:
    """Convert integer n into a fixed-length big-endian bit list."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if length < 0:
        raise ValueError("length must be non-negative")
    return list(map(int, format(n, "b").zfill(length)))


def next_power_of_two(n: int) -> int:
    """Return the next power of two greater than or equal to n."""
    if n <= 1:
        return 1
    return 1 << (n - 1).bit_length()
