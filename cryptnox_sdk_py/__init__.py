# -*- coding: utf-8 -*-
"""
This is a library for communicating with Cryptnox cards

See the README.md for API details and general information.
"""
from .card.base import Base as Card
from .connection import Connection
from . import factory
from . import enums, exceptions
from .enums import SlotIndex, Derivation, KeyType, AuthType, SeedSource, Origin

__version__ = "1.0.5"

__all__ = [
    'Card',
    'Connection',
    'factory',
    '__version__',
    'enums',
    'exceptions',
    'SlotIndex',
    'Derivation',
    'KeyType',
    'AuthType',
    'SeedSource',
    'Origin'
]
