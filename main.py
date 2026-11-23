#!/usr/bin/env python3
"""Entry point for the make.fun news-image-20261122 entry (v2).

The front page itself is rendered by build_image.py (Python + Pillow,
deterministic: two runs byte-identical) and committed as entry.png.
This entry point copies that committed page into the harness output
directory ($MAKEFUN_OUTPUT_DIR, or ./output beside this file when the
variable is unset) and verifies the copy is byte-identical by SHA-256,
so the graded run depends on nothing beyond the standard library.
"""

import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join(HERE, "output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    if sha256(SRC) != sha256(dst):
        print("ERROR: output is not byte-identical to entry.png", file=sys.stderr)
        return 1
    print("wrote %s" % dst)
    print("sha256: %s (byte-identical to entry.png)" % sha256(dst))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
