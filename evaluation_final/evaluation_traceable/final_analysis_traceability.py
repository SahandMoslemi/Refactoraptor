import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict

def load_and_process_data_with_full_traceability(json_file_path):
    """
    Load JSON data and process it to extract detailed confusion matrix metrics
    with full traceability to heatmap generation
    """
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    print(f"Found {len(data)} top-level keys in JSON data")
    
    # Store ALL individual samples for complete traceability
    all_samples = []
    
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
        
        # Clean model name for better readability
        model_mapping = {
            'deepseek33b-temp0-latest': 'DeepSeek-33B',
            'qwen2.5-coder32b-temp0-latest': 'Qwen2.5-Coder-32B',
            'gpt-4o-mini': 'GPT-4o-Mini',
            'codellama70b-temp0-latest': 'CodeLlama-70B'
        }
        clean_model_name = model_mapping.get(model_name, model_name)
        
        # Process the nested structure
        if isinstance(model_data, dict):
            violation_results = None
            
            # Check multiple possible locations for violation_results
            if strategy in model_data and isinstance(model_data[strategy], dict) and 'violation_results' in model_data[strategy]:
                violation_results = model_data[strategy]['violation_results']
            elif violation_from_key.lower() in model_data and isinstance(model_data[violation_from_key.lower()], dict) and 'violation_results' in model_data[violation_from_key.lower()]:
                violation_results = model_data[violation_from_key.lower()]['violation_results']
            elif 'violation_results' in model_data:
                violation_results = model_data['violation_results']
            
            if violation_results:
                print(f"  Found violation_results with keys: {list(violation_results.keys())}")
                
                for violation_name, violation_data in violation_results.items():
                    if 'items' in violation_data:
                        print(f"  Processing {len(violation_data['items'])} items for {violation_name}")
                        
                        # Process each individual sample
                        for item_idx, item in enumerate(violation_data['items']):
                            level = item.get('level', 'UNKNOWN')
                            expected_violation = item.get('expected_violation', 'UNKNOWN')
                            detected_violation = item.get('detected_violation', 'NONE')
                            violation_match = item.get('violation_match', False)
                            language = item.get('language', 'UNKNOWN')
                            
                            # Calculate confusion matrix values
                            # Using violation_match as the primary indicator
                            tp = 1 if violation_match else 0
                            fp = 1 if (not violation_match and detected_violation != 'NONE') else 0
                            fn = 1 if (not violation_match and detected_violation == 'NONE' and expected_violation != 'NONE') else 0
                            tn = 1 if (detected_violation == 'NONE' and expected_violation == 'NONE') else 0
                            
                            # Store complete sample information
                            sample_record = {
                                'sample_id': f"{json_key}_{violation_name}_{item_idx}",
                                'json_key': json_key,
                                'violation_type': expected_violation,
                                'detected_violation': detected_violation,
                                'level': level,
                                'language': language,
                                'model': clean_model_name,
                                'model_raw': model_name,
                                'strategy': strategy,
                                'violation_match': violation_match,
                                'tp': tp,
                                'fp': fp,
                                'fn': fn,
                                'tn': tn,
                                'accuracy': 1 if violation_match else 0,  # Sample-level accuracy
                                # Additional context for debugging
                                'expected_violation_raw': expected_violation,
                                'detected_violation_raw': detected_violation,
                                'processing_group': violation_name
                            }
                            
                            all_samples.append(sample_record)
    
    print(f"\nTotal samples processed: {len(all_samples)}")
    
    return all_samples

