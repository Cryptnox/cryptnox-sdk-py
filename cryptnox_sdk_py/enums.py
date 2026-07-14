# -*- coding: utf-8 -*-
"""
Enum classes used by the module
"""

from enum import (
    Enum,
    IntEnum
)


class AuthType(Enum):
    """
    Predefined values for authentication type.
    """
    NO_AUTH = 0
    PIN = 1
    USER_KEY = 2

    def __bool__(self):
        return self != AuthType.NO_AUTH


class Derivation(IntEnum):
    """
    Predefined values to use for parameters as Derivation.
    """
    CURRENT_KEY = 0x00
    DERIVE = 0x01
    DERIVE_AND_MAKE_CURRENT = 0x02
    PINLESS_PATH = 0x03


class KeyType(IntEnum):
    """
    Predefined values to use for parameters as KeyType.
    """
    K1 = 0x00
    R1 = 0x10
    ED25519 = 0x20


class Origin(Enum):
    """
    Predefined values for keeping the origin of the card
    """
    UNKNOWN = 0
    ORIGINAL = 1
    FAKE = 2


class SlotIndex(IntEnum):
    """
    Predefined values to use for parameters as SlotIndex.
    """
    EC256R1 = 0x01
    RSA = 0x02
    FIDO = 0x03


class SeedSource(Enum):
    """
    Predefined values for how seed was created
    """
    NO_SEED = 0x00
    SINGLE = ord("K")
    EXTENDED = ord("X")
    EXTERNAL = ord("L")
    INTERNAL = ord("S")
    DUAL = ord("D")
    WRAPPED = ord("R")
