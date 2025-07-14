import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict

def debug_json_structure(json_file_path):
    """
    Debug function to examine the JSON structure
    """
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    print(f"Found {len(data)} top-level keys in JSON data")
    
    # Look at the first key to understand the structure
    first_key = list(data.keys())[0]
    print(f"\nFirst key: {first_key}")
    print(f"Type of data[first_key]: {type(data[first_key])}")
    
    if isinstance(data[first_key], dict):
        print(f"Keys in first entry: {list(data[first_key].keys())}")
        
        # Check each key in the first entry
        for key, value in data[first_key].items():
            print(f"  {key}: {type(value)}")
            if isinstance(value, dict):
                print(f"    Sub-keys: {list(value.keys())[:10]}")  # Show first 10 keys
                if 'violation_results' in value:
                    print(f"    Found violation_results!")
                    vr = value['violation_results']
                    if isinstance(vr, dict):
                        print(f"    Violation types: {list(vr.keys())}")
                        first_vr_key = list(vr.keys())[0]
                        if 'items' in vr[first_vr_key]:
                            print(f"    Found items in {first_vr_key}: {len(vr[first_vr_key]['items'])} items")
                            if len(vr[first_vr_key]['items']) > 0:
                                sample_item = vr[first_vr_key]['items'][0]
                                print(f"    Sample item keys: {list(sample_item.keys())}")
    
    return data

