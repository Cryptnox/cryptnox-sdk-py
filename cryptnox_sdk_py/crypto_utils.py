# -*- coding: utf-8 -*-
"""
Module containing cryptographic methods used by the library
"""

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def aes_encrypt(key: bytes, initialization_vector: bytes, data: bytes) -> bytes:
    """
    AES encrypt data using key and initialization vector.

    :param bytes key: Key to use for encryption
    :param bytes initialization_vector: Initialization vector
    :param bytes data: Data to encrypt

    :return: Encrypted data
    :rtype: bytes
    """
    # AES-CBC is required by the SCP03 smartcard protocol; authentication is handled via separate MAC
    # nosemgrep: python.cryptography.security.mode-without-authentication.crypto-mode-without-authentication
    cipher = Cipher(algorithms.AES(key), modes.CBC(initialization_vector),
                    backend=default_backend())
    encryptor = cipher.encryptor()
    result = encryptor.update(data) + encryptor.finalize()

    return result


def aes_decrypt(key: bytes, initialization_vector: bytes, data: bytes) -> bytes:
    """
    AES decrypt data using key and initialization vector.

    :param bytes key: Key to use for encryption
    :param bytes initialization_vector: Initialization vector
    :param bytes data: Data to decrypt

    :return: Decrypted data
    :rtype: bytes
    """
    # AES-CBC is required by the SCP03 smartcard protocol; authentication is handled via separate MAC
    # nosemgrep: python.cryptography.security.mode-without-authentication.crypto-mode-without-authentication
    cipher = Cipher(algorithms.AES(key), modes.CBC(initialization_vector),
                    backend=default_backend())
    decryptor = cipher.decryptor()
    result = decryptor.update(data) + decryptor.finalize()

    return result
