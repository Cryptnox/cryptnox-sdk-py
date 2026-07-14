# -*- coding: utf-8 -*-
"""
Module containing all exceptions that Cryptnox SDK Python module can raise.
"""


class CryptnoxException(Exception):
    """Base exception for the class exceptions."""


class CardClosedException(Exception):
    """The card wasn't opened with PIN code or challenge-response"""


class CardException(CryptnoxException):
    """No card was detected in the card reader."""


class CardTypeException(CryptnoxException):
    """The detected card is not supported by this library"""


class CertificateException(CryptnoxException):
    """There was an issue with the certification"""


class ConnectionException(CryptnoxException):
    """An issue occurred in the communication with the reader"""


class DataException(CryptnoxException):
    """The reader returned an empty message."""


class DataValidationException(CryptnoxException):
    """The sent data is not valid."""


class DerivationSelectionException(CryptnoxException):
    """Not a valid derivation selection."""


class KeySelectionException(CryptnoxException):
    """Not a valid key type selection"""


class AppletVersionException(CryptnoxException):
    """The card applet version is too old for the requested operation."""


class FirmwareException(CryptnoxException):
    """There is an issue with the firmware on the card"""


class GenuineCheckException(CryptnoxException):
    """The detected card is not a genuine Cryptnox product."""


class GenericException(CryptnoxException):
    """
    Generic exception that can mean multiple things depending on the call to the card

    Process stats and throw a specific Exception from it.
    """

    def __init__(self, status: bytes):
        self.status = status


class InitializationException(CryptnoxException):
    """The card hasn't been initialized."""


class KeyAlreadyGenerated(CryptnoxException):
    """Key can not be generated twice."""


class SeedException(CryptnoxException):
    """Keys weren't found on the card."""


class KeyGenerationException(CryptnoxException):
    """Error in key generation."""


class PinAuthenticationException(CryptnoxException):
    """Error in turning off PIN authentication. There is no user key in the card"""


class PinBlockedException(CryptnoxException):
    """PIN is locked. Use the unlock_pin command to unlock it before attempting this operation."""


class PinException(CryptnoxException):
    """
    Sent PIN code is not valid.

    :param int number_of_retries: Number of retries to send the PIN code
                                  before the card is locked.
    :param str message: Optional message
    """

    def __init__(self, message: str = "Invalid PIN code was provided", number_of_retries: int = 0):
        super().__init__(message)

        self.number_of_retries = number_of_retries


class PukException(CryptnoxException):
    """
    Sent PUK code is not valid.

    :param int number_of_retries: Number of retries to send the PIN code
                                  before the card is locked.
    :param str message: Optional message
    """

    def __init__(self, message: str = "Invalid PUK code was provided", number_of_retries: int = 0):
        super().__init__(message)

        self.number_of_retries = number_of_retries


class ReadPublicKeyException(CryptnoxException):
    """Data received during public key reading is not valid."""


class ReaderException(CryptnoxException):
    """Card reader wasn't found attached to the device."""


class SecureChannelException(CryptnoxException):
    """Secure channel couldn't be established."""


class SoftLock(CryptnoxException):
    """The card is soft locked, and requires power cycle before it can be opened"""


class CardNotBlocked(CryptnoxException):
    """Trying to unlock unblocked card"""