def create_comprehensive_csv_export(all_samples, base_filename="comprehensive_results"):
    """
    Create comprehensive CSV exports that directly correspond to heatmap calculations
    """
    if not all_samples:
        print("No samples to export")
        return None, None, None
    
    # Convert to DataFrame
    df = pd.DataFrame(all_samples)
    
    print(f"Creating comprehensive CSV exports with {len(df)} samples")
    
    # 1. Save raw sample-level data
    df.to_csv(f"{base_filename}_samples.csv", index=False)
    print(f"Saved individual samples to {base_filename}_samples.csv")
    
    # 2. Create heatmap-corresponding aggregations
    
    # ACCURACY BY DIFFICULTY LEVEL (corresponds to first heatmap)
    accuracy_by_level = df.groupby(['violation_type', 'level']).agg({
        'accuracy': ['count', 'sum', 'mean'],
        'tp': 'sum',
        'fp': 'sum', 
        'fn': 'sum',
        'tn': 'sum'
    }).reset_index()
    
    # Flatten column names
    accuracy_by_level.columns = ['violation_type', 'level', 'total_samples', 'correct_samples', 'accuracy_pct', 'tp', 'fp', 'fn', 'tn']
    accuracy_by_level['accuracy_pct'] = accuracy_by_level['accuracy_pct'] * 100
    
    # ACCURACY BY LANGUAGE (corresponds to second heatmap)
    accuracy_by_language = df.groupby(['violation_type', 'language']).agg({
        'accuracy': ['count', 'sum', 'mean'],
        'tp': 'sum',
        'fp': 'sum',
        'fn': 'sum', 
        'tn': 'sum'
    }).reset_index()
    
    accuracy_by_language.columns = ['violation_type', 'language', 'total_samples', 'correct_samples', 'accuracy_pct', 'tp', 'fp', 'fn', 'tn']
    accuracy_by_language['accuracy_pct'] = accuracy_by_language['accuracy_pct'] * 100
    
    # F1 BY MODEL (corresponds to F1 heatmap)
    f1_by_model = df.groupby(['violation_type', 'model']).agg({
        'tp': 'sum',
        'fp': 'sum',
        'fn': 'sum',
        'tn': 'sum',
        'accuracy': ['count', 'sum']
    }).reset_index()
    
    f1_by_model.columns = ['violation_type', 'model', 'tp', 'fp', 'fn', 'tn', 'total_samples', 'correct_samples']
    
    # Calculate F1 metrics
    f1_by_model['precision'] = f1_by_model['tp'] / (f1_by_model['tp'] + f1_by_model['fp'])
    f1_by_model['recall'] = f1_by_model['tp'] / (f1_by_model['tp'] + f1_by_model['fn'])
    f1_by_model['f1_score'] = 2 * (f1_by_model['precision'] * f1_by_model['recall']) / (f1_by_model['precision'] + f1_by_model['recall'])
    f1_by_model['f1_score_pct'] = f1_by_model['f1_score'] * 100
    
    # Handle division by zero
    f1_by_model = f1_by_model.fillna(0)
    
    # F1 BY STRATEGY (corresponds to F1 heatmap)
    f1_by_strategy = df.groupby(['violation_type', 'strategy']).agg({
        'tp': 'sum',
        'fp': 'sum',
        'fn': 'sum',
        'tn': 'sum',
        'accuracy': ['count', 'sum']
    }).reset_index()
    
    f1_by_strategy.columns = ['violation_type', 'strategy', 'tp', 'fp', 'fn', 'tn', 'total_samples', 'correct_samples']
    
    # Calculate F1 metrics
    f1_by_strategy['precision'] = f1_by_strategy['tp'] / (f1_by_strategy['tp'] + f1_by_strategy['fp'])
    f1_by_strategy['recall'] = f1_by_strategy['tp'] / (f1_by_strategy['tp'] + f1_by_strategy['fn'])
    f1_by_strategy['f1_score'] = 2 * (f1_by_strategy['precision'] * f1_by_strategy['recall']) / (f1_by_strategy['precision'] + f1_by_strategy['recall'])
    f1_by_strategy['f1_score_pct'] = f1_by_strategy['f1_score'] * 100
    
    # Handle division by zero
    f1_by_strategy = f1_by_strategy.fillna(0)
    
    # Save all aggregated results
    accuracy_by_level.to_csv(f"{base_filename}_accuracy_by_level.csv", index=False)
    accuracy_by_language.to_csv(f"{base_filename}_accuracy_by_language.csv", index=False)
    f1_by_model.to_csv(f"{base_filename}_f1_by_model.csv", index=False)
    f1_by_strategy.to_csv(f"{base_filename}_f1_by_strategy.csv", index=False)
    
    print(f"Saved aggregated results:")
    print(f"  - {base_filename}_accuracy_by_level.csv")
    print(f"  - {base_filename}_accuracy_by_language.csv")
    print(f"  - {base_filename}_f1_by_model.csv")
    print(f"  - {base_filename}_f1_by_strategy.csv")
    
    return accuracy_by_level, accuracy_by_language, f1_by_model, f1_by_strategy

