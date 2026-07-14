# Solana Transaction Signing with Cryptnox Card

Sign Solana native-SOL transfers using a Cryptnox hardware card for secure key storage and **Ed25519 (EdDSA)** signing.

> **Requires applet v2.0+.** Ed25519 signing is only available on Cryptnox applet v2.0 and later. On older cards the SDK raises `AppletVersionException`.

## Requirements

| Component | Details |
|-----------|---------|
| **Hardware** | Cryptnox card with **applet v2.0+** + PC/SC smart card reader |
| **Python** | `pip install cryptnox-sdk-py solders base58 requests` |
| **Optional** | `pip install pynacl` (for local signature verification) |

## Quick Start

```bash
# Send 0.001 SOL on devnet (default)
python solana_transaction.py --pin 000000000 --destination <base58-address>

# Custom amount on testnet
python solana_transaction.py --pin 000000000 --destination <addr> --amount 0.01 --testnet
```

Airdrop test SOL to the shown address first at [faucet.solana.com](https://faucet.solana.com).

## How It Works

### Signing Flow

```
 1. Get Public Key       Cryptnox card, Ed25519, SLIP-0010 m/44'/501'/0'/0'
         |
 2. Derive Address       base58(raw 32-byte key)  — NO hashing (unlike BTC/ETH/XRP)
         |
 3. Fetch Blockhash      JSON-RPC getLatestBlockhash
         |
 4. Build Message        System-Program transfer, fee-payer = sender, recent blockhash
         |
 5. Sign with Card       Ed25519 (P2=0x03), returns raw 64-byte R|S signature
         |               (Ed25519 is *pure* — the card hashes the FULL message internally)
         |
 6. Verify (optional)    PyNaCl verifies the signature over the original message bytes
         |
 7. Assemble + Broadcast Transaction.populate(message, [signature]) -> sendTransaction
```

### Key Implementation Details

**Address is the raw key, base58-encoded.** A Solana address is *not* a hash of the public key — it is simply `base58(public_key_bytes)`. Call `get_public_key(..., compressed=False)` to get the raw 32-byte Ed25519 key.

**Ed25519 is a pure signature scheme.** Unlike ECDSA (where the host hashes the message and sends a 32-byte digest), Ed25519 hashes internally. The **entire transaction message** is sent to the card, which returns a **raw 64-byte `R|S`** signature (no DER, no `0x30` prefix). The SIGN command uses **P2 = 0x03** to select EdDSA.

**Applet version gate.** Ed25519 operations require applet v2.0+. The SDK checks `card.applet_version` and raises `AppletVersionException` on older cards before touching the wire.

## Step-by-Step Code

### 1. Connect and get the Ed25519 public key

```python
import cryptnox_sdk_py
from cryptnox_sdk_py import exceptions
from cryptnox_sdk_py.enums import Derivation, KeyType

connection = None
try:
    connection = cryptnox_sdk_py.Connection(0)
    card = cryptnox_sdk_py.factory.get_card(connection)

    # Replace with your card's PIN (this is the factory default, for demo only)
    PIN = "000000000"
    card.verify_pin(PIN)

    # Raw 32-byte Ed25519 key (compressed=False is required)
    public_key = card.get_public_key(
        derivation=Derivation.DERIVE,
        key_type=KeyType.ED25519,
        path="m/44'/501'/0'/0'",
        compressed=False,
    )
except exceptions.AppletVersionException:
    raise SystemExit("Ed25519 requires a Cryptnox card with applet v2.0+")
except exceptions.CryptnoxException as error:
    raise SystemExit(f"Card error: {error}")
finally:
    if connection:
        connection.disconnect()
```

> The card calls (`verify_pin`, `get_public_key`, `sign`) all raise
> `exceptions.CryptnoxException` subclasses — wrap them as above. See
> `solana_transaction.py` for the full end-to-end handling.

### 2. Derive the Solana address

```python
import base58

address = base58.b58encode(bytes.fromhex(public_key)).decode()
```

### 3. Build the transfer message

```python
from solders.hash import Hash
from solders.message import Message
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer

from_pubkey = Pubkey.from_bytes(bytes.fromhex(public_key))
to_pubkey = Pubkey.from_string("RECIPIENT_ADDRESS")
ix = transfer(TransferParams(from_pubkey=from_pubkey, to_pubkey=to_pubkey, lamports=1_000_000))
message = Message.new_with_blockhash([ix], from_pubkey, Hash.from_string(recent_blockhash))
message_bytes = bytes(message)      # <-- exactly what the card signs
```

### 4. Sign with the card (full message, not a hash)

```python
signature = card.sign(
    data=message_bytes,
    derivation=Derivation.DERIVE,
    key_type=KeyType.ED25519,
    path="m/44'/501'/0'/0'",
)
# signature is a raw 64-byte R|S value
```

### 5. Assemble and broadcast

```python
from solders.signature import Signature
from solders.transaction import Transaction

tx = Transaction.populate(message, [Signature.from_bytes(signature)])
# base64-encode bytes(tx) and submit via JSON-RPC sendTransaction
```

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--pin` | (empty) | Card PIN code |
| `--destination` | (required) | Recipient Solana address (base58) |
| `--amount` | 0.001 | Amount in SOL |
| `--testnet` | false | Use testnet instead of devnet |
| `--mainnet` | false | Use mainnet-beta instead of devnet |
| `--debug` | false | Verbose output |

## Verification

Step 6 of the example verifies the card's signature locally with PyNaCl:

1. Loads the raw 32-byte Ed25519 public key as a `VerifyKey`
2. Verifies the 64-byte signature over the **original message bytes** (not a hash)

Output: `[PASS] Signature verifies over the original message bytes!`

This also confirms the DERIVE-mode path handling: the card must sign the original message, not the message with the derivation path bytes appended.

## Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `AppletVersionException` | Card applet older than v2.0 | Use a v2.0+ card; Ed25519 is unavailable on older applets |
| `Not enough funds` | Balance below amount + fee | Airdrop at [faucet.solana.com](https://faucet.solana.com) |
| `Invalid data received during signature` | Card did not return a 64-byte signature | Confirm applet v2.0 EdDSA support (P2=0x03) |
| `ReaderException` | No card reader | Connect a PC/SC reader |
| `SeedException` | No seed on card | Initialize card with a seed |

## License

Part of the Cryptnox SDK. See repository root for license terms.