def load_and_process_data(json_file_path):
    """
    Load JSON data and process it to extract violation detection accuracy and other metrics
    """
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    print(f"Found {len(data)} top-level keys in JSON data")
    
    # Initialize data structures for storing different types of results
    accuracy_results = defaultdict(lambda: defaultdict(lambda: {'correct': 0, 'total': 0}))
    f1_results = defaultdict(lambda: defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0}))
    language_results = defaultdict(lambda: defaultdict(lambda: {'correct': 0, 'total': 0}))
    
    # Process each model's results
    for json_key, model_data in data.items():
        print(f"Processing key: {json_key}")
        
        # Extract information from the key
        parts = json_key.split('--')
        if len(parts) >= 3:
            violation_from_key = parts[0].upper()
            model_name = parts[1]
            strategy = parts[2]
        else:
            continue
        
        # Process the nested structure
        if isinstance(model_data, dict):
            # Debug: show what we're looking for vs what we found
            print(f"  Looking for '{violation_from_key.lower()}' in keys: {list(model_data.keys())}")
            
            # Check if we have the strategy as a key (like 'smell', 'example', etc.)
            if strategy in model_data:
                strategy_data = model_data[strategy]
                print(f"  Found strategy data for {strategy}")
                if isinstance(strategy_data, dict) and 'violation_results' in strategy_data:
                    violation_results = strategy_data['violation_results']
                    print(f"  Found violation_results with keys: {list(violation_results.keys())}")
                    
                    for violation_name, violation_data in violation_results.items():
                        if 'items' in violation_data:
                            print(f"  Processing {len(violation_data['items'])} items for {violation_name}")
                            
                            for item in violation_data['items']:
                                level = item.get('level', 'UNKNOWN')
                                expected_violation = item.get('expected_violation', 'UNKNOWN')
                                detected_violation = item.get('detected_violation', 'NONE')
                                violation_match = item.get('violation_match', False)
                                language = item.get('language', 'UNKNOWN')
                                
                                # Accuracy results by difficulty level
                                accuracy_results[expected_violation][level]['total'] += 1
                                if violation_match:
                                    accuracy_results[expected_violation][level]['correct'] += 1
                                
                                # F1 results by strategy and model
                                strategy_model_key = f"{strategy}_{model_name}"
                                if violation_match:
                                    f1_results[expected_violation][strategy_model_key]['tp'] += 1
                                else:
                                    if detected_violation != 'NONE' and detected_violation != expected_violation:
                                        f1_results[expected_violation][strategy_model_key]['fp'] += 1
                                    if detected_violation == 'NONE':
                                        f1_results[expected_violation][strategy_model_key]['fn'] += 1
                                
                                # Language results
                                language_results[language][expected_violation]['total'] += 1
                                if violation_match:
                                    language_results[language][expected_violation]['correct'] += 1
            
            # Look for the nested structure with violation type as key
            elif violation_from_key.lower() in model_data:
                nested_data = model_data[violation_from_key.lower()]
                print(f"  Found nested data for {violation_from_key}")
                if isinstance(nested_data, dict) and 'violation_results' in nested_data:
                    violation_results = nested_data['violation_results']
                    print(f"  Found violation_results with keys: {list(violation_results.keys())}")
                    
                    for violation_name, violation_data in violation_results.items():
                        if 'items' in violation_data:
                            print(f"  Processing {len(violation_data['items'])} items for {violation_name}")
                            
                            for item in violation_data['items']:
                                level = item.get('level', 'UNKNOWN')
                                expected_violation = item.get('expected_violation', 'UNKNOWN')
                                detected_violation = item.get('detected_violation', 'NONE')
                                violation_match = item.get('violation_match', False)
                                language = item.get('language', 'UNKNOWN')
                                
                                # Accuracy results by difficulty level
                                accuracy_results[expected_violation][level]['total'] += 1
                                if violation_match:
                                    accuracy_results[expected_violation][level]['correct'] += 1
                                
                                # F1 results by strategy and model
                                strategy_model_key = f"{strategy}_{model_name}"
                                if violation_match:
                                    f1_results[expected_violation][strategy_model_key]['tp'] += 1
                                else:
                                    if detected_violation != 'NONE' and detected_violation != expected_violation:
                                        f1_results[expected_violation][strategy_model_key]['fp'] += 1
                                    if detected_violation == 'NONE':
                                        f1_results[expected_violation][strategy_model_key]['fn'] += 1
                                
                                # Language results
                                language_results[language][expected_violation]['total'] += 1
                                if violation_match:
                                    language_results[language][expected_violation]['correct'] += 1
            
            # Also check other possible structures...
            elif 'violation_results' in model_data:
                print(f"  Found violation_results directly in model_data")
                violation_results = model_data['violation_results']
                
                for violation_name, violation_data in violation_results.items():
                    if 'items' in violation_data:
                        print(f"  Processing {len(violation_data['items'])} items for {violation_name}")
                        
                        for item in violation_data['items']:
                            level = item.get('level', 'UNKNOWN')
                            expected_violation = item.get('expected_violation', 'UNKNOWN')
                            detected_violation = item.get('detected_violation', 'NONE')
                            violation_match = item.get('violation_match', False)
                            language = item.get('language', 'UNKNOWN')
                            
                            # Accuracy results by difficulty level
                            accuracy_results[expected_violation][level]['total'] += 1
                            if violation_match:
                                accuracy_results[expected_violation][level]['correct'] += 1
                            
                            # F1 results by strategy and model
                            strategy_model_key = f"{strategy}_{model_name}"
                            if violation_match:
                                f1_results[expected_violation][strategy_model_key]['tp'] += 1
                            else:
                                if detected_violation != 'NONE' and detected_violation != expected_violation:
                                    f1_results[expected_violation][strategy_model_key]['fp'] += 1
                                if detected_violation == 'NONE':
                                    f1_results[expected_violation][strategy_model_key]['fn'] += 1
                            
                            # Language results
                            language_results[language][expected_violation]['total'] += 1
                            if violation_match:
                                language_results[language][expected_violation]['correct'] += 1
            else:
                print(f"  No violation_results found. Available keys: {list(model_data.keys())}")
                # Let's look deeper into the structure
                for key, value in list(model_data.items())[:3]:
                    print(f"    {key}: {type(value)}")
                    if isinstance(value, dict) and len(value) < 20:
                        print(f"      Sub-keys: {list(value.keys())}")
        
        # Don't break early - process all entries
        # if len(accuracy_results) == 0 and json_key.count('--') >= 2:
        #     break
    
    print(f"\nProcessed violations: {list(accuracy_results.keys())}")
    return accuracy_results, f1_results, language_results

