#!/usr/bin/python3
# -*-coding:Utf-8 -*-

# THIS MODULE NEED pycryptodome to work

from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA


# Symmetric cryptography using AES256
# Generates a key and an iv if none are provided to as an initialization argument
class CryptoAES:
    def __init__(self, key=None, iv=None):
        if key is None:
            self.key = get_random_bytes(32)
        else:
            self.key = key
        if iv is None:
            self.iv = get_random_bytes(16)
        else:
            self.iv = iv

    # Encrypts a character string or a bytes string using the key and the iv.
    # The ciphertext is returned as a chain of bytes
    def encrypt(self, plaintext):
        if type(plaintext) == str:
            plaintext = plaintext.encode("utf-8")
        cipher = AES.new(self.key, AES.MODE_CFB, iv=self.iv)
        return cipher.encrypt(plaintext)

    # Deciphers a character string or a bytes string using the key and the iv.
    # The plaintext is returned as a string of bytes
    def decrypt(self, cipher_text):
        if type(cipher_text) == str:
            cipher_text = cipher_text.encode("utf-8")
        cipher = AES.new(self.key, AES.MODE_CFB, iv=self.iv)
        return cipher.decrypt(cipher_text)


# Asymmetric cryptography using RSA with 2048 bits key
# Generates a key pair if the public key is not provided to as an initialization argument
# Only the public key can be exported using the export_pub_key() method
class CryptoRSA:
    def __init__(self, public_key=None):
        if public_key is None:
            self.__private_key = RSA.generate(2048)
            self.__public_key = self.__private_key.publickey()
        else:
            self.__public_key = RSA.import_key(public_key)
            self.__private_key = None

    # Export the public key as a bytes string
    def export_pub_key(self):
        return self.__public_key.export_key()

    # Encrypts a character string or a bytes string using the public key.
    # The ciphertext is returned as a chain of bytes
    def encrypt(self, plaintext):
        if type(plaintext) == str:
            plaintext = plaintext.encode("utf-8")
        cipher = PKCS1_OAEP.new(self.__public_key)
        return cipher.encrypt(plaintext)

    # Deciphers a string or a bytes string using the private key.
    # The plaintext is returned as a string of bytes
    def decrypt(self, cipher_text):
        if type(cipher_text) == str:
            cipher_text = cipher_text.encode("utf-8")
        if self.__private_key is None:
            print("ERROR : you don't have the private key needs to decrypt")
        else:
            cipher = PKCS1_OAEP.new(self.__private_key)
            return cipher.decrypt(cipher_text)
