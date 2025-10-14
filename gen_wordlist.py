import secrets
import string
import time
import os

# Configuration
OUTFILE = "wordlist_32_lower_alnum_unique_1m.txt"
TOTAL = 1_000_000
LENGTH = 32
BATCH_SIZE = 10_000
ALPHABET = string.ascii_lowercase + string.digits  # 'abcdefghijklmnopqrstuvwxyz0123456789'

def main():
    start = time.time()
    print(f"Generating {TOTAL:,} unique {LENGTH}-character lowercase alphanumeric strings...")
    print(f"Estimated output size: ~{(TOTAL * (LENGTH + 1)) / (1024 * 1024):.2f} MB\n")

    unique = set()
    with open(OUTFILE, "w", encoding="utf-8") as f:
        while len(unique) < TOTAL:
            needed = TOTAL - len(unique)
            batch_size = min(BATCH_SIZE, needed)
            # generate candidate strings
            batch = {
                ''.join(secrets.choice(ALPHABET) for _ in range(LENGTH))
                for _ in range(batch_size * 2)
            }
            # add only new strings
            new_strings = list(batch - unique)
            if not new_strings:
                continue
            # trim if overshoot
            if len(unique) + len(new_strings) > TOTAL:
                new_strings = new_strings[: TOTAL - len(unique)]
            # record new ones
            for s in new_strings:
                f.write(s + "\n")
            unique.update(new_strings)

            if len(unique) % (BATCH_SIZE * 10) == 0 or len(unique) == TOTAL:
                pct = len(unique) / TOTAL * 100
                elapsed = time.time() - start
                rate = len(unique) / elapsed if elapsed > 0 else 0
                print(f"  {len(unique):,}/{TOTAL:,} ({pct:.2f}%) — {rate:,.0f} lines/sec")

    total_time = time.time() - start
    print(f"\n✅ Done! Generated {TOTAL:,} unique lines in {total_time:.1f} seconds.")
    print(f"Output file: {os.path.abspath(OUTFILE)}")
    print(f"File size: {os.path.getsize(OUTFILE) / (1024 * 1024):.2f} MB")

    # show a quick sample
    print("\nSample (first 5 lines):")
    with open(OUTFILE, "r", encoding="utf-8") as f:
        for i in range(5):
            print(f" {i+1}: {f.readline().strip()}")

if __name__ == "__main__":
    main()
