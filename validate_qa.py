import csv
import re
from collections import Counter

FILE_PATH = "data-science/datasets/intent_v0_raw.csv"
EXPECTED_COLS = ["text", "intent", "group_id", "source", "split"]
VALID_INTENTS = {
    "cek_pesanan", "tanya_ongkir", "tanya_produk",
    "info_umum", "komplain", "di_luar_konteks"
}
VALID_SOURCES = {"team_written", "synthetic", "real"}

errors = []
seen_texts = set()
intent_counts = Counter()

with open(FILE_PATH, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    if reader.fieldnames != EXPECTED_COLS:
        errors.append(f"Header kolom salah: {reader.fieldnames}")

    rows = list(reader)
    if len(rows) < 240:
        errors.append(f"Total baris hanya {len(rows)}, wajib minimal 240 baris.")

    for idx, row in enumerate(rows, start=2):
        text = (row.get("text") or "").strip()
        intent = (row.get("intent") or "").strip()
        group_id = (row.get("group_id") or "").strip()
        source = (row.get("source") or "").strip()
        split = (row.get("split") or "").strip()

        if not text or not intent or not group_id or not source:
            errors.append(f"Baris {idx}: Ada kolom wajib yang kosong.")
        if len(text) > 500:
            errors.append(f"Baris {idx}: Teks melebihi 500 karakter ({len(text)}).")
        if split != "":
            errors.append(f"Baris {idx}: Kolom 'split' harus kosong di intent_v0_raw.csv.")

        text_lower = text.lower()
        if text_lower in seen_texts:
            errors.append(f"Baris {idx}: Kalimat duplikat -> '{text}'")
        seen_texts.add(text_lower)

        if intent not in VALID_INTENTS:
            errors.append(f"Baris {idx}: Intent tidak valid -> '{intent}'")
        else:
            intent_counts[intent] += 1

        if source not in VALID_SOURCES:
            errors.append(f"Baris {idx}: Source tidak valid -> '{source}'")

        if re.search(r"(\+62|08)\d{7,12}", text) or re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text):
            errors.append(f"Baris {idx}: Terdeteksi potensi PII -> '{text}'")

for intent in VALID_INTENTS:
    if intent_counts[intent] < 40:
        errors.append(f"Kelas '{intent}' hanya memiliki {intent_counts[intent]} baris (minimal 40).")

print("=== LAPORAN VALIDASI QA DATASET INTENT (WP-11a) ===")
print(f"Total Baris Terbaca : {len(rows)}")
print("Distribusi Kelas    :", dict(intent_counts))
print("-" * 48)
if errors:
    print(f"[GAGAL] Ditemukan {len(errors)} masalah:")
    for err in errors[:10]:
        print(" -", err)
else:
    print("[PASS] 100% Sesuai data_dictionary.md & kontrak OpenAPI!")