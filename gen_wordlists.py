#!/usr/bin/env python3
"""
generate_lowercase_wordlist_1m.py
Generates 1,000,000 lines of 32-character lowercase-only strings.
Writes to 'wordlist_32_lower_1m.txt' in the current directory.

Be sure you have ~40 MB free disk space before running.
"""

import secrets
import string
import os
import time

OUTFILE = "wordlist_32_lower_1m.txt"
TOTAL = 1_000_000
LENGTH = 32
BATCH_SIZE = 10_000  # number of lines to generate per batch (tune for speed/memory)
ALPHABET = string.ascii_lowercase  # 'abcdefghijklmnopqrstuvwxyz'

def generate_line(length=LENGTH):
    # use secrets.choice for cryptographic randomness; replace with random.choices for speed if desired
    return ''.join(secrets.choice(ALPHABET) for _ in range(length))

def main():
    start = time.time()
    # Quick sanity: estimate size
    estimated_bytes = (LENGTH + 1) * TOTAL  # each line + newline
    estimated_mb = estimated_bytes / (1024 * 1024)
    print(f"Generating {TOTAL:,} lines of length {LENGTH} (lowercase letters only).")
    print(f"Estimated file size: {estimated_bytes:,} bytes (~{estimated_mb:.2f} MiB).")
    print(f"Output file: {os.path.abspath(OUTFILE)}\n")

    written = 0
    with open(OUTFILE, "w", encoding="utf-8") as f:
        while written < TOTAL:
            to_do = min(BATCH_SIZE, TOTAL - written)
            # generate batch
            batch_lines = [''.join(secrets.choice(ALPHABET) for _ in range(LENGTH)) for _ in range(to_do)]
            # write as a single blob to minimize I/O overhead
            f.write("\n".join(batch_lines))
            f.write("\n")
            written += to_do

            # progress print
            if written % (BATCH_SIZE * 1) == 0 or written == TOTAL:
                pct = written / TOTAL * 100
                elapsed = time.time() - start
                rate = written / elapsed if elapsed > 0 else 0
                print(f"  Written {written:,}/{TOTAL:,} lines ({pct:.2f}%) — {rate:.0f} lines/sec")

    total_time = time.time() - start
    print(f"\nDone. Written {TOTAL:,} lines to '{OUTFILE}' in {total_time:.1f} seconds.")
    print(f"Actual file size: {os.path.getsize(OUTFILE) / (1024*1024):.2f} MiB")

if __name__ == "__main__":
    main()