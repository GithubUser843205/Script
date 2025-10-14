import hashlib
from Crypto.Cipher import AES
import base64
import string
import os

def is_mostly_printable(text: str, threshold: float = 0.9) -> bool:
    if not text:
        return False
    printable = set(string.printable)
    score = sum(1 for c in text if c in printable) / len(text)
    return score >= threshold

def try_decrypt_with_key(encrypted_bytes: bytes, candidate_key: str):
    """Return (True, plaintext) on success, otherwise (False, reason)."""
    try:
        aes_key = hashlib.sha256(candidate_key.encode('utf-8')).digest()
        iv = encrypted_bytes[:16]
        ciphertext = encrypted_bytes[16:]
        if len(ciphertext) == 0:
            return False, "ciphertext empty after IV"
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        decrypted = decrypted.rstrip(b'\x00')  # remove null padding
        try:
            plaintext = decrypted.decode('utf-8')
        except UnicodeDecodeError:
            return False, "utf-8 decode failed"
        if not plaintext.strip():
            return False, "plaintext empty or whitespace"
        if not is_mostly_printable(plaintext):
            return False, "plaintext not mostly printable"
        return True, plaintext
    except Exception as e:
        return False, f"exception: {e}"

def main():
    encrypted_b64 = input("Enter Encrypted Value (Base64): ").strip()
    if not encrypted_b64:
        print("No encrypted value provided. Exiting.")
        return

    wordlist_path = input("Enter path to wordlist file (one key per line): ").strip()
    if not wordlist_path or not os.path.isfile(wordlist_path):
        print("Wordlist file not found. Exiting.")
        return

    # decode once
    try:
        encrypted_bytes = base64.b64decode(encrypted_b64)
    except Exception as e:
        print("Failed to Base64-decode encrypted value:", e)
        return

    if len(encrypted_bytes) <= 16:
        print("Decoded data too short (must contain IV + ciphertext). Exiting.")
        return

    found = []  # list of tuples (candidate_key, plaintext)
    total_tried = 0

    # Count lines (best-effort) for progress display
    total_lines = None
    try:
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            total_lines = sum(1 for _ in f)
    except Exception:
        total_lines = None

    print(f"Trying keys from {wordlist_path} (total ~ {total_lines if total_lines is not None else 'unknown'}) ...")

    try:
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            for idx, raw_line in enumerate(f, 1):
                candidate = raw_line.rstrip("\n\r")
                if not candidate:
                    continue
                total_tried += 1

                success, result = try_decrypt_with_key(encrypted_bytes, candidate)
                if success:
                    print(f"\n[FOUND] Key (line {idx}): {candidate}")
                    print("Decrypted plaintext:")
                    print(result)
                    found.append((candidate, result))
                    # continue searching — collect all valid keys

                # optional progress print
                if total_tried % 1000 == 0:
                    if total_lines:
                        print(f"  Tried {total_tried}/{total_lines} keys...")
                    else:
                        print(f"  Tried {total_tried} keys...")

    except KeyboardInterrupt:
        print("\nInterrupted by user — will report what was found so far.")
    except Exception as e:
        print("Error while reading wordlist:", e)
        return

    # Report results
    if found:
        print("\n✅ Completed. Valid keys found:")
        for i, (k, p) in enumerate(found, 1):
            print(f"\n{i}) Key: {k}\nPlaintext:\n{p}\n{'-'*40}")
    else:
        print("\n❌ Completed. No valid keys found in the provided wordlist.")

    print(f"Total keys tried: {total_tried}")

if __name__ == "__main__":
    main()
