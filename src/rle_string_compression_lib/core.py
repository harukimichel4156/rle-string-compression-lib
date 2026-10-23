"""Character-based run-length encoding that escapes literal digit runs.

The encoding records repeated characters as ``<count><char>``. To keep the
format unambiguous, any literal run of ASCII digits in the input is prefixed
with a ``\\`` so the decoder can treat it as raw data instead of a count. Any
single ``\\`` that is not followed by a digit is itself escaped as ``\\\\`` so the
backslash survives the round trip. Single characters (count == 1) are written
without a count, which keeps short mixed text from ballooning.
"""

from collections.abc import Iterable


class RLEError(ValueError):
    """Raised when the compressed stream is malformed."""


def _is_digit(ch: str) -> bool:
    return "0" <= ch <= "9"


def compress(s: str) -> str:
    """Compress ``s`` using escaped, character-based RLE.

    Returns the compressed string. ``compress`` is the exact inverse of
    :func:`decompress` for all inputs, including strings that contain
    backslashes and digits.
    """
    out: list[str] = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        j = i + 1
        while j < n and s[j] == ch:
            j += 1
        run_len = j - i

        if _is_digit(ch):
            # Literal digit runs are escaped so the decoder reads them as data,
            # never as a leading count.
            out.append("\\")
            out.append(ch * run_len)
        elif ch == "\\":
            # A backslash not followed by a digit would otherwise be
            # indistinguishable from the escape marker, so we double it.
            out.append("\\\\" * run_len)
        else:
            if run_len == 1:
                out.append(ch)
            else:
                out.append(str(run_len))
                out.append(ch)
        i = j
    return "".join(out)


def _parse_count(stream: str, start: int) -> tuple[int, int]:
    """Read a decimal integer from ``stream`` starting at ``start``.

    Returns ``(count, next_index)``. Raises :class:`RLEError` on overflow.
    """
    i = start
    while i < len(stream) and _is_digit(stream[i]):
        i += 1
    digits = stream[start:i]
    if not digits:
        raise RLEError(f"expected digits at position {start}")
    try:
        count = int(digits)
    except ValueError as exc:
        raise RLEError(f"count overflow at position {start}") from exc
    return count, i


def decompress(s: str) -> str:
    """Decompress a string produced by :func:`compress`.

    Raises :class:`RLEError` if the stream is malformed.
    """
    out: list[str] = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == "\\":
            if i + 1 >= n:
                raise RLEError("dangling backslash at end of input")
            nxt = s[i + 1]
            if _is_digit(nxt):
                j = i + 1
                while j < n and _is_digit(s[j]):
                    j += 1
                out.append(s[i + 1:j])
                i = j
                continue
            if nxt == "\\":
                out.append("\\")
                i += 2
                continue
            raise RLEError(f"invalid escape sequence \\{nxt!r} at position {i}")

        if _is_digit(ch):
            count, after = _parse_count(s, i)
            if after >= n:
                raise RLEError(f"count {count} has no character at position {i}")
            out.append(s[after] * count)
            i = after + 1
            continue

        out.append(ch)
        i += 1
    return "".join(out)


def iter_decompress(s: str) -> Iterable[str]:
    """Yield decompressed chunks one run at a time.

    Useful when feeding a large compressed stream incrementally; correctness
    is identical to :func:`decompress`, which simply joins these chunks.
    """
    out: list[str] = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == "\\":
            if i + 1 >= n:
                raise RLEError("dangling backslash at end of input")
            nxt = s[i + 1]
            if _is_digit(nxt):
                j = i + 1
                while j < n and _is_digit(s[j]):
                    j += 1
                out.append(s[i + 1:j])
                i = j
                continue
            if nxt == "\\":
                out.append("\\")
                i += 2
                continue
            raise RLEError(f"invalid escape sequence \\{nxt!r} at position {i}")

        if _is_digit(ch):
            count, after = _parse_count(s, i)
            if after >= n:
                raise RLEError(f"count {count} has no character at position {i}")
            out.append(s[after] * count)
            i = after + 1
            continue

        out.append(ch)
        i += 1

        if len(out) >= 256:
            yield "".join(out)
            out.clear()

    if out:
        yield "".join(out)