def calculate_accuracy_matrix(results):
    """
    Calculate accuracy matrix for heatmap by difficulty level
    """
    # Define SOLID principles and difficulty levels
    solid_principles = ['SRP', 'OCP', 'LSP', 'ISP', 'DIP']
    difficulty_levels = ['EASY', 'MODERATE', 'HARD']
    
    # Create accuracy matrix
    accuracy_matrix = []
    violation_labels = []
    
    print(f"Available violations in results: {list(results.keys())}")
    
    for violation in solid_principles:
        if violation in results:
            row = []
            for level in difficulty_levels:
                if level in results[violation]:
                    total = results[violation][level]['total']
                    correct = results[violation][level]['correct']
                    accuracy = (correct / total * 100) if total > 0 else 0
                    row.append(accuracy)
                else:
                    row.append(0)
            accuracy_matrix.append(row)
            violation_labels.append(violation)
    
    # Handle case where no violations are found
    if not accuracy_matrix:
        print("No matching SOLID violations found in the data.")
        print("Creating matrix with available violations...")
        
        # Use whatever violations are available in the data
        for violation in results.keys():
            row = []
            for level in difficulty_levels:
                if level in results[violation]:
                    total = results[violation][level]['total']
                    correct = results[violation][level]['correct']
                    accuracy = (correct / total * 100) if total > 0 else 0
                    row.append(accuracy)
                else:
                    row.append(0)
            accuracy_matrix.append(row)
            violation_labels.append(violation)
    
    # Ensure we have at least some data
    if not accuracy_matrix:
        print("No data available for heatmap generation.")
        return np.array([]), [], []
    
    return np.array(accuracy_matrix), violation_labels, difficulty_levels

def calculate_f1_by_strategy(f1_results):
    """
    Calculate F1 scores averaged by strategy across all models
    """
    solid_principles = ['SRP', 'OCP', 'LSP', 'ISP', 'DIP']
    strategies = ['smell', 'example', 'default', 'ensemble']
    
    # Aggregate results by strategy
    strategy_aggregated = defaultdict(lambda: defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0}))
    
    for violation in f1_results:
        for strategy_model_key in f1_results[violation]:
            if '_' in strategy_model_key:
                strategy = strategy_model_key.split('_')[0]
                tp = f1_results[violation][strategy_model_key]['tp']
                fp = f1_results[violation][strategy_model_key]['fp']
                fn = f1_results[violation][strategy_model_key]['fn']
                
                strategy_aggregated[violation][strategy]['tp'] += tp
                strategy_aggregated[violation][strategy]['fp'] += fp
                strategy_aggregated[violation][strategy]['fn'] += fn
    
    # Calculate F1 matrix
    f1_matrix = []
    violation_labels = []
    
    for violation in solid_principles:
        if violation in strategy_aggregated:
            row = []
            for strategy in strategies:
                if strategy in strategy_aggregated[violation]:
                    tp = strategy_aggregated[violation][strategy]['tp']
                    fp = strategy_aggregated[violation][strategy]['fp']
                    fn = strategy_aggregated[violation][strategy]['fn']
                    
                    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                    row.append(f1_score * 100)
                else:
                    row.append(0)
            f1_matrix.append(row)
            violation_labels.append(violation)
    
    return np.array(f1_matrix), violation_labels, strategies