def generate_heatmaps_from_csv_data(accuracy_by_level, accuracy_by_language, f1_by_model, f1_by_strategy):
    """
    Generate heatmaps directly from CSV-aggregated data to ensure perfect correspondence
    """
    # Set up SOLID principles and other categories
    solid_principles = ['SRP', 'OCP', 'LSP', 'ISP', 'DIP']
    difficulty_levels = ['EASY', 'MODERATE', 'HARD']
    
    print("=== Generating Heatmaps from CSV Data ===")
    
    # 1. ACCURACY BY DIFFICULTY LEVEL HEATMAP
    print("Creating accuracy by difficulty level matrix...")
    
    # Create pivot table for accuracy by level
    accuracy_level_pivot = accuracy_by_level.pivot(index='violation_type', columns='level', values='accuracy_pct')
    
    # Ensure we have all SOLID principles and difficulty levels
    accuracy_level_matrix = []
    violation_labels_level = []
    
    for violation in solid_principles:
        if violation in accuracy_level_pivot.index:
            row = []
            for level in difficulty_levels:
                if level in accuracy_level_pivot.columns:
                    value = accuracy_level_pivot.loc[violation, level]
                    row.append(value if not pd.isna(value) else 0)
                else:
                    row.append(0)
            accuracy_level_matrix.append(row)
            violation_labels_level.append(violation)
    
    accuracy_level_matrix = np.array(accuracy_level_matrix)
    
    # 2. ACCURACY BY LANGUAGE HEATMAP
    print("Creating accuracy by language matrix...")
    
    # Create pivot table for accuracy by language
    accuracy_lang_pivot = accuracy_by_language.pivot(index='violation_type', columns='language', values='accuracy_pct')
    
    # Get available languages (excluding UNKNOWN)
    available_languages = [lang for lang in accuracy_lang_pivot.columns if lang != 'UNKNOWN']
    
    accuracy_lang_matrix = []
    violation_labels_lang = []
    
    for violation in solid_principles:
        if violation in accuracy_lang_pivot.index:
            row = []
            for lang in available_languages:
                if lang in accuracy_lang_pivot.columns:
                    value = accuracy_lang_pivot.loc[violation, lang]
                    row.append(value if not pd.isna(value) else 0)
                else:
                    row.append(0)
            accuracy_lang_matrix.append(row)
            violation_labels_lang.append(violation)
    
    accuracy_lang_matrix = np.array(accuracy_lang_matrix)
    
    # 3. F1 BY MODEL HEATMAP
    print("Creating F1 by model matrix...")
    
    f1_model_pivot = f1_by_model.pivot(index='violation_type', columns='model', values='f1_score_pct')
    available_models = list(f1_model_pivot.columns)
    
    f1_model_matrix = []
    violation_labels_f1_model = []
    
    for violation in solid_principles:
        if violation in f1_model_pivot.index:
            row = []
            for model in available_models:
                if model in f1_model_pivot.columns:
                    value = f1_model_pivot.loc[violation, model]
                    row.append(value if not pd.isna(value) else 0)
                else:
                    row.append(0)
            f1_model_matrix.append(row)
            violation_labels_f1_model.append(violation)
    
    f1_model_matrix = np.array(f1_model_matrix)
    
    # 4. F1 BY STRATEGY HEATMAP
    print("Creating F1 by strategy matrix...")
    
    f1_strategy_pivot = f1_by_strategy.pivot(index='violation_type', columns='strategy', values='f1_score_pct')
    available_strategies = list(f1_strategy_pivot.columns)
    
    f1_strategy_matrix = []
    violation_labels_f1_strategy = []
    
    for violation in solid_principles:
        if violation in f1_strategy_pivot.index:
            row = []
            for strategy in available_strategies:
                if strategy in f1_strategy_pivot.columns:
                    value = f1_strategy_pivot.loc[violation, strategy]
                    row.append(value if not pd.isna(value) else 0)
                else:
                    row.append(0)
            f1_strategy_matrix.append(row)
            violation_labels_f1_strategy.append(violation)
    
    f1_strategy_matrix = np.array(f1_strategy_matrix)
    
    return {
        'accuracy_level': (accuracy_level_matrix, violation_labels_level, difficulty_levels),
        'accuracy_language': (accuracy_lang_matrix, violation_labels_lang, available_languages),
        'f1_model': (f1_model_matrix, violation_labels_f1_model, available_models),
        'f1_strategy': (f1_strategy_matrix, violation_labels_f1_strategy, available_strategies)
    }

