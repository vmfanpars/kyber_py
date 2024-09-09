import unittest
import os
import pytest
from kyber_py.kyber import Kyber512, Kyber768, Kyber1024, KYBER_K
from kyber_py.drbg.aes256_ctr_drbg import AES256_CTR_DRBG

def parse_kat_data(data):
    parsed_data = {}
    count_blocks = data.split("\n\n")
    for block in count_blocks[:-1]:
        block_data = block.split("\n")
        count, seed, pk, sk, ct, ss = [
            line.split(" = ")[-1] for line in block_data
        ]
        parsed_data[int(count)] = {
            "seed": bytes.fromhex(seed),
            "pk": bytes.fromhex(pk),
            "sk": bytes.fromhex(sk),
            "ct": bytes.fromhex(ct),
            "ss": bytes.fromhex(ss),
        }
    return parsed_data

class TestKyber(unittest.TestCase):
    """
    Test Kyber levels for internal consistency by generating keypairs and
    shared secrets.
    """

    def generic_test_kyber(self, Kyber, count):
        for _ in range(count):
            pk, sk = Kyber.keygen()
            for _ in range(count):
                key, c = Kyber.encaps(pk)

                # Correct decaps works
                _key = Kyber.decaps(sk, c)
                self.assertEqual(key, _key)

                # Incorrect ct does not work
                _bad_ct = bytes([0] * len(c))
                _bad = Kyber.decaps(sk, _bad_ct)
                self.assertNotEqual(key, _bad)

    def test_kyber512(self):
        self.generic_test_kyber(Kyber512, 5)

    def test_kyber768(self):
        self.generic_test_kyber(Kyber768, 5)

    def test_kyber1024(self):
        self.generic_test_kyber(Kyber1024, 5)

    def test_xof_failure(self):
        self.assertRaises(ValueError, lambda: Kyber512._xof(b"1", b"2", b"3"))

    def test_prf_failure(self):
        self.assertRaises(ValueError, lambda: Kyber512._prf(b"1", b"2", 32))

class TestKyberDeterministic(unittest.TestCase):
    """
    Ensure that deterministic DRBG is deterministic!

    Uses AES256 CTR DRBG for randomness.
    Note: requires pycryptodome for AES impl.
    (Seemed overkill to code my own AES for Kyber)
    """

    def generic_test_kyber_deterministic(self, Kyber, count):
        """
        First we generate five pk,sk pairs
        from the same seed and make sure
        they're all the same
        """
        seed = os.urandom(48)
        pk_output = []
        for _ in range(count):
            Kyber.set_drbg_seed(seed)
            pk, sk = Kyber.keygen()
            pk_output.append(pk + sk)
        self.assertEqual(len(pk_output), 5)
        self.assertEqual(len(set(pk_output)), 1)

        """
        Now given a fixed keypair make sure
        that c,key are the same for a fixed seed
        """
        key_output = []
        seed = os.urandom(48)
        pk, sk = Kyber.keygen()
        for _ in range(count):
            Kyber.set_drbg_seed(seed)
            key, c = Kyber.encaps(pk)
            _key = Kyber.decaps(sk, c)
            # Check key derivation works
            self.assertEqual(key, _key)
            key_output.append(c + key)
        self.assertEqual(len(key_output), count)
        self.assertEqual(len(set(key_output)), 1)

    def test_kyber512_deterministic(self):
        self.generic_test_kyber_deterministic(Kyber512, 5)

    def test_kyber768_deterministic(self):
        self.generic_test_kyber_deterministic(Kyber768, 5)

    def test_kyber1024_deterministic(self):
        self.generic_test_kyber_deterministic(Kyber1024, 5)

def data_parse(filename):
    # Set DRBG to generate seeds
    entropy_input = bytes([i for i in range(48)])
    rng = AES256_CTR_DRBG(entropy_input)

    with open(filename) as f:
        kat_data = f.read()
        parsed_data = parse_kat_data(kat_data)

    return [(rng.random_bytes(48), i) for i in parsed_data.values()]

@pytest.mark.parametrize(
    "Kyber, seed, data",
    [
        (kem, seed, param)
        for kem, filename in [
            (Kyber512, "assets/PQCkemKAT_1632.rsp"),
            (Kyber768, "assets/PQCkemKAT_2400.rsp"),
            (Kyber1024, "assets/PQCkemKAT_3168.rsp"),
        ]
        for seed, param in data_parse(filename)
    ],
    ids=[
        f"{kem}-test-{num}"
        for kem in ["Kyber512", "Kyber768", "Kyber1024"]
        for num in range(100)
    ],
)
def test_generic_kyber_known_answer(Kyber, seed, data):

    # Set the seed and check it matches the KAT
    assert seed == data["seed"]

    # Seed DRBG with KAT seed
    Kyber.set_drbg_seed(seed)

    # Assert keygen matches
    pk, sk = Kyber.keygen()
    assert pk == data["pk"]
    assert sk == data["sk"]

    # Assert encapsulation matches
    ss, ct = Kyber.encaps(pk)
    assert ss == data["ss"]
    assert ct == data["ct"]

    # Assert decapsulation matches
    _ss = Kyber.decaps(sk, ct)
    assert _ss == data["ss"]

if KYBER_K == 2:
    pk, sk= Kyber512.keygen()
    key, c = Kyber512.encaps(pk)
elif KYBER_K == 3:
    pk, sk= Kyber768.keygen()
    key, c = Kyber768.encaps(pk)
elif KYBER_K == 4:
    pk, sk= Kyber1024.keygen()
    key, c = Kyber1024.encaps(pk)
else:
    print("KYBER_K must be in {2, 3, 4}")

print(f"Public Key char: {(pk)}\n, sk = {len(sk)}, key = {len(key)}, c = {len(c)}")

# kyber = Kyber(DEFAULT_PARAMETERS["kyber_768"])
pk, sk= Kyber768.keygen()
key, c = Kyber768.encaps(pk)
print(f"kyber_768 -> pk = {len(pk)}, sk = {len(sk)}, key = {len(key)}, c = {len(c)}")

# kyber = Kyber(DEFAULT_PARAMETERS["kyber_1024"])
pk, sk= Kyber1024.keygen()
key, c = Kyber1024.encaps(pk)
print(f"kyber_1024 -> pk = {len(pk)}, sk = {len(sk)}, key = {len(key)}, c = {len(c)}")

_key = Kyber1024.decaps(sk, c)
print(f"kyber_1024 -> len(_key) = {len(_key)}, len(key) = {len(key)}")
print(f"kyber_1024 -> len(_key) = {(_key[:7])}, len(key) = {(key[:7])}")

pk , sk = Kyber1024._cpapke_keygen()
print("pk:!   ", len(pk), "  sk:   !   ", len(sk))

# pke = Public Key Encryption
sk_pke, pk_pke, pk_hash, z = Kyber1024._unpack_secret_key(sk)
print(f"kyber_1024 -> sk_pke = {len(sk_pke)}, pk_pke = {len(pk_pke)}, pk_hash = {len(pk_hash)}, z = {len(z)}")