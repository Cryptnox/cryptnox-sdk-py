=========
Changelog
=========

Version 1.0.5 - 2026-07-14
------------------------------------------------------------------------------------------------

Added
^^^^^^^

- Added Ed25519 (EdDSA) signing support for applet v2.0 (``KeyType.ED25519``)
- Added ``examples/solana_transaction/`` demonstrating Solana signing and transaction building

Changed
^^^^^^^

- Renamed ``BasicG1`` card class to ``Basic`` (``BasicG1`` kept as a backwards-compatible alias)
- Padded the SIGN PIN to the spec's fixed 9-byte field and replaced SIGN magic numbers with named constants
- Replaced hardcoded PINs in examples with a named PIN variable

Fixed
^^^^^^^

- Guarded Ed25519 key handling against silently falling through to the ECDSA path (unknown key types now raise)

Version 1.0.4 - 2026-04-10
------------------------------------------------------------------------------------------------

Security
^^^^^^^^

- Block ``change_puk()`` when PIN is locked (FINDING-009)
- Pinned vulnerable transitive dev dependencies to safe minimum versions:

  - ``protobuf >= 5.29.6`` (GHSA-7gcm-g887-7qv7, CVSS 8.2)
  - ``python-multipart >= 0.0.22`` (GHSA-59g5-xgcq-4qw3 / GHSA-wp53-j4wj-2cfg, CVSS 8.7/8.6)
  - ``zipp >= 3.19.1`` (GHSA-jfmj-5v4g-7637, CVSS 6.9)

Fixed
^^^^^^^

- Fixed ``verify_pin(None)`` to return 0 when PIN is blocked instead of raising an exception
- Resolved PIN exception handling in BasicG1 card

Changed
^^^^^^^

- Updated ``PinBlockedException`` message for clarity
- Updated ``python_requires`` to ``>=3.11`` (removed upper bound, Python 3.14 now supported)
- Updated README with supported hardware details
- Updated docs configuration with SEO meta tags, favicon, and project details

Added
^^^^^^^

- Added ``examples/README.md`` with overview of available examples and run instructions

CI
^^^

- Fixed OSV-Scanner workflow to scan resolved installed package versions
- Pinned OSV-Scanner action to ``v2.3.5`` for reproducible CI builds

Version 1.0.3 - 2025-12-24
------------------------------------------------------------------------------------------------

Added
^^^^^^^

- Added ``get_manufacturer_certificate()`` method to Base card class with ``hexed`` parameter for flexible certificate retrieval

Changed
^^^^^^^

- Updated ``get_manufacturer_certificate()`` in BasicG1 with multi-page APDU support for full certificate retrieval
- Updated ``manufacturer_certificate()`` function in authenticity module to use the new card-specific method

Version 1.0.2 - 2025-12-08
------------------------------------------------------------------------------------------------

Changes
^^^^^^^

- Updated dependencies to resolve security vulnerabilities
- Improved Python 3 compatibility in cryptographic utilities

Added
^^^^^^^

- Implemented Python code quality scanning CI/CD pipeline using flake8
- Implemented security vulnerability scanning CI/CD pipeline using OSV-Scanner
- Added automated dependency security checks in GitHub Actions workflows

Fixed
^^^^^^^

- Fixed ``AttributeError: module 'cryptnox_sdk_py.cryptos.py2specials' has no attribute 'is_python2'`` error
- Fixed ``TypeError: can't concat str to bytes`` error in ``encode_pubkey()`` function
- Resolved info command issue that prevented retrieving card information
- Fixed Python 3.12 compatibility issues in ``py2specials.py`` module
  - Added proper Python 3 implementation for base 256 encoding/decoding
  - Fixed bytes/string handling in cryptographic operations

Version 1.0.1 - 2025-11-18
------------------------------------------------------------------------------------------------

Changes
^^^^^^^

- Package renamed from ``cryptnoxpy`` to ``cryptnox_sdk_py``
  - All imports must be updated from ``import cryptnoxpy`` to ``import cryptnox_sdk_py``
  - Install using: ``pip install cryptnox-sdk-py``
- Updated README.md with new package name and improved examples
- Updated valid PUK validation logic
- Updated GitHub Actions workflows for documentation and CI/CD
- Modified setup configuration (setup.cfg) for better package management

Added
^^^^^^^

- Added flake8 code quality checks to CI/CD workflow
- Added Sphinx documentation framework
- Implemented ``disconnect()`` method for Connection class to properly close connections
- Added comprehensive exception handling improvements

Fixed
^^^^^^^

- Fixed card not recognized error
- Resolved PUK retries persistence issue
- Fixed flake8 code style errors throughout the codebase

Removed
^^^^^^^

- Removed basic G0 cards references (no longer supported)
- Removed factory hashlib codes
