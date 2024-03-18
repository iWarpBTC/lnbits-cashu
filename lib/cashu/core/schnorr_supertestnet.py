import hashlib
import time

from secp256k1 import PrivateKey, PublicKey

pk = PrivateKey(
    bytes.fromhex("8d7324709be0921acad49a8b65062153df85243e1358bf4308060678a426447e")
)
msg = (
    '["P2PK", {"data":'
    ' "020e8b47e763b9899292f861ed5d5d1d16507b7fdb4892bb2bf08470b628b5eecb", "nonce":'
    ' "f4ed43fda3223cbc645643d0979c1b07", "tags": [["locktime", "1707395502"],'
    ' ["sigflag", "SIG_ALL"]]}]'
)
msg = "hallo"
msg = (
    '["P2PK", {"data":'
    ' "020e8b47e763b9899292f861ed5d5d1d16507b7fdb4892bb2bf08470b628b5eecb", "nonce":'
    ' "4c194d04ed23309b528e51148c63db34", "tags": [["locktime", "1707398765"],'
    ' ["sigflag", "SIG_ALL"]]}]'
)

print("private key:")
print(pk.serialize())

print("pubkey:")
pubkey = pk.pubkey
assert pubkey
print(pubkey.serialize().hex())

print("message:")
print(msg)
print("message digest:")
digest = hashlib.sha256(msg.encode()).digest()
print(digest.hex())

sig = pk.schnorr_sign(digest, None, raw=True)
sig_hex = sig.hex()
print("signature:")
print(sig_hex)

sig = bytes.fromhex(
    "0f8c70778260937ab73cf008cfca090ab355b6d20bd89bafa38efc3a4fb788c2f2ca0fb0005c8145fb874f66e3abb5083ce4980f0a942e37dfb2cc510df787ad"
)

print(
    "Valid?",
    pubkey.schnorr_verify(msg=digest, schnorr_sig=sig, bip340tag=None, raw=True),
)

# res = []
# N = 2**16
# for i in range(N):
#     _hash = hashlib.sha256(str(i).encode("utf-8")).digest()
#     result = 0
#     try:
#         PublicKey(b"\x02" + _hash, raw=True)
#         result = 1
#     except Exception:
#         pass
#     res.append(result)
# print(f"Sum: {sum(res)}")
# print(f"Average: {sum(res) / N}")

DOMAIN_SEPARATOR = b"Secp256k1_HashToCurve_Cashu_"


def hash_to_curve_deprecated(message: bytes) -> PublicKey:
    """Generates a secp256k1 point from a message.

    The point is generated by hashing the message with a domain separator and then
    iteratively trying to compute a new point from the hash. An increasing uint32 counter
    (byte order little endian) is appended to the hash until a point is found that lies on the curve.

    The chance of finding a valid point is 50% for every iteration. The maximum number of iterations
    is 2**16. If no valid point is found after 2**16 iterations, a ValueError is raised (this should
    never happen in practice).

    The domain separator is b"Secp256k1_HashToCurve_Cashu_" or
    bytes.fromhex("536563703235366b315f48617368546f43757276655f43617368755f").
    """
    msg_to_hash = hashlib.sha256(DOMAIN_SEPARATOR + message).digest()
    counter = 0
    while True and counter < 2**16:
        _hash = hashlib.sha256(msg_to_hash + counter.to_bytes(4, "little")).digest()
        try:
            # will error if point does not lie on curve
            return PublicKey(b"\x02" + _hash, raw=True)
        except Exception:
            counter += 1
    # it should never reach this point
    raise ValueError("No valid point found")


def hash_to_curve(message: bytes) -> PublicKey:
    """Generates a point from the message hash and checks if the point lies on the curve.
    If it does not, iteratively tries to compute a new point from the hash."""
    point = None
    msg_to_hash = message
    while point is None:
        _hash = hashlib.sha256(msg_to_hash).digest()
        try:
            # will error if point does not lie on curve
            point = PublicKey(b"\x02" + _hash, raw=True)
        except Exception:
            msg_to_hash = _hash
    return point


start = time.time()
N = 2**17
for i in range(N):
    Y = hash_to_curve_deprecated(str(i).encode("utf-8"))

print(f"Took {time.time() - start} seconds for {N} iterations")


start = time.time()
N = 2**17
for i in range(N):
    Y = hash_to_curve(str(i).encode("utf-8"))

print(f"Took {time.time() - start} seconds for {N} iterations")
