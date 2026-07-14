#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solana Transaction Signing Example with Cryptnox Card

This example demonstrates how to:
1. Derive the Ed25519 public key from the card (applet v2.0+)
2. Compute the Solana address (base58 of the raw 32-byte key - no hashing)
3. Fetch a recent blockhash from a Solana JSON-RPC endpoint
4. Build a System-Program transfer message with solders
5. Send the raw message bytes to the card for signing (Ed25519 is *pure* - the
   card hashes internally, so the full message is signed, not a pre-hash)
6. Assemble the 64-byte signature onto the message and broadcast it

Requirements:
    pip install solders base58 requests cryptnox-sdk-py

Usage:
    python solana_transaction.py --pin 1234 --destination <base58-address> --amount 0.001

Note: This example requires a Cryptnox card with applet v2.0+ and a seed loaded.
      It defaults to devnet - airdrop test SOL to the shown address first:
      https://faucet.solana.com
"""

import base64
import sys
from typing import Any, Dict, Optional

try:
    import base58
    import requests
    from solders.hash import Hash
    from solders.message import Message
    from solders.pubkey import Pubkey
    from solders.signature import Signature
    from solders.system_program import TransferParams, transfer
    from solders.transaction import Transaction
    SOLANA_AVAILABLE = True
    SOLANA_IMPORT_WARNING: Optional[str] = None
except ImportError:
    SOLANA_AVAILABLE = False
    SOLANA_IMPORT_WARNING = ("Warning: solders/base58 not installed. Install with: "
                             "pip install solders base58 requests")

# Cryptnox SDK
try:
    import cryptnox_sdk_py
    from cryptnox_sdk_py.enums import Derivation, KeyType
    CRYPTNOX_AVAILABLE = True
    CRYPTNOX_IMPORT_WARNING: Optional[str] = None
except ImportError:
    CRYPTNOX_AVAILABLE = False
    CRYPTNOX_IMPORT_WARNING = ("Warning: cryptnox-sdk-py not installed. "
                               "Install with: pip install cryptnox-sdk-py")


# =============================================================================
# Solana Constants
# =============================================================================

# Solana derivation path used by Phantom and most wallets (all-hardened SLIP-0010)
SOLANA_DERIVATION_PATH = "m/44'/501'/0'/0'"

# 1 SOL = 1 000 000 000 lamports
LAMPORTS_PER_SOL = 1_000_000_000

DEVNET_URL = "https://api.devnet.solana.com"
TESTNET_URL = "https://api.testnet.solana.com"
MAINNET_URL = "https://api.mainnet-beta.solana.com"


# =============================================================================
# Address Derivation
# =============================================================================

def public_key_to_solana_address(public_key_hex: str) -> str:
    """
    Derive a Solana address from a raw Ed25519 public key.

    Unlike Bitcoin/Ethereum/XRP, a Solana address is *not* a hash of the public
    key: it is simply the base58 encoding of the raw 32-byte Ed25519 key.

    Args:
        public_key_hex: Raw 32-byte Ed25519 public key as hex (64 chars)

    Returns:
        Base58 Solana address
    """
    return base58.b58encode(bytes.fromhex(public_key_hex)).decode()


# =============================================================================
# Solana JSON-RPC Helpers
# =============================================================================

def _rpc(url: str, method: str, params: list) -> Any:
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    response = requests.post(url, json=payload, timeout=20)
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        raise RuntimeError(data["error"].get("message", "Solana RPC error"))
    return data["result"]


def get_balance(url: str, address: str) -> int:
    """Return the balance of *address* in lamports."""
    result = _rpc(url, "getBalance", [address])
    return result["value"]


def get_latest_blockhash(url: str) -> str:
    """Return a recent blockhash as a base58 string."""
    result = _rpc(url, "getLatestBlockhash", [{"commitment": "finalized"}])
    return result["value"]["blockhash"]


def send_transaction(url: str, transaction: "Transaction") -> str:
    """Broadcast a signed transaction (base64) and return its signature string."""
    encoded = base64.b64encode(bytes(transaction)).decode()
    return _rpc(url, "sendTransaction", [encoded, {"encoding": "base64"}])


# =============================================================================
# Transaction Building
# =============================================================================

def build_transfer_message(from_public_key_hex: str, to_address: str, lamports: int,
                           recent_blockhash: str) -> "Message":
    """
    Build a System-Program transfer message with the sender as fee-payer.

    ``bytes(message)`` are exactly what the card signs.
    """
    from_pubkey = Pubkey.from_bytes(bytes.fromhex(from_public_key_hex))
    to_pubkey = Pubkey.from_string(to_address)
    instruction = transfer(TransferParams(from_pubkey=from_pubkey, to_pubkey=to_pubkey,
                                          lamports=lamports))
    blockhash = Hash.from_string(recent_blockhash)
    return Message.new_with_blockhash([instruction], from_pubkey, blockhash)


def assemble_transaction(message: "Message", signature: bytes) -> "Transaction":
    """Graft a card-produced 64-byte signature onto a message."""
    return Transaction.populate(message, [Signature.from_bytes(signature)])


# =============================================================================
# Cryptnox Card Helpers
# =============================================================================

def get_public_key_from_card(card, derivation_path: str = SOLANA_DERIVATION_PATH) -> str:
    """
    Get the raw 32-byte Ed25519 public key from the card as hex.

    ``compressed=False`` is required: Ed25519 keys must never be run through the
    secp256k1/r1 compression path.
    """
    return card.get_public_key(
        derivation=Derivation.DERIVE,
        key_type=KeyType.ED25519,
        path=derivation_path,
        compressed=False
    )


def sign_with_card(card, message_bytes: bytes, path: str = SOLANA_DERIVATION_PATH,
                   pin: str = "") -> bytes:
    """
    Sign the raw message bytes with the card, returning a 64-byte Ed25519
    signature. Ed25519 is pure: the *entire* message is sent, not a pre-hash.
    """
    return card.sign(
        data=message_bytes,
        derivation=Derivation.DERIVE,
        key_type=KeyType.ED25519,
        path=path,
        pin=pin
    )


def verify_signature(public_key_hex: str, message_bytes: bytes, signature: bytes) -> bool:
    """
    Verify the card's Ed25519 signature over the original message bytes using
    PyNaCl, when available. Returns False if PyNaCl is not installed.
    """
    try:
        from nacl.signing import VerifyKey
        from nacl.exceptions import BadSignatureError
    except ImportError:
        return False

    try:
        VerifyKey(bytes.fromhex(public_key_hex)).verify(message_bytes, signature)
        return True
    except BadSignatureError:
        return False


# =============================================================================
# Main Example
# =============================================================================

def run_solana_transaction_example(
    pin: str = "",
    destination: str = "",
    amount_sol: float = 0.001,
    debug: bool = False,
    url: str = DEVNET_URL
) -> Optional[Dict[str, Any]]:
    """Run a complete Solana native-SOL transfer signing example."""
    if not SOLANA_AVAILABLE:
        print("Error: solders/base58 libraries are required. "
              "Install with: pip install solders base58 requests")
        return None

    if not CRYPTNOX_AVAILABLE:
        print("Error: cryptnox-sdk-py library is required.")
        return None

    if not destination:
        print("Error: --destination is required.")
        return None

    connection = None

    try:
        print("=" * 60)
        print("Solana Transaction Signing with Cryptnox Card")
        print("=" * 60)
        print("\n[Step 1] Connecting to Cryptnox card...")

        connection = cryptnox_sdk_py.Connection(0, debug=debug)
        card = cryptnox_sdk_py.factory.get_card(connection, debug=debug)
        print(f"  ✓ Connected to card (Serial: {card.serial_number})")
        print(f"  → Applet version: {'.'.join(map(str, card.applet_version))}")

        if pin:
            print("  → Verifying PIN...")
            card.verify_pin(pin)
            print("  ✓ PIN verified")

        if not card.valid_key:
            print("  ✗ Error: Card does not have a seed loaded")
            return None

        # =====================================================================
        # Step 2: Get Ed25519 public key + Solana address
        # =====================================================================
        print("\n[Step 2] Getting Ed25519 public key from card...")
        print(f"  → Derivation path: {SOLANA_DERIVATION_PATH}")

        public_key_hex = get_public_key_from_card(card, SOLANA_DERIVATION_PATH)
        print(f"  ✓ Public key (32 bytes): {public_key_hex}")

        from_address = public_key_to_solana_address(public_key_hex)
        print(f"  ✓ Solana address: {from_address}")

        # =====================================================================
        # Step 3: Check balance
        # =====================================================================
        print(f"\n[Step 3] Fetching balance from {url}...")
        balance_lamports = get_balance(url, from_address)
        print(f"  → Balance: {balance_lamports / LAMPORTS_PER_SOL} SOL")

        lamports = int(amount_sol * LAMPORTS_PER_SOL)
        if balance_lamports < lamports + 5_000:
            print("  ✗ Error: Not enough funds (need amount + ~5000 lamports fee).")
            print("  ! Airdrop devnet SOL at: https://faucet.solana.com")
            return None

        # =====================================================================
        # Step 4: Build transfer message
        # =====================================================================
        print("\n[Step 4] Building System-Program transfer message...")
        blockhash = get_latest_blockhash(url)
        print(f"  → Recent blockhash: {blockhash}")

        message = build_transfer_message(public_key_hex, destination, lamports, blockhash)
        message_bytes = bytes(message)
        print(f"  ✓ Message ({len(message_bytes)} bytes)")
        if debug:
            print(f"    Message (hex): {message_bytes.hex()}")

        # =====================================================================
        # Step 5: Sign with the card (Ed25519, pure - full message)
        # =====================================================================
        print("\n[Step 5] Signing with Cryptnox card (Ed25519)...")
        signature = sign_with_card(card, message_bytes, SOLANA_DERIVATION_PATH, pin)
        print(f"  ✓ Received signature ({len(signature)} bytes)")
        if debug:
            print(f"    Signature (hex): {signature.hex()}")

        # =====================================================================
        # Step 6: Verify the signature locally (optional, PyNaCl)
        # =====================================================================
        print("\n[Step 6] Verifying signature against the public key...")
        if verify_signature(public_key_hex, message_bytes, signature):
            print("  [PASS] Signature verifies over the original message bytes!")
        else:
            print("  [SKIP/FAIL] PyNaCl not installed or signature invalid "
                  "(install with: pip install pynacl)")

        # =====================================================================
        # Step 7: Assemble + broadcast
        # =====================================================================
        print("\n[Step 7] Assembling and broadcasting transaction...")
        transaction = assemble_transaction(message, signature)
        tx_signature = send_transaction(url, transaction)

        cluster = "devnet" if url == DEVNET_URL else \
            "testnet" if url == TESTNET_URL else "mainnet-beta"
        print("\n" + "=" * 60)
        print("TRANSACTION BROADCAST")
        print("=" * 60)
        print(f"\nSignature: {tx_signature}")
        print(f"Explorer:  https://explorer.solana.com/tx/{tx_signature}?cluster={cluster}")

        return {
            "public_key": public_key_hex,
            "from_address": from_address,
            "destination": destination,
            "amount_sol": amount_sol,
            "signature": signature.hex(),
            "tx_signature": tx_signature,
        }

    except exceptions.AppletVersionException as e:
        print(f"\n✗ Error: {e}")
        print("  ! Solana signing requires a Cryptnox card with applet v2.0 or later.")
        return None
    except exceptions.ReaderException:
        print("\n✗ Error: Card reader not found")
        return None
    except exceptions.CardException as e:
        print(f"\n✗ Error: Card error - {e}")
        return None
    except exceptions.PinException:
        print("\n✗ Error: Invalid PIN code")
        return None
    except exceptions.SeedException:
        print("\n✗ Error: No seed on card. Please load a seed first.")
        return None
    except exceptions.CryptnoxException as e:
        print(f"\n✗ Error: {e}")
        return None
    except (ValueError, TypeError, RuntimeError, ImportError, requests.RequestException) as e:
        print(f"\n✗ Unexpected error: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return None
    finally:
        if connection:
            print("\n[Cleanup] Disconnecting from card...")
            connection.disconnect()
            print("  ✓ Disconnected")


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Solana Transaction Signing with Cryptnox Card",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send 0.001 SOL on devnet (default)
  python solana_transaction.py --pin 1234 --destination <base58-address>

  # Custom amount on testnet
  python solana_transaction.py --pin 1234 --destination <addr> --amount 0.01 --testnet

For more information, see README.md
        """
    )
    parser.add_argument("--pin", type=str, default="", help="Card PIN code")
    parser.add_argument("--destination", type=str, required=True,
                        help="Recipient's Solana address (base58, required)")
    parser.add_argument("--amount", type=float, default=0.001,
                        help="Amount to send in SOL (default: 0.001)")
    parser.add_argument("--testnet", action="store_true",
                        help="Use testnet instead of devnet")
    parser.add_argument("--mainnet", action="store_true",
                        help="Use mainnet-beta instead of devnet")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    endpoint = DEVNET_URL
    if args.testnet:
        endpoint = TESTNET_URL
    elif args.mainnet:
        endpoint = MAINNET_URL

    result = run_solana_transaction_example(
        pin=args.pin,
        destination=args.destination,
        amount_sol=args.amount,
        debug=args.debug,
        url=endpoint
    )

    if not result:
        sys.exit(1)
