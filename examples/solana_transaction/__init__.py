# -*- coding: utf-8 -*-
"""
Solana Transaction Signing Example

Demonstrates how to sign Solana (Ed25519) native-SOL transfers using a Cryptnox
hardware card (applet v2.0+) for secure key storage and signing.

Usage:
    python solana_transaction.py --pin YOUR_PIN --destination <base58-address>
"""

from .solana_transaction import (
    # Address derivation
    public_key_to_solana_address,
    # Network queries
    get_balance,
    get_latest_blockhash,
    send_transaction,
    # Transaction building
    build_transfer_message,
    assemble_transaction,
    # Card interaction
    get_public_key_from_card,
    sign_with_card,
    # Verification
    verify_signature,
    # Entry point
    run_solana_transaction_example,
)

__all__ = [
    "public_key_to_solana_address",
    "get_balance",
    "get_latest_blockhash",
    "send_transaction",
    "build_transfer_message",
    "assemble_transaction",
    "get_public_key_from_card",
    "sign_with_card",
    "verify_signature",
    "run_solana_transaction_example",
]
