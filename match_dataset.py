import json
import pandas as pd
from collections import Counter

# === CONFIG ===
csv_path = 'SOLID_Violation_Cases_for_Manual_Review_complete.csv'
json_path = 'detailed_results_v5.json'
output_json_path = 'detailed_results_v5_updated.json'
unmatched_log_path = 'unmatched_entries_log_final.csv'

# === LANGUAGE NORMALIZATION MAP ===
LANGUAGE_MAP = {
    "CSHARP": "C#",
    "C SHARP": "C#",
    "C_SHARP": "C#",
    "JAVA": "JAVA",
    "PYTHON": "PYTHON",
    "KOTLIN": "KOTLIN"
}

# === LOAD FILES ===
df = pd.read_csv(csv_path)
with open(json_path, 'r') as f:
    data = json.load(f)

# === TRACKING ===
unmatched = []
updated = 0

# === MAIN LOOP ===
for idx, row in df.iterrows():
    # Extract and normalize fields
    raw_model = str(row['file/model']).strip()
    strategy = str(row['strategy']).strip().lower()
    raw_language = str(row['language']).strip().upper().replace(" ", "").replace("_", "")
    language = LANGUAGE_MAP.get(raw_language, raw_language)
    sample_id = int(row['id'])
    expected_violation = str(row['expected_violation']).strip().upper()
    match_value = row['violation_match']

    # Normalize model for JSON key
    model_clean = raw_model.replace(":", "-").lower()
    json_key = f"{expected_violation.lower()}--{model_clean}--{strategy}"

    # Navigate JSON hierarchy: violation -> model+strategy key -> strategy -> violation -> items
    if json_key not in data:
        unmatched.append({**row.to_dict(), "reason": f"JSON key '{json_key}' not found"})
        continue

    strategy_block = data[json_key].get(strategy, {})
    violation_block = strategy_block.get("violation_results", {}).get(expected_violation.lower(), {})
    items = violation_block.get("items", [])

    match_found = False
    for item in items:
        if item["id"] == sample_id:
            item["violation_match"] = bool(match_value)
            updated += 1
            match_found = True

            # Optional: log language mismatch but do not block update
            json_lang = item.get("language", "").strip().upper()
            if json_lang != language:
                unmatched.append({**row.to_dict(), "reason": f"Language mismatch: CSV={language}, JSON={json_lang} (updated anyway)"})
            break

    if not match_found:
        unmatched.append({**row.to_dict(), "reason": "Matching ID not found in violation block"})

# === SAVE OUTPUTS ===
with open(output_json_path, 'w') as f:
    json.dump(data, f, indent=2)

if unmatched:
    unmatched_df = pd.DataFrame(unmatched)
    unmatched_df.to_csv(unmatched_log_path, index=False)

# === SUMMARY ===
print(f"\n✅ Updated {updated} entries.")
print(f"⚠️ {len(unmatched)} unmatched entries logged to '{unmatched_log_path}'")

# Optional: reason breakdown
if unmatched:
    reason_counts = Counter([u["reason"] for u in unmatched])
    print("\n🔍 Breakdown of unmatched reasons:")
    for reason, count in reason_counts.items():
        print(f"  {reason}: {count}")
