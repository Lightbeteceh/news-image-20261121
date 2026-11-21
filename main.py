#!/usr/bin/env python3
"""news-image-20261121 — make.fun bounty entry.

Sums up the world news of Saturday 21 November 2026 in a single picture.

The picture lives in this repository as ``entry.png``. It is drawn
offline by ``render.py`` from the headlines in ``stories.json``.
This program only places an exact copy of that picture at
``/output/entry.png``, where the bounty harness looks for it.

The copy is byte-for-byte: the file is never re-encoded, nothing
about the current time or machine leaks into it, and it never
touches the network. Run it twice and the two outputs match.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
DEST = Path(os.environ.get("OUTPUT_PATH", "/output/entry.png"))
LIMIT = 1024 * 1024  # the bounty allows at most one mebibyte


def main() -> int:
    if not SOURCE.is_file():
        print(f"error: {SOURCE} is missing", file=sys.stderr)
        return 1

    size = SOURCE.stat().st_size
    if size > LIMIT:
        print(f"error: entry.png is {size} bytes, over the 1 MiB limit",
              file=sys.stderr)
        return 1

    DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, DEST)

    digest = hashlib.sha256(DEST.read_bytes()).hexdigest()
    print(f"wrote {DEST} ({size} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
