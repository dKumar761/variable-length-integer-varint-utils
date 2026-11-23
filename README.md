# variable-length-integer-varint-utils

Encodes and decodes integers using protobuf-style variable-length encoding, returning byte objects and consuming from arbitrary byte streams.

## Usage

```python
from variable_length_integer_varint_utils import (
    encode_varint,
    decode_varint,
    encode_signed_varint,
    decode_signed_varint,
)

# Unsigned varints
encoded = encode_varint(300)          # b'\xac\x02'
value, offset = decode_varint(encoded) # (300, 2)

# Signed varints use zigzag encoding
encoded = encode_signed_varint(-1)     # b'\x01'
value, offset = decode_signed_varint(encoded)  # (-1, 1)
```

## Why this exists

Protocol Buffers and similar formats need a compact, self-delimiting integer encoding. This library implements the base-128 varint scheme used by protobuf, plus zigzag encoding for signed integers. The trade-off is simplicity: it operates on `bytes` and explicit offsets rather than wrapping a stream object, so it works with any buffer you already have and adds no dependencies.

## Edge case

The decoder rejects varints longer than 10 bytes (the maximum for a 64-bit value). If you feed it a truncated or overlong varint it raises `VarintError`. Note that Python integers are arbitrary precision, but the wire format is defined for 64-bit values only; `encode_signed_varint` masks to 64 bits before encoding.
