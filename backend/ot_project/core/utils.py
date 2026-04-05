# core/utils.py
#use for XOR a,b
def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

#change int to bit list for later enc/dec
def int_to_bitlist(n, l):
    return list(map(int, format(n, 'b').zfill(l)))