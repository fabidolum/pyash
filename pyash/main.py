#! /bin/env python3
"""
Build an alternative to unix checksum (like sha256sum) to skip some lines 
when doing the checksum computation.

Usage:

    * hash creation : 
        python3 -m phash.main -s 'comment_character' 'file_name'
    * hash verification
        python3 -m phash.main -c -s 'comment_character' 'file_name'
        python3 -m phash.main -c 'file_name'

"""

import hashlib
import sys
import argparse

from typing import Optional, Iterator, Callable
from io import BufferedReader


def regular_computehash(filein: BufferedReader, stchar: None) -> str:
    """Create a sha256sum, without filtering"""
    m = hashlib.sha256()
    for l in filein:
        m.update(l)
    return f"{m.hexdigest()}"


def computehash(filein: BufferedReader, stchar: bytes) -> str:
    """Create a sha256sum, filtering the comments"""
    m = hashlib.sha256()
    for l in filein:
        if not l.startswith(stchar):
            m.update(l)
    return f"{m.hexdigest()}"


def split_line(l):
    """Splitting the line to check.

    Valid separator are (from man sha256sum):
     - '  ' (double space)
     - ' *' (spoace followed by star)

    """
    try:
        (ch, cf) = l.split(b"  ")
    except ValueError:
        try:
            (ch, cf) = l.split(b" *")
        except ValueError:
            raise
    return (ch, cf.strip())


def checkhash(
    filein: BufferedReader, stchar: Optional[bytes]
) -> Iterator[tuple[bool, bytes]]:
    """Check each "checksum file" and yield the result. Comment character is enforced."""
    if stchar is None:
        compute_function: Callable[[BufferedReader, None], str] = regular_computehash
    else:
        compute_function: Callable[[BufferedReader, None], bytes] = computehash
    for l in filein:
        if l.startswith(b"#"):
            continue
        (ch, cf) = split_line(l)
        with open(cf, "rb") as f:
            h = compute_function(f, stchar)
        if ch == bytes(h, "utf-8"):
            yield (True, cf)
        else:
            yield (False, cf)


def checkhash_autodetect(
    filein: BufferedReader, stchar: Optional[bytes]
) -> Iterator[tuple[bool, bytes]]:
    """Check each "checksum file" and yield the result, guessing the skip character."""
    compute_function: Callable[[BufferedReader, None], str] = regular_computehash
    for l in filein:
        if l.startswith(b"# -s "):
            stchar = l.removeprefix(b"# -s ").rstrip()
            compute_function: Callable[[BufferedReader, None], bytes] = computehash
            continue
        (ch, cf) = split_line(l)
        with open(cf, "rb") as f:
            h = compute_function(f, stchar)
        if ch == bytes(h, "utf-8"):
            yield (True, cf)
        else:
            yield (False, cf)
        compute_function: Callable[[BufferedReader, None], str] = regular_computehash


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Checksum (sha256sum) while skipping commented lines"
    )
    parser.add_argument(
        "filelist",
        help="list of files for checksum computation or check",
        nargs="+",
    )
    parser.add_argument(
        "-c",
        "--check",
        help="read SHA256 sums from the filelist and check them",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--skip",
        help="start of line characters to consider as a comment",
        type=str,
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help="don't print OK for each successfully verified file",
        action="store_true",
    )
    parser.add_argument(
        "--strict",
        help="Placeholder option for compatibility with sha256sum",
        action="store_true",
    )
    args = parser.parse_args(argv)

    filelist: list[str] = args.filelist

    stchar: Optional[bytes] = None
    if args.skip is not None:
        stchar = bytes(args.skip, "utf-8")
        compute_function = computehash
        check_function = checkhash
    else:
        compute_function = regular_computehash
        check_function = checkhash_autodetect

    status = 0
    if args.check:
        for fi in filelist:
            try:
                with open(fi, "rb") as f:
                    try:
                        for r, filename in check_function(f, stchar):
                            if r:
                                if not args.quiet:
                                    print(f'{filename.decode(encoding="utf-8")} OK')
                            else:
                                if not args.quiet:
                                    print(f'{filename.decode(encoding="utf-8")} FAILED')
                                status += 1
                    except ValueError as e:
                        if not args.quiet:
                            print(f"Malformed line in {fi}: {e}")
                        status += 1
            except FileNotFoundError as e:
                if not args.quiet:
                    print(f"File not found: {e}")
                status = 127
        return status
    else:
        for fi in filelist:
            try:
                with open(fi, "rb") as f:
                    if args.skip is not None:
                        print(f'# -s {stchar.decode(encoding="utf-8")}')
                    print(f"{compute_function(f, stchar)}  {fi}")
            except FileNotFoundError:
                status = 127
        return status


if __name__ == "__main__":
    sys.exit(main())
