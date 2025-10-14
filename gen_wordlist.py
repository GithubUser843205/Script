#!/usr/bin/env python3
"""
generate_unique_hex_10m.py
Generate 10,000,000 UNIQUE 32-character lowercase hexadecimal strings (0-9, a-f).
Each line is produced by AES-128(key).encrypt(counter) where counter is a 16-byte big-endian integer.
This guarantees uniqueness without storing generated items in memory.

Output file: wordlist_32_hex_unique_10m.txt
"""
import os
import time
import secrets
from Crypto.Cipher import AES

# Configuration
OUTFILE = "wordlist_32_hex_unique_10m.txt"
TOTAL = 10_000_000
BATCH_SIZE = 100_000   # tune for I/O. 100k is a reasonable default.
# You can set START_COUNTER to 0 to start from 0, or provide any integer < 2**128
START_COUNTER = 0

def int_to_16bytes_be(n: int) -> bytes:
    return n.to_bytes(16, byteorder="big")

def main():
    # generate a random AES-128 key (16 bytes). Save the key to reproduce.
    key = secrets.token_bytes(16)
    cipher = AES.new(key, AES.MODE_ECB)  # ECB is fine here because we encrypt unique counters

    print("Output file:", os.path.abspath(OUTFILE))
    print("Total lines:", f"{TOTAL:,}")
    print("Batch size:", f"{BATCH_SIZE:,}")
    print("AES key (hex) — save this to reproduce the file:", key.hex())
    print("Start counter:", START_COUNTER)
    print()

    written = 0
    counter = START_COUNTER
    start_time = time.time()

    with open(OUTFILE, "w", encoding="utf-8") as f:
        while written < TOTAL:
            # create a batch
            to_do = min(BATCH_SIZE, TOTAL - written)
            lines = []
            for _ in range(to_do):
                block = int_to_16bytes_be(counter)
                ct = cipher.encrypt(block)         # 16 bytes
                hex32 = ct.hex()                   # 32 lowercase hex chars
                lines.append(hex32)
                counter += 1

            # write batch as single blob
            f.write("\n".join(lines))
            f.write("\n")

            written += to_do

            # progress print (every batch)
            elapsed = time.time() - start_time
            rate = written / elapsed if elapsed > 0 else 0
            pct = written / TOTAL * 100
            print(f"  Written {written:,}/{TOTAL:,} ({pct:.2f}%) — {rate:,.0f} lines/sec", end="\r")

    total_time = time.time() - start_time
    print("\n\nDone.")
    print(f"Written {TOTAL:,} lines to {OUTFILE}")
    print(f"Actual file size: {os.path.getsize(OUTFILE) / (1024*1024):.2f} MiB")
    print(f"Elapsed time: {total_time:.1f} s")
    print("\nTo reproduce the same file later, reuse the printed AES key hex and the same START_COUNTER.")

if __name__ == "__main__":
    main()