def calculate_f1_by_model(f1_results):
    """
    Calculate F1 scores averaged by model across all strategies
    """
    solid_principles = ['SRP', 'OCP', 'LSP', 'ISP', 'DIP']
    
    # Extract unique models and clean their names
    model_mapping = {
        'deepseek33b-temp0-latest': 'DeepSeek-33B',
        'qwen2.5-coder32b-temp0-latest': 'Qwen2.5-Coder-32B',
        'gpt-4o-mini': 'GPT-4o-Mini',
        'codellama70b-temp0-latest': 'CodeLlama-70B'
    }
    
    # Aggregate results by model
    model_aggregated = defaultdict(lambda: defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0}))
    
    for violation in f1_results:
        for strategy_model_key in f1_results[violation]:
            if '_' in strategy_model_key:
                parts = strategy_model_key.split('_', 1)
                if len(parts) > 1:
                    model = parts[1]
                    clean_model = model_mapping.get(model, model)
                    
                    tp = f1_results[violation][strategy_model_key]['tp']
                    fp = f1_results[violation][strategy_model_key]['fp']
                    fn = f1_results[violation][strategy_model_key]['fn']
                    
                    model_aggregated[violation][clean_model]['tp'] += tp
                    model_aggregated[violation][clean_model]['fp'] += fp
                    model_aggregated[violation][clean_model]['fn'] += fn
    
    # Get clean model names in order
    clean_models = list(model_mapping.values())
    
    # Calculate F1 matrix
    f1_matrix = []
    violation_labels = []
    
    for violation in solid_principles:
        if violation in model_aggregated:
            row = []
            for model in clean_models:
                if model in model_aggregated[violation]:
                    tp = model_aggregated[violation][model]['tp']
                    fp = model_aggregated[violation][model]['fp']
                    fn = model_aggregated[violation][model]['fn']
                    
                    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                    row.append(f1_score * 100)
                else:
                    row.append(0)
            f1_matrix.append(row)
            violation_labels.append(violation)
    
    return np.array(f1_matrix), violation_labels, clean_models

def calculate_language_matrix(language_results):
    """
    Calculate accuracy matrix by language and SOLID principle
    """
    solid_principles = ['SRP', 'OCP', 'LSP', 'ISP', 'DIP']
    languages = sorted(list(language_results.keys()))
    
    print(f"Found languages: {languages}")
    
    # Filter out UNKNOWN languages
    valid_languages = [lang for lang in languages if lang != 'UNKNOWN']
    
    # Create accuracy matrix with SOLID principles as rows and languages as columns
    accuracy_matrix = []
    
    for violation in solid_principles:
        row = []
        for language in valid_languages:
            if language in language_results and violation in language_results[language]:
                total = language_results[language][violation]['total']
                correct = language_results[language][violation]['correct']
                accuracy = (correct / total * 100) if total > 0 else 0
                row.append(accuracy)
            else:
                row.append(0)
        accuracy_matrix.append(row)
    
    return np.array(accuracy_matrix), solid_principles, valid_languages

def create_heatmap(accuracy_matrix, row_labels, col_labels, 
                  ylabel="Row Labels", xlabel="Column Labels",
                  figsize=(12, 8), 
                  save_path=None, metric_label="Accuracy (%)",
                  cmap='RdYlGn'):
    """
    Create and display the heatmap with improved font sizes and spacing
    """
    # Check if we have valid data
    if accuracy_matrix.size == 0 or len(row_labels) == 0:
        print("No data available for heatmap generation.")
        return
    
    # Set font sizes for better readability in 2-column format
    plt.rcParams.update({
        'font.size': 14,           # Base font size
        'axes.titlesize': 16,      # Title font size
        'axes.labelsize': 14,      # Axis label font size
        'xtick.labelsize': 12,     # X-axis tick label font size
        'ytick.labelsize': 12,     # Y-axis tick label font size
        'legend.fontsize': 12,     # Legend font size
        'figure.titlesize': 16     # Figure title font size
    })
    
    plt.figure(figsize=figsize)
    
    # Create heatmap with adjusted parameters
    ax = sns.heatmap(accuracy_matrix, 
                     annot=True, 
                     fmt='.1f', 
                     cmap=cmap,
                     xticklabels=col_labels,
                     yticklabels=row_labels,
                     cbar_kws={'label': metric_label, 'shrink': 0.8, 'pad': 0.02},  # Reduced pad to decrease space
                     vmin=0, 
                     vmax=100,
                     annot_kws={'size': 11})  # Font size for annotations in cells
    
    # Set labels with increased font size
    plt.xlabel(xlabel, fontsize=14, fontweight='bold')
    plt.ylabel(ylabel, fontsize=14, fontweight='bold')
    
    # Adjust colorbar font size
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=12)
    cbar.set_label(metric_label, fontsize=12)
    
    # Rotate x-axis labels if they are long
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(rotation=0, fontsize=12)
    
    # Adjust layout to prevent clipping
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()

