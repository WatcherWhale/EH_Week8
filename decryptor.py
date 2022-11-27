import sys
import base64

import hashlib
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES

def decrypt_file(file):
    with open(file) as encrypted_file:
        encrypted = encrypted_file.read().strip()

    enc_password = base64.b64decode(encrypted.split('.')[0])
    enc_bytes = encrypted.split('.')[1]

    dec_password = decrypt_rsa(enc_password)

    data_str = decrypt(enc_bytes, dec_password)
    data_bytes = base64.b64decode(data_str)

    with open(file + ".decrypted", "wb") as file:
        file.write(data_bytes)

def decrypt_rsa(data):
    with open("./keys/priv.key", "r") as file:
        private_key = file.read()

    private_key = RSA.importKey(private_key.encode())
    private_key = PKCS1_OAEP.new(private_key)

    return private_key.decrypt(data)

def decrypt(enc, password):
    private_key = hashlib.sha256(password).digest()
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    return unpad(cipher.decrypt(enc[16:]))

if __name__ == "__main__":
    decrypt_file(sys.argv[1])