def create_heatmap_with_csv_traceability(matrix, row_labels, col_labels, csv_data, grouping_cols,
                                        ylabel="Row Labels", xlabel="Column Labels",
                                        figsize=(12, 8), save_path=None, metric_label="Value (%)",
                                        cmap='RdYlGn'):
    """
    Create heatmap and save a CSV showing exactly how each cell value was calculated
    """
    if matrix.size == 0 or len(row_labels) == 0:
        print("No data available for heatmap generation.")
        return
    
    # Create traceability CSV showing calculation for each cell
    traceability_data = []
    
    for i, row_label in enumerate(row_labels):
        for j, col_label in enumerate(col_labels):
            cell_value = matrix[i, j]
            
            # Find corresponding rows in CSV data
            if len(grouping_cols) == 2:
                mask = (csv_data[grouping_cols[0]] == row_label) & (csv_data[grouping_cols[1]] == col_label)
            else:
                # Handle other grouping scenarios
                mask = csv_data[grouping_cols[0]] == row_label
                for k, group_col in enumerate(grouping_cols[1:], 1):
                    if k == 1:
                        mask = mask & (csv_data[group_col] == col_label)
            
            matching_rows = csv_data[mask]
            
            if len(matching_rows) > 0:
                # Get the calculation details
                total_samples = len(matching_rows) if 'total_samples' not in matching_rows.columns else matching_rows['total_samples'].iloc[0]
                if 'accuracy_pct' in matching_rows.columns:
                    calculated_value = matching_rows['accuracy_pct'].iloc[0]
                    tp = matching_rows['tp'].iloc[0] if 'tp' in matching_rows.columns else 0
                    fp = matching_rows['fp'].iloc[0] if 'fp' in matching_rows.columns else 0
                    fn = matching_rows['fn'].iloc[0] if 'fn' in matching_rows.columns else 0
                    tn = matching_rows['tn'].iloc[0] if 'tn' in matching_rows.columns else 0
                elif 'f1_score_pct' in matching_rows.columns:
                    calculated_value = matching_rows['f1_score_pct'].iloc[0]
                    tp = matching_rows['tp'].iloc[0]
                    fp = matching_rows['fp'].iloc[0]
                    fn = matching_rows['fn'].iloc[0]
                    tn = matching_rows['tn'].iloc[0]
                else:
                    calculated_value = cell_value
                    tp = fp = fn = tn = 0
                
                traceability_data.append({
                    'heatmap_row': row_label,
                    'heatmap_col': col_label,
                    'heatmap_value': cell_value,
                    'csv_calculated_value': calculated_value,
                    'total_samples': total_samples,
                    'tp': tp,
                    'fp': fp,
                    'fn': fn,
                    'tn': tn,
                    'matches_csv': abs(cell_value - calculated_value) < 0.01
                })
            else:
                traceability_data.append({
                    'heatmap_row': row_label,
                    'heatmap_col': col_label,
                    'heatmap_value': cell_value,
                    'csv_calculated_value': 0,
                    'total_samples': 0,
                    'tp': 0,
                    'fp': 0,
                    'fn': 0,
                    'tn': 0,
                    'matches_csv': cell_value == 0
                })
    
    # Save traceability CSV
    traceability_df = pd.DataFrame(traceability_data)
    traceability_filename = save_path.replace('.png', '_traceability.csv') if save_path else 'heatmap_traceability.csv'
    traceability_df.to_csv(traceability_filename, index=False)
    print(f"Saved heatmap traceability to {traceability_filename}")
    
    # Create the heatmap
    plt.rcParams.update({
        'font.size': 14,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'figure.titlesize': 16
    })
    
    plt.figure(figsize=figsize)
    
    ax = sns.heatmap(matrix, 
                     annot=True, 
                     fmt='.1f', 
                     cmap=cmap,
                     xticklabels=col_labels,
                     yticklabels=row_labels,
                     cbar_kws={'label': metric_label, 'shrink': 0.8, 'pad': 0.02},
                     vmin=0, 
                     vmax=100,
                     annot_kws={'size': 11})
    
    plt.xlabel(xlabel, fontsize=14, fontweight='bold')
    plt.ylabel(ylabel, fontsize=14, fontweight='bold')
    
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=12)
    cbar.set_label(metric_label, fontsize=12)
    
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(rotation=0, fontsize=12)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()
    
    return traceability_df

