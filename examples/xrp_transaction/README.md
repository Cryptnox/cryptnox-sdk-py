# XRP Transaction Signing with Cryptnox Card

Sign XRP Ledger transactions using a Cryptnox hardware card for secure key storage and ECDSA signing.

## Requirements

| Component | Details |
|-----------|---------|
| **Hardware** | Cryptnox card (Basic G1 or NFT) + PC/SC smart card reader |
| **Python** | `pip install cryptnox-sdk-py xrpl-py` |

## Quick Start

```bash
# Sign a 1 XRP transaction
python xrp_transaction.py --pin 000000000 --destination rXXX...

# Custom amount
python xrp_transaction.py --pin 000000000 --destination rXXX... --amount 10.5
```

## How It Works

### Signing Flow

```
 1. Get Public Key       Cryptnox card, secp256k1, BIP44 m/44'/144'/0'/0/0
         |
 2. Derive XRP Address   SHA-256 -> RIPEMD-160 -> Base58Check = rXXX...
         |
 3. Fetch Sequence       Auto-query Testnet for current account sequence
         |
 4. Build TX JSON        Account (derived), Destination, Amount, Fee, Sequence
         |
 5. Encode for Signing   XRP binary codec + STX prefix + SigningPubKey
         |
 6. Hash                 SHA-512 first 32 bytes
         |
 7. Sign with Card       ECDSA secp256k1, returns canonical low-S DER signature
         |
 8. Insert into TX       TxnSignature + SigningPubKey -> encode -> tx_blob
         |
 9. Verify vs xrpl-py    Compare with official reference library
```

### Key Implementation Details

**Address is derived from the card.** The `Account` field is always derived from the card's public key. This is required because the XRP Ledger verifies that the signature matches the Account address.

**SigningPubKey must be in the signing data.** The XRP Ledger includes `SigningPubKey` in the serialized data before hashing. The transaction is encoded with `SigningPubKey` set, then hashed, then signed. This matches how `xrpl-py`'s `sign()` works internally.

**Signatures are canonical DER.** The Cryptnox card's SIGN command (P2=0x00) returns DER-encoded signatures with canonical low-S form (S ≤ curve_order / 2) per BIP-62. No additional normalization is needed.

**Sequence is auto-fetched.** When `--sequence` is 0 (default), the script queries the XRP Testnet to get the correct sequence number for the account.

## Step-by-Step Code

### 1. Connect and get public key

```python
import cryptnox_sdk_py
from cryptnox_sdk_py.enums import Derivation, KeyType

connection = cryptnox_sdk_py.Connection(0)
card = cryptnox_sdk_py.factory.get_card(connection)

# Replace with your card's PIN (this is the factory default, for demo only)
PIN = "000000000"
card.verify_pin(PIN)

# Derive to XRP path and get compressed public key
card.derive(key_type=KeyType.K1, path="m/44'/144'/0'/0/0")
public_key = card.get_public_key(
    derivation=Derivation.CURRENT_KEY, key_type=KeyType.K1, compressed=True
)
```

### 2. Derive XRP address

```python
from examples.xrp_transaction import public_key_to_xrp_address

address = public_key_to_xrp_address(public_key)
# "rsPZPCjBu8gSL3dqHQaoJXvVzz4GU1bc7u"
```

### 3. Build transaction

```python
tx = {
    "TransactionType": "Payment",
    "Account": address,       # Always derived from card public key
    "Destination": "RECIPIENT_ADDRESS",  # Recipient address
    "Amount": "1000000",      # 1 XRP in drops
    "Fee": "12",
    "Sequence": 14673550,     # from network or --sequence flag
}
```

### 4. Encode, hash, and sign

```python
from xrpl.core.binarycodec import encode_for_signing, encode
import hashlib

# Encode WITH SigningPubKey (critical!)
tx["SigningPubKey"] = public_key.upper()
signing_bytes = bytes.fromhex(encode_for_signing(tx))

# SHA-512 first 32 bytes
tx_hash = hashlib.sha512(signing_bytes).digest()[:32]

# Sign with card
signature = card.sign(data=tx_hash, derivation=Derivation.CURRENT_KEY, key_type=KeyType.K1)
```

### 5. Finalize

```python
from examples.xrp_transaction import insert_signature

# The card already returns canonical low-S DER (SIGN P2=0x00)
sig_hex = signature.hex().upper()

# Insert into transaction and generate tx_blob
signed_tx = insert_signature(tx, sig_hex, public_key)
tx_blob = encode(signed_tx)
```

### 6. Verify and submit

```python
from examples.xrp_transaction import verify_signature_with_xrpl

# Verify against xrpl-py reference
assert verify_signature_with_xrpl(tx, sig_hex, public_key)

# Submit
from xrpl.clients import JsonRpcClient
from xrpl.models import SubmitOnly

client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
response = client.request(SubmitOnly(tx_blob=tx_blob))
```

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--pin` | (empty) | Card PIN code |
| `--destination` | (required) | Recipient XRP address |
| `--amount` | 1.0 | Amount in XRP |
| `--sequence` | 0 (auto) | Account sequence (0 = fetch from network) |
| `--mainnet` | false | Query Mainnet instead of Testnet |
| `--debug` | false | Verbose output |

## Verification

Step 9 of the example compares the Cryptnox-generated signature against xrpl-py's reference ECDSA implementation:

1. Reconstructs the signing data (`encode_for_signing` with `SigningPubKey`)
2. Computes `sha512_first_half` (same as xrpl-py internally)
3. Verifies the DER signature using `ecpy.ecdsa.ECDSA` on secp256k1

Output: `[PASS] Signature matches xrpl-py reference`

## Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `Invalid signature` | Account doesn't match signing key | Address is auto-derived from card key |
| `Bad signature` | Wrong hash signed | SigningPubKey must be in signing data |
| `tefPAST_SEQ` | Stale sequence number | Use `--sequence 0` to auto-fetch |
| `terNO_ACCOUNT` | Account not funded | Fund at [XRP Faucet](https://xrpl.org/resources/dev-tools/xrp-faucets) |
| `ReaderException` | No card reader | Connect a PC/SC reader |
| `SeedException` | No seed on card | Initialize card with a seed |

## License

Part of the Cryptnox SDK. See repository root for license terms.
