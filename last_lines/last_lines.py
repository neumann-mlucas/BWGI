"""
This Python script emulates the behavior of the UNIX tac command: it prints the lines
of one or more files in reverse order (last line first). It reads files by memory-mapping
them and scanning backwards in configurable-sized chunks, yielding one line at a
time. Lines are decoded as UTF-8, with invalid sequences replaced. The script accepts
one or more file paths as command-line arguments and an optional buffer size.

Example usecase:

$ cat log.txt
log line 1
log line 2

$ python last_lines.py log.txt
log line 2
log line 1\n
"""

import argparse
import io
import mmap

from pathlib import Path
from typing import Iterator, BinaryIO


def last_lines(
    file: BinaryIO, bufsize: int = io.DEFAULT_BUFFER_SIZE
) -> Iterator[bytes]:
    """read the file lines in reverse order"""
    # initialize the memory-mapped file objects
    mm = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)

    pos = mm.size()
    while pos > 0:
        # find last newline character within the buffer range
        next = mm.rfind(b"\n", max(pos - bufsize, 0), pos)
        # if no newline character is found, set next to the start of the buffer
        next = max(next, pos - bufsize)
        # yield the line from next to pos
        yield mm[next + 1 : pos + 1]
        # update pos to the position before the newline character
        pos = next


def faster_last_lines(
    file: BinaryIO, bufsize: int = io.DEFAULT_BUFFER_SIZE
) -> Iterator[bytes]:
    """avoids using mmap to not load the addrs space into memory"""
    file.seek(0, io.SEEK_END)
    while file.tell() > 1:
        yield readuntil_backwards(file, b"\n", bufsize)


def readuntil_backwards(file: BinaryIO, delimiter: bytes, limit: int) -> bytes:
    pos, cnt = file.tell(), 0
    buf = bytearray()

    while pos > 1 and cnt < limit:
        pos -= 1
        file.seek(pos - 1)
        byte = file.read(1)
        if byte == delimiter:
            buf.reverse()
            buf.extend(delimiter)
            return bytes(buf)
        buf.extend(byte)
        cnt += 1

    buf.reverse()
    buf.extend(delimiter)
    return bytes(buf)


def clean_bytes(line: bytes) -> str:
    """Convert bytes to UTF-8 string."""
    return line.decode("utf-8", errors="replace")


def main():
    args = parse_args()
    for file_path in args.files:
        with Path(file_path).open("rb") as fp:
            for line in map(clean_bytes, faster_last_lines(fp, args.bufsize)):
                if line.strip():
                    print(repr(line))


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Write each FILE to standard output, last line first."
    )
    parser.add_argument(
        "files", metavar="FILE", type=str, nargs="+", help="the file(s) to read"
    )
    parser.add_argument(
        "--bufsize", "-b", type=int, default=1024, help="chunk size in bytes"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
