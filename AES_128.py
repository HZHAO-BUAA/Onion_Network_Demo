# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 14:24:46 2017

@author: Hzhao

AES-128 to encrypt private keys
"""

from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

class AES_128(object):
    def __init__(self, key):
        self.key = key.encode()
        self.mode = AES.MODE_CBC
        
    #encryption function, if len(plaintext) doesn't = n *16，then make up for to make sure the length = multiple of 16
    def encrypt(self, plaintext):
        encryptor = AES.new(self.key, self.mode, self.key)
        plaintext = plaintext.encode("utf-8")
        # The length of key should = 16 (AES-128）
        length = 16
        count = len(plaintext)
        add = length - (count % length)
        plaintext = plaintext + (b'\0' * add)
        self.ciphertext = encryptor.encrypt(plaintext)
        # Because output of AES encryption is not necessarily a string of ascii character set, maybe there will be 
        # a problem when we output it to the terminal or save, so we unified encrypted string into a hexadecimal string
        return b2a_hex(self.ciphertext).decode("ASCII")
    
        
    def decrypt(self, ciphertext):
        decryptor = AES.new(self.key, self.mode, self.key)
        plaintext = decryptor.decrypt(a2b_hex(ciphertext))
        return plaintext.rstrip(b'\0').decode("utf-8")
    
if __name__ == '__main__':
    pc = AES_128("keyskeyskeyskeyskeyskeyskeyskeys") # definition of the secret key of the private key
    e = pc.encrypt("1234567890987654321")
    d = pc.decrypt(e)
    print(e)
    print(d)
        