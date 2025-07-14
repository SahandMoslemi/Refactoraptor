import json
import os
import subprocess
import re
import time

OLLAMA_PATH = "ollama"
OLLAMA_MODELS = ["codellama70b-temp0:latest", "deepseek33b-temp0:latest", "qwen2.5-coder32b-temp0:latest"]
# OLLAMA_MODEL = "qwen2.5-coder32b-temp0:latest"
DATA_PATHs = ["data/srp_violations.json", "data/ocp_violations.json", "data/lsp_violations.json", "data/isp_violations.json", "data/dip_violations.json"]

def ensemble_prompt(code_snippet, language="Java"):
    return f"""Analyze the following {language} code for SOLID principle violations:

```{language.lower()}
{code_snippet}
```

INSTRUCTIONS:
1. Rate each SOLID principle (0-5 scale)
2. Select the most impactful violation

SOLID RATINGS:
- SRP: [score] - [reasoning]
- OCP: [score] - [reasoning]
- LSP: [score] - [reasoning]
- ISP: [score] - [reasoning]
- DIP: [score] - [reasoning]

MOST IMPACTFUL VIOLATION: [principle or NONE]

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
[SOLID ratings above]

**[VIOLATION TYPE or NONE]**

[Explanation of violation]

REMEMBER: 
- If there is NO violation, write **NONE** and provide no explanation.
- If there IS a violation, provide an explanation of what makes it a violation.
"""

def code_smell_prompt(code_snippet, language): 
   return ( 
       f"First, identify any code smells (e.g., God Object, Interface Bloat, Inappropriate Intimacy) in the following {language} code.\n" 
       "Then, map each smell to a relevant SOLID principle.\n" 
       "After that, rate the code from 0 (bad) to 5 (good) on:\n" 
       "SRP, OCP, LSP, ISP, DIP.\n\n" 
       "Then, pick the **single most violated** principle and explain the violation.\n\n"
       "If there is no violation, you can return NONE.\n" 
       "**Important:** Your output must follow *exactly* this format, with no additional commentary before or after.\n\n" 
       "**<VIOLATION TYPE>**\n" 
       "<Explanation of the violation>\n\n" 
       "Only output the text above. Do not include extra analysis or preamble.\n\n" 
       "Example:\n" 
       "**SRP**\n" 
       "This class violates the Single Responsibility Principle because it has multiple responsibilities.\n\n"
       + code_snippet 
   )

def default_prompt(source, language):
   return f"Identify the type of SOLID violation (Single Responsibility Principle, Open-Closed Principle, Liskov Substitution Principle, Interface Segregation Principle) in the following {language} code. If you cannot find a violation, return NONE:\n{source}"

def example_prompt(source, language):
    return (
        f"You are an expert in identifying and refactoring SOLID principle violations in {language} code. "
        "Your task is to analyze the code provided and respond in the exact format below, without any additional text or commentary.\n\n"
        "You must provide the following three parts in your response:\n"
        "1. The violated SOLID principle (e.g., SRP, OCP, LSP, ISP, DIP). If no violation exists, respond with **NONE**.\n"
        "2. A brief explanation of the violation and the refactoring.\n\n"
        "Use these criteria to detect violations:\n"
        "- **SRP**: A class does too many unrelated tasks.\n"
        "- **OCP**: Multiple `if-else` or `switch` blocks for logic that should be handled by polymorphism.\n"
        "- **LSP**: Subclasses override behavior in a way that breaks the contract of the base class (e.g., throw exceptions).\n"
        "- **ISP**: Interfaces that are too large or force implementing unnecessary methods.\n"
        "- **DIP**: High-level classes directly depend on low-level classes instead of abstractions.\n\n"
        "If more than one violation is present, report only the most prominent one.\n\n"
        "**IMPORTANT:** Follow this output format *exactly*. Do not include greetings, summaries, or comments before or after the output:\n\n"
        "**<VIOLATION TYPE>**\n"
        "<Explanation of the violation>\n\n"
        "Example output:\n"
        "**SRP**\n"
        "This class violates the Single Responsibility Principle because it has multiple responsibilities.\n\n" 
        "Here is the code:\n"
        + source
    )

def extract_code_block(response):
    matches = re.findall(r"```(?:\w+)?\n(.*?)```", response, re.DOTALL)
    return matches[0].strip() if matches else ""

def extract_explanation(response):
    parts = response.split("```")
    return parts[0].strip() if parts else ""

