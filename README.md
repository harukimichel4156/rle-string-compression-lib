# rle-string-compression-lib

Compresses and decompresses strings using a character-based run-length encoding scheme that escapes literal digit runs.

```python
from rle_string_compression_lib import compress, decompress

compressed = compress("aaabbb1111")      # '3a3b\\1111'
original = decompress(compressed)         # 'aaabbb1111'
```

The library exists for the case where text has long runs of a single character (whitespace, padding, repeated symbols) and you want a reversible, dependency-free compression that stays human-readable. The trade-off is that strings with few repeats may grow slightly: every literal run of digits is escaped with a backslash, and single backslashes are doubled, so digit- and backslash-heavy text is the worst case.

The awkward edge: because a digit directly precedes the character it counts, literal digit runs must be escaped (with a leading backslash) so the decoder never mistakes them for a count. If your input contains many scattered digits, `compress` will insert a backslash before each, which inflates size. A single backslash in the input becomes two in the output; a backslash followed by a digit becomes two characters plus the digit.

The format writes single characters without a count, so `compress("abc")` returns `"abc"`, not `"1a1b1c"`. Malformed compressed input raises `RLEError`, a subclass of `ValueError`.

Exported names: `compress`, `decompress`, `RLEError`.
