import base64
import json
import os

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


CONFIG_ENCRYPTION_MARKER = "gits-config"
LEGACY_CONFIG_ENCRYPTION_MARKERS = {"gits-config-v1"}

PRIVATE_KEY_PEM = b"""-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDPzBeMd2oANHZY
qBXaLOXvpwg4DOxYLAOde78JoECi4C+A64aGPHxyjq5FWd6YAj+qL8DRcsO46Gva
bi3g9PMKfj5ZnluP6umqoLfrP29HPSqao4WaSo6vMaoWHrBVg+DS/zKQan7taQW8
LgW6YTOSSw9jtubNfIvl3loiYVdzJxMFWglT7kinRwdN8kiAkl5kgMWy+QXG/J7E
pJcfh5CZFy9QjnsrDcNs8VAzz08AxJGoP5+AZN+cqkuo358BJBxuyYZxxSH1Kt2K
INU64YOw4/qPGvzPpQBF9CuoqKcmcTUmzB9BvuIKEq4F5BvikpIKVtOF74sY+6kV
Ol32nDwxAgMBAAECggEAXnEp+sODP9iYOS8bz288ijFmQONOv7wxYHAPoXZeKiiu
Lm/dUkFHZmGGvypbSscq3FSb1BXO8slfy4TsASQTGh/KgrzAbKad0Nj+/kJ0dvJL
3MCZRkjAlMuDvE3yYstvcTZfatecHJbw7lgUbmMjJ0hKFE3alGYYxz7JxHptXn3/
gyhnOsy2tW7dqB2QvmUuKdMibvSpAFGiF3aWHdnrtI18iZv06wz0Pj3KfIqlwt5b
d3BPrPVm/2bBjK/uZcPd5wu65TyQ2rM9rDgPkMPWHbMGLu4qLJrLDbsACkcA8OCa
81US6XMxpicZA68k8GMWn97MkPiV+1qpqkwAGb9eyQKBgQD6PslWCtGJPfVew6kG
Kl2im1rG8QdCxYQIeRW1GwKbGSEjM/JLLKr5xtjV1Ryt6B5W5XoeNHasyK1NX8/R
WYQ4ZSYrtGtMWOdR4USNr2aFik5T2w7JKxEwTTZr3wGHG0BtqnRCKCjwC3NbWj8i
UCJb2c08s+np5JISpBd7QOorQwKBgQDUk2kglPgWUbRd9vJBvEbP1kUWnZRj0f0h
UAnpAorTCAEKAVf50lSy1A85UqNqBqaw1fTnTditjXrcvJhqGNkd45EmyQtUhnMo
Gpqv4G9dgPBXxUBK/xrjguiAOlqfVNVVb3N3siPDvm5gAK2vO36kWPRUsfikw3Be
YSLL1T4RewKBgAVz4MczLSWkZ/hMox4zRh8I641yKwpVa28T1FlB4Winv4UY2Kqy
qncO0iK2pg1UBXU3QtXtprhVFxGciNay8KKZ8Z76K2xac4/hLLE5pS47uUEygLv5
aEJ5LDplfY8IFPtOv4HBhkLUvQq8iKuiu1zs/f/Ym7ww8s3dLXXOEEwpAoGBAK6y
covvQS7+eI9cWd1CAKPfgKnEWOXr9e5Bm9NdXn9trYTuc8GAZFEOy3AdhOSmkKj1
PK42oKKIifcMGunef9f7ZBeO03vkfpDvxD5T4NHkHCDVny/DFPLya2auDjmw+x2a
WTd+M7wzLPxCsno3F62y2SEdnayyXQ+DHpiLJ9YvAoGAOEWdLnavTF5r8qp+omdF
5qjTF9789vqcS55y1k/otfHDwImeSFKNdZgadKl9X4bESxzjiZGn4kmpCP8AByMJ
ygPIul4ub11FIoWgNv1peiespCEY4dNMWQnWdfCiMw78gvFor5EaxQUc/h+uUtPs
D4C7qJb5GucvJRIgNFq29Gg=
-----END PRIVATE KEY-----"""

PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAz8wXjHdqADR2WKgV2izl
76cIOAzsWCwDnXu/CaBAouAvgOuGhjx8co6uRVnemAI/qi/A0XLDuOhr2m4t4PTz
Cn4+WZ5bj+rpqqC36z9vRz0qmqOFmkqOrzGqFh6wVYPg0v8ykGp+7WkFvC4FumEz
kksPY7bmzXyL5d5aImFXcycTBVoJU+5Ip0cHTfJIgJJeZIDFsvkFxvyexKSXH4eQ
mRcvUI57Kw3DbPFQM89PAMSRqD+fgGTfnKpLqN+fASQcbsmGccUh9SrdiiDVOuGD
sOP6jxr8z6UARfQrqKinJnE1JswfQb7iChKuBeQb4pKSClbThe+LGPupFTpd9pw8
MQIDAQAB
-----END PUBLIC KEY-----"""


def is_encrypted_config(value):
    return isinstance(value, dict) and value.get("type") in {
        CONFIG_ENCRYPTION_MARKER,
        *LEGACY_CONFIG_ENCRYPTION_MARKERS,
    }


def encrypt_config(config):
    plaintext = json.dumps(config, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    aes_key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)
    ciphertext = AESGCM(aes_key).encrypt(nonce, plaintext, None)

    public_key = serialization.load_pem_public_key(PUBLIC_KEY_PEM)
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    return {
        "type": CONFIG_ENCRYPTION_MARKER,
        "key": base64.b64encode(encrypted_key).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "data": base64.b64encode(ciphertext).decode("ascii"),
    }


def decrypt_config(encrypted_config):
    private_key = serialization.load_pem_private_key(PRIVATE_KEY_PEM, password=None)
    aes_key = private_key.decrypt(
        base64.b64decode(encrypted_config["key"]),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    plaintext = AESGCM(aes_key).decrypt(
        base64.b64decode(encrypted_config["nonce"]),
        base64.b64decode(encrypted_config["data"]),
        None,
    )
    return json.loads(plaintext.decode("utf-8"))