def main():
    """
    Main function with full traceability from CSV to heatmaps
    """
    json_file_path = "detailed_results_with_levels_all_mapped.json"
    
    try:
        print("=== Loading and processing data with full traceability ===")
        all_samples = load_and_process_data_with_full_traceability(json_file_path)
        
        if not all_samples:
            print("No samples found in the data")
            return
        
        print("\n=== Creating comprehensive CSV exports ===")
        accuracy_by_level, accuracy_by_language, f1_by_model, f1_by_strategy = create_comprehensive_csv_export(all_samples)
        
        print("\n=== Generating heatmaps from CSV data ===")
        heatmap_data = generate_heatmaps_from_csv_data(accuracy_by_level, accuracy_by_language, f1_by_model, f1_by_strategy)
        
        print("\n=== Creating traceable heatmaps ===")
        
        # 1. Accuracy by difficulty level with traceability
        acc_level_matrix, acc_level_rows, acc_level_cols = heatmap_data['accuracy_level']
        if acc_level_matrix.size > 0:
            create_heatmap_with_csv_traceability(
                acc_level_matrix, acc_level_rows, acc_level_cols, accuracy_by_level,
                ['violation_type', 'level'],
                ylabel="SOLID Violation Type", xlabel="Difficulty Level",
                figsize=(10, 6), save_path="accuracy_by_level_traceable.png",
                metric_label="Accuracy (%)"
            )
        
        # 2. Accuracy by language with traceability
        acc_lang_matrix, acc_lang_rows, acc_lang_cols = heatmap_data['accuracy_language']
        if acc_lang_matrix.size > 0:
            create_heatmap_with_csv_traceability(
                acc_lang_matrix, acc_lang_rows, acc_lang_cols, accuracy_by_language,
                ['violation_type', 'language'],
                ylabel="SOLID Violation Type", xlabel="Programming Language",
                figsize=(12, 6), save_path="accuracy_by_language_traceable.png",
                metric_label="Accuracy (%)"
            )
        
        # 3. F1 by model with traceability
        f1_model_matrix, f1_model_rows, f1_model_cols = heatmap_data['f1_model']
        if f1_model_matrix.size > 0:
            create_heatmap_with_csv_traceability(
                f1_model_matrix, f1_model_rows, f1_model_cols, f1_by_model,
                ['violation_type', 'model'],
                ylabel="SOLID Violation Type", xlabel="Model",
                figsize=(12, 6), save_path="f1_by_model_traceable.png",
                metric_label="F1 Score (%)"
            )
        
        # 4. F1 by strategy with traceability
        f1_strategy_matrix, f1_strategy_rows, f1_strategy_cols = heatmap_data['f1_strategy']
        if f1_strategy_matrix.size > 0:
            create_heatmap_with_csv_traceability(
                f1_strategy_matrix, f1_strategy_rows, f1_strategy_cols, f1_by_strategy,
                ['violation_type', 'strategy'],
                ylabel="SOLID Violation Type", xlabel="Strategy",
                figsize=(10, 6), save_path="f1_by_strategy_traceable.png",
                metric_label="F1 Score (%)"
            )
        
        print("\n=== Summary ===")
        print("Generated files with full traceability:")
        print("1. comprehensive_results_samples.csv - All individual samples")
        print("2. comprehensive_results_accuracy_by_level.csv - Aggregated accuracy by difficulty")
        print("3. comprehensive_results_accuracy_by_language.csv - Aggregated accuracy by language") 
        print("4. comprehensive_results_f1_by_model.csv - Aggregated F1 by model")
        print("5. comprehensive_results_f1_by_strategy.csv - Aggregated F1 by strategy")
        print("6. *_traceable.png - Heatmaps with corresponding traceability CSVs")
        print("7. *_traceability.csv - Shows exactly how each heatmap cell was calculated")
        
        print(f"\nProcessed {len(all_samples)} total samples")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()