def create_combined_f1_heatmap(f1_model_matrix, f1_strategy_matrix, 
                              model_labels, strategy_labels, violation_labels,
                              save_path=None, figsize=(16, 6)):
    """
    Create a combined heatmap figure with F1 scores by model and strategy side by side
    """
    # Check if we have valid data
    if f1_model_matrix.size == 0 or f1_strategy_matrix.size == 0:
        print("No data available for combined heatmap generation.")
        return
    
    # Set font sizes for better readability
    plt.rcParams.update({
        'font.size': 14,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'figure.titlesize': 16
    })
    
    # Create figure with two subplots and extra bottom margin
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # First heatmap: F1 by Model
    sns.heatmap(f1_model_matrix, 
                annot=True, 
                fmt='.1f', 
                cmap='RdYlGn',
                xticklabels=model_labels,
                yticklabels=violation_labels,
                vmin=0, 
                vmax=100,
                annot_kws={'size': 11},
                cbar=False,  # No colorbar for first plot
                ax=ax1)
    
    ax1.set_xlabel('Model', fontsize=14, fontweight='bold')
    ax1.set_ylabel('SOLID Violation Type', fontsize=14, fontweight='bold')
    ax1.tick_params(axis='x', rotation=45, labelsize=12)
    ax1.tick_params(axis='y', rotation=0, labelsize=12)
    
    # Second heatmap: F1 by Strategy
    im = sns.heatmap(f1_strategy_matrix, 
                     annot=True, 
                     fmt='.1f', 
                     cmap='RdYlGn',
                     xticklabels=strategy_labels,
                     yticklabels=violation_labels,
                     vmin=0, 
                     vmax=100,
                     annot_kws={'size': 11},
                     cbar_kws={'label': 'F1 Score (%)', 'shrink': 0.8, 'pad': 0.02},
                     ax=ax2)
    
    ax2.set_xlabel('Prompt Strategy', fontsize=14, fontweight='bold')
    ax2.set_ylabel('', fontsize=14)  # Empty ylabel for second plot
    ax2.tick_params(axis='x', rotation=45, labelsize=12)
    ax2.tick_params(axis='y', rotation=0, labelsize=12)
    
    # Adjust colorbar font size
    cbar = im.collections[0].colorbar
    cbar.ax.tick_params(labelsize=12)
    cbar.set_label('F1 Score (%)', fontsize=12)
    
    # Adjust layout with more bottom space for rotated labels
    plt.subplots_adjust(bottom=0.2)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()

