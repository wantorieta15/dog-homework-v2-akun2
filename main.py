"""Entry writer for Make Fun bounty:
The Dog Ate My Homework: Funniest Excuse (Akun 2, v2).

Reads the entry from a module-level constant, validates it against the
competition gate (1-200 characters, exactly one line, not blank), and
writes it to entry.txt in the output directory from MAKEFUN_OUTPUT_DIR
(default /output). Standard library only; no third-party dependencies.

The output file is written directly with open() and its mode is set
explicitly to 0644 so the grader can read it. After writing, the file
is re-read and must be byte-identical to the entry, or the run fails.
"""

import hashlib
import os
import sys


ENTRY = (
    "I did the maths in my head. The answer was 'walk'. "
    "The teacher marked it wrong, so I ate the evidence."
)

MIN_LEN = 1
MAX_LEN = 200


def check_length(text):
    if len(text) < MIN_LEN or len(text) > MAX_LEN:
        raise ValueError(
            "entry length %d outside gate %d-%d" % (len(text), MIN_LEN, MAX_LEN)
        )


def check_single_line(text):
    for ch in ("\n", "\r"):
        if ch in text:
            raise ValueError("entry must be a single line (no newline characters)")


def check_no_edge_whitespace(text):
    if text != text.strip():
        raise ValueError("entry must not start or end with whitespace")


def check_no_control_chars(text):
    bad = [ch for ch in text if ord(ch) < 32 or ord(ch) == 127]
    if bad:
        raise ValueError(
            "entry contains control character(s): %r" % bad[:5]
        )


def check_not_blank(text):
    if not text.strip():
        raise ValueError("entry must not be whitespace only")


def validate(text):
    if not isinstance(text, str):
        raise TypeError("entry must be a string, got %s" % type(text).__name__)
    check_length(text)
    check_single_line(text)
    check_not_blank(text)
    check_no_edge_whitespace(text)
    check_no_control_chars(text)
    return text


def output_path():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, "entry.txt")


def verify_roundtrip(path, text):
    """Re-read the file and require byte-identical content.

    The write above is direct (open + chmod, no temp file, no rename),
    and this check proves the bytes on disk are exactly the entry.
    """
    expected = text.encode("utf-8")
    with open(path, "rb") as handle:
        actual = handle.read()
    if actual != expected:
        raise RuntimeError(
            "round-trip mismatch: wrote %d bytes, read %d bytes"
            % (len(expected), len(actual))
        )


def write_entry(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.chmod(path, 0o644)
    verify_roundtrip(path, text)


def main():
    entry = validate(ENTRY)
    path = output_path()
    write_entry(path, entry)
    digest = hashlib.sha256(entry.encode("utf-8")).hexdigest()
    print("wrote %s" % path)
    print("chars: %d" % len(entry))
    print("sha256: %s" % digest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
