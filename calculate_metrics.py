import json
import pandas as pd
from collections import defaultdict
from sklearn.metrics import precision_recall_fscore_support

# === CONFIG ===
json_path = "detailed_results_v5_updated.json"

# === LOAD JSON ===
with open(json_path, "r") as f:
    data = json.load(f)

# === COLLECT ALL SAMPLES ===
records = []

for full_key, model_block in data.items():
    try:
        # Parse key: e.g. "lsp--model--strategy"
        expected_violation, model_name, strategy = full_key.split("--")
        strategy_data = model_block[strategy]
        items = strategy_data["violation_results"][expected_violation]["items"]
    except Exception as e:
        print(f"Skipping malformed block: {full_key} — {e}")
        continue

    for item in items:
        records.append({
            "violation": expected_violation.upper(),
            "strategy": strategy,
            "model": item.get("model", model_name),
            "language": item.get("language", "UNKNOWN").upper(),
            "id": item["id"],
            "label": True,  # All gold labels are True (we expect violation to be matched)
            "pred": bool(item.get("violation_match", False))
        })

df = pd.DataFrame(records)

# === METRIC FUNCTION ===
def compute_metrics(group, keys):
    y_true = group["label"]
    y_pred = group["pred"]
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )
    return {
        **{k: group[k].iloc[0] for k in keys},
        "accuracy": round((y_true == y_pred).mean(), 3),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1_score": round(f1, 3),
        "support": len(group)
    }

# === GROUP AND CALCULATE ===
results_vio_strat = df.groupby(["violation", "strategy"]).apply(lambda g: compute_metrics(g, ["violation", "strategy"]))
results_vio_strat_lang = df.groupby(["violation", "strategy", "language"]).apply(lambda g: compute_metrics(g, ["violation", "strategy", "language"]))
results_vio_strat_model = df.groupby(["violation", "strategy", "model"]).apply(lambda g: compute_metrics(g, ["violation", "strategy", "model"]))

# === OUTPUT AS DATAFRAMES ===
df_vio_strat = pd.DataFrame(results_vio_strat.tolist())
df_vio_strat_lang = pd.DataFrame(results_vio_strat_lang.tolist())
df_vio_strat_model = pd.DataFrame(results_vio_strat_model.tolist())

# Save to CSV
df_vio_strat.to_csv("metrics_by_strategy.csv", index=False)
df_vio_strat_lang.to_csv("metrics_by_language.csv", index=False)
df_vio_strat_model.to_csv("metrics_by_model.csv", index=False)

# Print summary and tell the user where to find results
print("\n✅ Metrics saved:")
print("- metrics_by_strategy.csv")
print("- metrics_by_language.csv")
print("- metrics_by_model.csv")

