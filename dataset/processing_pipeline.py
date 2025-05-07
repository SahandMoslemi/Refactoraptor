import os
import json
import requests
from pathlib import Path
from tqdm import tqdm

API_URL = "http://localhost:8080/refactor"

MODELS = ["codellama:7b", "starcoder:7b", "codegemma:7b", "deepseek:6.7b"]
STRATEGIES = ["DEFAULT", "ENSEMBLE", "TAGGING", "SMELL"]

INPUT_DIR = Path(".")
OUTPUT_DIR = Path("refactored_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

def call_refactor_api(model, strategy, source_code):
    payload = {
        "model": model,
        "strategy": strategy,
        "temperature": "0",
        "source": source_code
    }
    response = requests.post(API_URL, json=payload)
    response.raise_for_status()
    return response.json().get("response", "")

def parse_response(response_str):
    try:
        response_data = json.loads(response_str)
        return {
            "type": response_data.get("type", ""),
            "refactored_code": response_data.get("refactored_code", ""),
            "explanation": response_data.get("explanation", "")
        }
    except json.JSONDecodeError:
        print("Failed to decode JSON from response")
        return {
            "type": "",
            "refactored_code": "",
            "explanation": ""
        }

def process_file(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)

    base_name = filepath.stem

    for model in tqdm(MODELS, desc="Models"):
        for strategy in tqdm(STRATEGIES, desc=f"Strategies for {model}", leave=False):
            updated_data = {"code_examples": []}
            examples = data.get("code_examples", [])
            for example in tqdm(examples, desc=f"Examples ({model}/{strategy})", leave=False):
                response = call_refactor_api(model, strategy, example["input"])
                parsed = parse_response(response)
                example["refactored_code"] = parsed["refactored_code"]
                example["type"] = parsed["type"]
                example["explanation"] = parsed["explanation"]
                updated_data["code_examples"].append(example)

            output_filename = f"{base_name}_{model.replace(':', '-')}_{strategy}.json"
            with open(OUTPUT_DIR / output_filename, "w") as out_file:
                json.dump(updated_data, out_file, indent=4)

# Process all JSON files in the current directory
for file in INPUT_DIR.glob("*.json"):
    process_file(file)