def extract_violation(response, return_list=False):
    pattern = r"(?i)\b(SRP|SINGLE RESPONSIBILITY PRINCIPLE|OCP|OPEN-CLOSED PRINCIPLE|LSP|LISKOV SUBSTITUTION PRINCIPLE|ISP|INTERFACE SEGREGATION PRINCIPLE|DIP|DEPENDENCY INVERSION PRINCIPLE)\b"
    matches = re.findall(pattern, response)

    if not matches:
        return [] if return_list else "Unknown"

    mapping = {
        "SINGLE RESPONSIBILITY PRINCIPLE": "SRP",
        "SRP": "SRP",
        "OPEN-CLOSED PRINCIPLE": "OCP",
        "OCP": "OCP",
        "LISKOV SUBSTITUTION PRINCIPLE": "LSP",
        "LSP": "LSP",
        "INTERFACE SEGREGATION PRINCIPLE": "ISP",
        "ISP": "ISP",
        "DEPENDENCY INVERSION PRINCIPLE": "DIP",
        "DIP": "DIP",
    }

    unique = list(dict.fromkeys(mapping[m.upper()] for m in matches))
    return unique if return_list else ", ".join(unique)

def run_ollama(prompt, model_name):
    try:
        cmd = [OLLAMA_PATH, "run", model_name]

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True  # text=True
        )

        stdout, stderr = process.communicate(input=prompt, timeout=600)

        if process.returncode != 0:
            print(f"[ERROR] Ollama failed for {model_name}:", stderr.strip())
            return "[ERROR: Ollama failed]"

        return stdout.strip()

    except subprocess.TimeoutExpired:
        return "[ERROR: Ollama timed out]"
def engineer_prompt(source, language):
    return (
        f"Identify violations in the following {language} code that has a solid violation. "
        f"The type of violation will be given to you at the end of the prompt. "
        f"*Important:* Your output must follow exactly this format, with no additional commentary before or after.\n\n"
        f"*<VIOLATION TYPE>*\n"
        f"<Explanation of the violation>\n\n"
        f"Only output the text above. Do not include extra analysis or preamble.\n\n"
        f"{source}"
    )        

def sanitize_model_name(model):
    return model.replace(":", "-").replace("/", "-")

def build_prompt(strategy, code, language):
    if strategy == "example":
        return example_prompt(code, language)
    elif strategy == "ensemble":
        return ensemble_prompt(code, language)
    elif strategy == "smell":
        return code_smell_prompt(code, language)
    elif strategy == "default":
        return default_prompt(code, language)
    elif strategy == "no":
        return engineer_prompt(code, language)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


def main():
    strategies = ["ensemble", "example", "smell", "default"]
    # model_name = OLLAMA_MODEL
    for model_name in OLLAMA_MODELS:
        safe_model = sanitize_model_name(model_name)

        for data_path in DATA_PATHs:
            with open(data_path, "r") as f:
                data_json = json.load(f)

            dataset = data_json.get("code_examples", data_json)

            # Extract violation name from filename (e.g., "srp" from "data/srp_violations.json")
            violation_name = os.path.splitext(os.path.basename(data_path))[0].split('_')[0]

            for strategy in strategies:
                output_dir = os.path.join("completions/test", f"{violation_name}--{safe_model}--{strategy}")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, "output_test.jsonl")

                with open(output_path, "a") as out_f:
                    for idx, example in enumerate(dataset):
                        start_time = time.time()

                        language = example.get("language", "Java")
                        src = example["input"]
                        # src += "\n This code has the following violation type: %s" % (example["violation"])
                        prompt = build_prompt(strategy, src, language)

                        final_response = run_ollama(prompt, model_name)
                        explanation = extract_explanation(final_response)
                        code_block = "NO FIX VERSION"  # Placeholder for code block extraction

                        duration = time.time() - start_time
                        
                        entry = {
                            "id": idx,
                            "strategy": strategy,
                            "violation_type": violation_name,
                            "model": model_name,
                            "language": language,
                            "input": example["input"],
                            "prompt": prompt,
                            "raw_response": final_response,
                            "violation": extract_violation(final_response),
                            "violation_list": extract_violation(final_response, return_list=True),
                            "explanation": explanation,
                            "solution_code": code_block,
                            "duration_seconds": duration
                        }

                        out_f.write(json.dumps(entry) + "\n")
                        print(f"✓ [{violation_name}] [{strategy}] {model_name} | {idx + 1}/{len(dataset)} in {duration:.2f}s")



if __name__ == "__main__":
    main()