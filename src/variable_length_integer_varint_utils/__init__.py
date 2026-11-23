"""Variable-length integer encoding utilities.

This package provides protobuf-style varint encoding and decoding.
The public API is re-exported here for convenience.
"""

from .core import (
    encode_varint,
    decode_varint,
    encode_signed_varint,
    decode_signed_varint,
    VarintError,
)

__all__ = [
    "encode_varint",
    "decode_varint",
    "encode_signed_varint",
    "decode_signed_varint",
    "VarintError",
]