def create_combined_accuracy_heatmap(accuracy_matrix, language_matrix, 
                                   difficulty_labels, language_labels, 
                                   violation_labels_difficulty, violation_labels_language,
                                   save_path=None, figsize=(16, 6)):
    """
    Create a combined heatmap figure with accuracy by difficulty level and programming language side by side
    """
    # Check if we have valid data
    if accuracy_matrix.size == 0 or language_matrix.size == 0:
        print("No data available for combined accuracy heatmap generation.")
        return
    
    # Set font sizes for better readability
    plt.rcParams.update({
        'font.size': 14,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'figure.titlesize': 16
    })
    
    # Create figure with two subplots (back to equal widths)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # First heatmap: Accuracy by Difficulty Level
    sns.heatmap(accuracy_matrix, 
                annot=True, 
                fmt='.1f', 
                cmap='RdYlGn',
                xticklabels=difficulty_labels,
                yticklabels=violation_labels_difficulty,
                vmin=0, 
                vmax=100,
                annot_kws={'size': 11},
                cbar=False,  # No colorbar for first plot
                ax=ax1)
    
    ax1.set_xlabel('Difficulty Level', fontsize=14, fontweight='bold', ha='center')
    ax1.set_ylabel('SOLID Violation Type', fontsize=14, fontweight='bold')
    ax1.tick_params(axis='x', rotation=45, labelsize=12)
    ax1.tick_params(axis='y', rotation=0, labelsize=12)
    
    # Second heatmap: Accuracy by Programming Language
    im = sns.heatmap(language_matrix, 
                     annot=True, 
                     fmt='.1f', 
                     cmap='RdYlGn',
                     xticklabels=language_labels,
                     yticklabels=violation_labels_language,
                     vmin=0, 
                     vmax=100,
                     annot_kws={'size': 11},
                     cbar_kws={'label': 'Accuracy (%)', 'shrink': 0.8, 'pad': 0.02},
                     ax=ax2)
    
    ax2.set_xlabel('Programming Language', fontsize=14, fontweight='bold', ha='center')
    ax2.set_ylabel('', fontsize=14)  # Empty ylabel for second plot
    ax2.tick_params(axis='x', rotation=45, labelsize=12)
    ax2.tick_params(axis='y', rotation=0, labelsize=12)
    
    # Adjust colorbar font size
    cbar = im.collections[0].colorbar
    cbar.ax.tick_params(labelsize=12)
    cbar.set_label('Accuracy (%)', fontsize=12)
    
    # Adjust layout
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()

def generate_detailed_report(results):
    """
    Generate a detailed text report of the results
    """
    print("=== SOLID Violations Detection Accuracy Report ===\n")
    
    for violation, levels in results.items():
        print(f"{violation} (Liskov Substitution Principle):" if violation == 'LSP' 
              else f"{violation} Violation:")
        print("-" * 40)
        
        for level, stats in levels.items():
            accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {level:>10}: {stats['correct']:>3}/{stats['total']:>3} ({accuracy:>5.1f}%)")
        
        print()

