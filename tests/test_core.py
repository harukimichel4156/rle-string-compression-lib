import unittest

from rle_string_compression_lib import compress, decompress, RLEError


class TestRoundTrip(unittest.TestCase):
    def assert_round_trip(self, original):
        self.assertEqual(decompress(compress(original)), original)

    def test_empty(self):
        self.assert_round_trip("")

    def test_single_char(self):
        self.assert_round_trip("a")

    def test_short_run(self):
        self.assert_round_trip("aaabbbccc")

    def test_long_run(self):
        self.assert_round_trip("a" * 1000)

    def test_mixed_text(self):
        self.assert_round_trip("mississippi river")

    def test_single_digits_embedded(self):
        # Single digits must round-trip because they are literal data.
        self.assert_round_trip("ab3cd9")

    def test_repeated_digits(self):
        self.assert_round_trip("11111")

    def test_digit_run_inside_text(self):
        self.assert_round_trip("chapter 42 has 1111 footnotes")

    def test_all_digits(self):
        self.assert_round_trip("0123456789")

    def test_single_backslash(self):
        self.assert_round_trip("a\\b")

    def test_repeated_backslashes(self):
        self.assert_round_trip("a\\\\\\b")

    def test_backslash_before_digit(self):
        self.assert_round_trip("\\5")

    def test_backslash_before_letter(self):
        self.assert_round_trip("\\a")

    def test_mixed_backslashes_and_digits(self):
        self.assert_round_trip("a\\1b222c\\\\\\d3")


class TestCompressedForm(unittest.TestCase):
    def test_short_run_encoding(self):
        self.assertEqual(compress("aaabbb"), "3a3b")

    def test_single_char_encoding(self):
        self.assertEqual(compress("abc"), "abc")

    def test_digit_run_is_escaped(self):
        self.assertEqual(compress("111"), "\\111")

    def test_backslash_is_doubled(self):
        self.assertEqual(compress("\\\\"), "\\\\\\\\")


class TestErrors(unittest.TestCase):
    def test_dangling_backslash(self):
        with self.assertRaises(RLEError):
            decompress("\\")

    def test_invalid_escape(self):
        with self.assertRaises(RLEError):
            decompress("\\a")

    def test_count_without_char(self):
        with self.assertRaises(RLEError):
            decompress("5")

    def test_empty_is_empty(self):
        self.assertEqual(decompress(""), "")


if __name__ == "__main__":
    unittest.main()
