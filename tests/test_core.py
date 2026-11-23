import unittest

from variable_length_integer_varint_utils import (
    encode_varint,
    decode_varint,
    encode_signed_varint,
    decode_signed_varint,
    VarintError,
)


class TestEncodeVarint(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(encode_varint(0), b"\x00")

    def test_one(self):
        self.assertEqual(encode_varint(1), b"\x01")

    def test_127(self):
        self.assertEqual(encode_varint(127), b"\x7f")

    def test_128(self):
        self.assertEqual(encode_varint(128), b"\x80\x01")

    def test_300(self):
        self.assertEqual(encode_varint(300), b"\xac\x02")

    def test_large(self):
        self.assertEqual(encode_varint(2**64 - 1), b"\xff" * 9 + b"\x01")

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            encode_varint(-1)


class TestDecodeVarint(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(decode_varint(b"\x00"), (0, 1))

    def test_one(self):
        self.assertEqual(decode_varint(b"\x01"), (1, 1))

    def test_127(self):
        self.assertEqual(decode_varint(b"\x7f"), (127, 1))

    def test_128(self):
        self.assertEqual(decode_varint(b"\x80\x01"), (128, 2))

    def test_300(self):
        self.assertEqual(decode_varint(b"\xac\x02"), (300, 2))

    def test_large(self):
        encoded = b"\xff" * 9 + b"\x01"
        self.assertEqual(decode_varint(encoded), (2**64 - 1, 10))

    def test_offset(self):
        data = b"\x00\xac\x02"
        self.assertEqual(decode_varint(data, 1), (300, 3))

    def test_truncated(self):
        with self.assertRaises(VarintError):
            decode_varint(b"\x80")

    def test_too_long(self):
        # 11 bytes with continuation bits set (invalid for 64-bit varint)
        data = b"\x80" * 10 + b"\x01"
        with self.assertRaises(VarintError):
            decode_varint(data)


class TestSignedVarint(unittest.TestCase):
    def test_roundtrip(self):
        for value in [0, 1, -1, 2, -2, 127, -127, 128, -128, 2**31 - 1, -(2**31)]:
            encoded = encode_signed_varint(value)
            decoded, offset = decode_signed_varint(encoded)
            self.assertEqual(decoded, value)
            self.assertEqual(offset, len(encoded))

    def test_zigzag_examples(self):
        self.assertEqual(encode_signed_varint(0), b"\x00")
        self.assertEqual(encode_signed_varint(-1), b"\x01")
        self.assertEqual(encode_signed_varint(1), b"\x02")
        self.assertEqual(encode_signed_varint(-2), b"\x03")
        self.assertEqual(encode_signed_varint(2), b"\x04")

    def test_offset(self):
        encoded = encode_signed_varint(-300)
        data = b"\x00" + encoded
        value, offset = decode_signed_varint(data, 1)
        self.assertEqual(value, -300)
        self.assertEqual(offset, len(data))

    def test_truncated(self):
        with self.assertRaises(VarintError):
            decode_signed_varint(b"\x80")


if __name__ == "__main__":
    unittest.main()