def main():
    """
    Main function to run the heatmap generation
    """
    # Configuration
    json_file_path = "detailed_results_final.json"
    
    try:
        # First, debug the JSON structure
        print("=== Debugging JSON Structure ===")
        debug_json_structure(json_file_path)
        
        # Load and process data
        print("\n=== Loading and processing data ===")
        accuracy_results, f1_results, language_results = load_and_process_data(json_file_path)
        
        # 1. Generate combined accuracy heatmap (difficulty level and programming language)
        print("\n=== Generating Combined Accuracy Heatmap ===")
        accuracy_matrix, violation_labels, difficulty_levels = calculate_accuracy_matrix(accuracy_results)
        lang_matrix, principles, language_labels = calculate_language_matrix(language_results)
        
        if accuracy_matrix.size > 0 and lang_matrix.size > 0:
            generate_detailed_report(accuracy_results)
            
            create_combined_accuracy_heatmap(accuracy_matrix, lang_matrix,
                                           difficulty_levels, language_labels,
                                           violation_labels, principles,
                                           save_path="solid_violations_accuracy_combined.png",
                                           figsize=(16, 6))
            
            # Save individual CSVs
            df_accuracy = pd.DataFrame(accuracy_matrix, 
                                     index=violation_labels, 
                                     columns=difficulty_levels)
            df_accuracy.to_csv("solid_violations_accuracy_by_level.csv")
            
            df_language = pd.DataFrame(lang_matrix, 
                                     index=principles, 
                                     columns=language_labels)
            df_language.to_csv("solid_violations_accuracy_by_language.csv")
            print("Combined accuracy results saved to 'solid_violations_accuracy_combined.png'")
            print("Individual CSV files saved for difficulty and language accuracy")
        else:
            print("Could not generate combined accuracy heatmap - missing data")
            print(f"Accuracy matrix size: {accuracy_matrix.size}")
            print(f"Language matrix size: {lang_matrix.size}")
            
            # Generate individual heatmaps as fallback
            if accuracy_matrix.size > 0:
                create_heatmap(accuracy_matrix, violation_labels, difficulty_levels,
                              ylabel="SOLID Violation Type", 
                              xlabel="Difficulty Level",
                              figsize=(8, 6),
                              save_path="solid_violations_accuracy_by_level.png",
                              metric_label="Accuracy (%)")
            
            if lang_matrix.size > 0:
                create_heatmap(lang_matrix, principles, language_labels,
                              ylabel="SOLID Principle", 
                              xlabel="Programming Language",
                              figsize=(8, 6),
                              save_path="solid_violations_accuracy_by_language.png",
                              metric_label="Accuracy (%)")
        
        # 2. Generate combined F1 score heatmap (both model and strategy in one figure)
        print("\n=== Generating Combined F1 Score Heatmap ===")
        f1_model_matrix, f1_violation_labels_model, models = calculate_f1_by_model(f1_results)
        f1_strategy_matrix, f1_violation_labels, strategies = calculate_f1_by_strategy(f1_results)
        
        if f1_model_matrix.size > 0 and f1_strategy_matrix.size > 0:
            create_combined_f1_heatmap(f1_model_matrix, f1_strategy_matrix,
                                     models, strategies, f1_violation_labels,
                                     save_path="solid_violations_f1_combined.png",
                                     figsize=(16, 6))
            
            # Save individual CSVs
            df_f1_model = pd.DataFrame(f1_model_matrix, 
                                     index=f1_violation_labels_model, 
                                     columns=models)
            df_f1_model.to_csv("solid_violations_f1_by_model.csv")
            
            df_f1_strategy = pd.DataFrame(f1_strategy_matrix, 
                                        index=f1_violation_labels, 
                                        columns=strategies)
            df_f1_strategy.to_csv("solid_violations_f1_by_strategy.csv")
            print("Combined F1 results saved to 'solid_violations_f1_combined.png'")
            print("Individual CSV files saved for model and strategy F1 scores")
        
        # Note: This section was removed since language is now part of the combined accuracy heatmap above
        
        print("\n=== Summary ===")
        print("Generated 2 combined heatmaps:")
        print("1. Combined Accuracy by Difficulty Level and Programming Language")
        print("2. Combined F1 Scores by Model and Strategy")
        
    except FileNotFoundError:
        print(f"Error: Could not find file '{json_file_path}'")
        print("Please make sure the file path is correct.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in the file.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

def process_custom_json_key(json_data, violation, model_clean, strategy):
    """
    Process data using custom JSON key format for all violations
    """
    json_key = f"{violation.lower()}--{model_clean}--{strategy}"
    
    if json_key in json_data:
        model_data = json_data[json_key]
        print(f"Processing key: {json_key}")
        
        # Extract violation results
        if isinstance(model_data, dict):
            # Look for nested structure with violation name
            if violation.lower() in model_data:
                nested_data = model_data[violation.lower()]
                if 'violation_results' in nested_data:
                    return nested_data['violation_results']
            elif 'violation_results' in model_data:
                return model_data['violation_results']
        
        return model_data
    else:
        print(f"Key '{json_key}' not found in data")
        return None

def process_all_violations(json_data):
    """
    Process all SOLID violations across all models and strategies
    """
    violations = ['srp', 'ocp', 'lsp', 'isp', 'dip']
    models = ['deepseek33b-temp0-latest', 'qwen2.5-coder32b-temp0-latest', 'gpt-4o-mini', 'codellama70b-temp0-latest']
    strategies = ['smell', 'example', 'default', 'ensemble']
    
    all_results = {}
    
    for violation in violations:
        for model in models:
            for strategy in strategies:
                json_key = f"{violation}--{model}--{strategy}"
                if json_key in json_data:
                    all_results[json_key] = json_data[json_key]
    
    return all_results

if __name__ == "__main__":
    main()