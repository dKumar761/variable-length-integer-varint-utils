"""Core varint encoding and decoding functions.

This module implements protobuf-style base-128 varints. Unsigned integers are
encoded directly. Signed integers use zigzag encoding so that small negative
numbers also take few bytes.
"""

from typing import Tuple


class VarintError(ValueError):
    """Raised when a varint is malformed or cannot be decoded."""


def encode_varint(value: int) -> bytes:
    """Encode a non-negative integer as a protobuf-style varint.

    Args:
        value: The integer to encode. Must be >= 0.

    Returns:
        A bytes object containing the varint encoding.

    Raises:
        ValueError: If value is negative.
    """
    if value < 0:
        raise ValueError("encode_varint requires a non-negative integer")
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            break
    return bytes(out)


def decode_varint(data: bytes, offset: int = 0) -> Tuple[int, int]:
    """Decode a varint from a bytes-like object starting at offset.

    Args:
        data: The buffer to read from.
        offset: Starting index. Defaults to 0.

    Returns:
        A tuple (value, new_offset) where new_offset is the index just past the
        decoded varint.

    Raises:
        VarintError: If the varint is truncated or exceeds 64 bits (more than 10
            bytes with continuation bits set).
    """
    result = 0
    shift = 0
    pos = offset
    length = len(data)
    while True:
        if pos >= length:
            raise VarintError("truncated varint")
        byte = data[pos]
        pos += 1
        result |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            return result, pos
        shift += 7
        if shift >= 64:
            raise VarintError("varint too long")


def encode_signed_varint(value: int) -> bytes:
    """Encode a signed integer using zigzag followed by varint.

    Zigzag maps signed integers to unsigned integers so that numbers near zero
    (positive or negative) encode to short varints.

    Args:
        value: Any Python int.

    Returns:
        A bytes object containing the zigzag varint encoding.
    """
    zigzag = (value << 1) ^ (value >> 63)
    # Mask to 64 bits: Python ints are arbitrary precision, but the wire format
    # is defined for 64-bit values only.
    zigzag &= (1 << 64) - 1
    return encode_varint(zigzag)


def decode_signed_varint(data: bytes, offset: int = 0) -> Tuple[int, int]:
    """Decode a zigzag-encoded signed varint.

    Args:
        data: The buffer to read from.
        offset: Starting index. Defaults to 0.

    Returns:
        A tuple (value, new_offset).

    Raises:
        VarintError: If the underlying varint is malformed.
    """
    raw, new_offset = decode_varint(data, offset)
    value = (raw >> 1) ^ -(raw & 1)
    return value, new_offset
