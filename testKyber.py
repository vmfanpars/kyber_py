from kyber_py.kyber.kem import *
from kyber_py.kyber.duration import *
from kyber_py.kyber import __all__

print("<----------", __all__[KYBER_K-2], "---------->")

kyberLevel = {2: Kyber512, 3: Kyber768, 4: Kyber1024}
if KYBER_K in kyberLevel:
    kyber = kyberLevel[KYBER_K]
    pk, sk = kyber.keygen()
    key, c = kyber.encaps(pk)
    _key = kyber.decaps(sk, c)
else:
    print("KYBER_K must be in {2, 3, 4}")
n = 100
print()
print("keygen time:", keygenTime(kyber, n), " miliseconds\n")
print("encaps time:", encapsTime(kyber, pk, n), " miliseconds\n")
print("decaps time:", decapsTime(kyber, sk, c, n), " miliseconds")

pk_str = pk.decode(errors="ignore")
print(f"\nPublic Key char:\n{pk_str}")
print(f"len pk char= {len(pk)}")

print(f"\nPublic Key:\n{pk}")
print(f"len pk= {len(pk)}")
print(f"\nSecret Key:\n{sk}")
print(f"len sk= {len(sk)}")

print(f"\nCiphertext:\n{c}")
print(f"len sk= {len(c)}")
print(f"\nShared Secret A:\n{key}")
print(f"len ssa= {len(key)}")

print(f"\nShared Secret B:\n{_key}")
print(f"len ssa= {len(_key)}")

print("\nThe End")