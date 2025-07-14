import json
import pandas as pd
from collections import defaultdict
from typing import Dict, List, Tuple

def calculate_metrics(tp: int, fp: int, fn: int, tn: int) -> Dict[str, float]:
    """Calculate accuracy, precision, recall, and F1 score from confusion matrix values."""
    total = tp + fp + fn + tn
    
    # Avoid division by zero
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'true_positives': tp,
        'false_positives': fp,
        'false_negatives': fn,
        'true_negatives': tn,
        'total_samples': total
    }

def get_dip_confusion_matrix_correct(results_list: List[Dict]) -> Tuple[int, int, int, int]:
    """
    CORRECT way to calculate confusion matrix using the violation_match field.
    
    For DIP detection:
    - True Positive (TP): violation_match == True (correctly identified DIP)
    - False Negative (FN): violation_match == False (failed to identify DIP)
    - False Positive (FP): Not applicable in DIP-only dataset
    - True Negative (TN): Not applicable in DIP-only dataset
    """
    tp = 0  # True Positives: violation_match == True
    fp = 0  # False Positives: not applicable in DIP-only dataset
    fn = 0  # False Negatives: violation_match == False  
    tn = 0  # True Negatives: not applicable in DIP-only dataset
    
    for item in results_list:
        expected = item.get('expected_violation')
        match = item.get('violation_match', False)
        
        if expected == 'DIP':
            if match == True:
                tp += 1  # Correctly identified as DIP
            else:
                fn += 1  # Failed to correctly identify DIP
    
    return tp, fp, fn, tn

def analyze_dip_results_correct(file_path: str) -> Dict:
    """Analyze DIP violation detection results using the CORRECT method."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Initialize data structures for collecting results
    all_results = []
    
    # Parse folder names to extract model and strategy information
    for folder_name, folder_data in data.items():
        if not folder_data:
            continue
            
        # Parse folder name: dip--model--strategy
        parts = folder_name.split('--')
        if len(parts) >= 3:
            violation_type = parts[0]  # Should be 'dip'
            model = '--'.join(parts[1:-1])  # Handle models with -- in name
            strategy = parts[-1]
        else:
            continue
            
        # Extract results from each strategy
        for strategy_name, strategy_data in folder_data.items():
            if strategy_data.get('status') == 'ERROR':
                continue
                
            # Process each violation result
            for violation_type_key, violation_data in strategy_data.get('violation_results', {}).items():
                if violation_type_key != 'dip':
                    continue
                    
                for item in violation_data.get('items', []):
                    result = {
                        'folder_name': folder_name,
                        'model': model,
                        'strategy': strategy_name,
                        'language': item.get('language', 'UNKNOWN'),
                        'expected_violation': item.get('expected_violation', ''),
                        'detected_violation': item.get('detected_violation', ''),
                        'status': item.get('status', ''),
                        'violation_match': item.get('violation_match', False)
                    }
                    all_results.append(result)
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(all_results)
    
    if df.empty:
        print("No data found in the results file.")
        return {}
    
    print(f"Loaded {len(df)} total results")
    print(f"Models: {sorted(df['model'].unique())}")
    print(f"Strategies: {sorted(df['strategy'].unique())}")
    print(f"Languages: {sorted(df['language'].unique())}")
    
    # Debug: Check violation_match distribution
    print(f"\nViolation Match Distribution:")
    print(f"  True matches: {len(df[df['violation_match'] == True])}")
    print(f"  False matches: {len(df[df['violation_match'] == False])}")
    
    # Debug: Check by strategy
    print(f"\nTrue matches by strategy:")
    for strategy in sorted(df['strategy'].unique()):
        strategy_df = df[df['strategy'] == strategy]
        true_matches = len(strategy_df[strategy_df['violation_match'] == True])
        total = len(strategy_df)
        print(f"  {strategy:12s}: {true_matches:2d}/{total:2d} = {true_matches/total:.3f}")
    
    # Calculate statistics by different groupings
    statistics = {}
    
    # Overall statistics
    tp, fp, fn, tn = get_dip_confusion_matrix_correct(all_results)
    statistics['overall'] = calculate_metrics(tp, fp, fn, tn)
    
    # By strategy
    statistics['by_strategy'] = {}
    for strategy in df['strategy'].unique():
        strategy_results = df[df['strategy'] == strategy].to_dict('records')
        tp, fp, fn, tn = get_dip_confusion_matrix_correct(strategy_results)
        statistics['by_strategy'][strategy] = calculate_metrics(tp, fp, fn, tn)
    
    # By model
    statistics['by_model'] = {}
    for model in df['model'].unique():
        model_results = df[df['model'] == model].to_dict('records')
        tp, fp, fn, tn = get_dip_confusion_matrix_correct(model_results)
        statistics['by_model'][model] = calculate_metrics(tp, fp, fn, tn)
    
    # By language
    statistics['by_language'] = {}
    for language in df['language'].unique():
        language_results = df[df['language'] == language].to_dict('records')
        tp, fp, fn, tn = get_dip_confusion_matrix_correct(language_results)
        statistics['by_language'][language] = calculate_metrics(tp, fp, fn, tn)
    
    # By model and strategy combination
    statistics['by_model_strategy'] = {}
    for model in df['model'].unique():
        statistics['by_model_strategy'][model] = {}
        for strategy in df['strategy'].unique():
            subset_df = df[(df['model'] == model) & (df['strategy'] == strategy)]
            if not subset_df.empty:
                subset_results = subset_df.to_dict('records')
                tp, fp, fn, tn = get_dip_confusion_matrix_correct(subset_results)
                statistics['by_model_strategy'][model][strategy] = calculate_metrics(tp, fp, fn, tn)
    
    # By language and strategy combination
    statistics['by_language_strategy'] = {}
    for language in df['language'].unique():
        statistics['by_language_strategy'][language] = {}
        for strategy in df['strategy'].unique():
            subset_df = df[(df['language'] == language) & (df['strategy'] == strategy)]
            if not subset_df.empty:
                subset_results = subset_df.to_dict('records')
                tp, fp, fn, tn = get_dip_confusion_matrix_correct(subset_results)
                statistics['by_language_strategy'][language][strategy] = calculate_metrics(tp, fp, fn, tn)
    
    # By model and language combination
    statistics['by_model_language'] = {}
    for model in df['model'].unique():
        statistics['by_model_language'][model] = {}
        for language in df['language'].unique():
            subset_df = df[(df['model'] == model) & (df['language'] == language)]
            if not subset_df.empty:
                subset_results = subset_df.to_dict('records')
                tp, fp, fn, tn = get_dip_confusion_matrix_correct(subset_results)
                statistics['by_model_language'][model][language] = calculate_metrics(tp, fp, fn, tn)
    
    return statistics

def print_statistics_summary(stats: Dict):
    """Print a formatted summary of the statistics."""
    
    def format_metrics(metrics):
        return f"Acc: {metrics['accuracy']:.3f}, F1: {metrics['f1_score']:.3f}, " \
               f"Prec: {metrics['precision']:.3f}, Rec: {metrics['recall']:.3f} " \
               f"(TP: {metrics['true_positives']}, FN: {metrics['false_negatives']}, Total: {metrics['total_samples']})"
    
    print("\n" + "="*80)
    print("DIP VIOLATION DETECTION STATISTICS SUMMARY (CORRECTED)")
    print("="*80)
    
    # Overall statistics
    print(f"\nOVERALL PERFORMANCE:")
    print(f"  {format_metrics(stats['overall'])}")
    
    # By strategy
    print(f"\nPERFORMANCE BY STRATEGY:")
    strategy_scores = [(metrics['f1_score'], strategy, metrics) for strategy, metrics in stats['by_strategy'].items()]
    strategy_scores.sort(reverse=True)
    
    for f1, strategy, metrics in strategy_scores:
        print(f"  {strategy:12s}: {format_metrics(metrics)}")
    
    # By model (top 10)
    print(f"\nTOP 10 MODELS BY F1 SCORE:")
    model_scores = [(metrics['f1_score'], model, metrics) for model, metrics in stats['by_model'].items()]
    model_scores.sort(reverse=True)
    
    for i, (f1, model, metrics) in enumerate(model_scores[:10]):
        model_short = model[:30] + "..." if len(model) > 30 else model
        print(f"  {i+1:2d}. {model_short:33s}: {format_metrics(metrics)}")
    
    # By language
    print(f"\nPERFORMANCE BY LANGUAGE:")
    language_scores = [(metrics['f1_score'], language, metrics) for language, metrics in stats['by_language'].items()]
    language_scores.sort(reverse=True)
    
    for f1, language, metrics in language_scores:
        print(f"  {language:12s}: {format_metrics(metrics)}")
    
    # Best performing model-strategy combinations
    print(f"\nTOP 10 MODEL-STRATEGY COMBINATIONS:")
    model_strategy_scores = []
    for model, strategies in stats['by_model_strategy'].items():
        for strategy, metrics in strategies.items():
            if metrics['total_samples'] > 0:
                model_strategy_scores.append((
                    metrics['f1_score'],
                    metrics['accuracy'],
                    model,
                    strategy,
                    metrics
                ))
    
    model_strategy_scores.sort(key=lambda x: (x[0], x[1]), reverse=True)  # Sort by F1, then accuracy
    
    for i, (f1, acc, model, strategy, metrics) in enumerate(model_strategy_scores[:10]):
        model_short = model[:25] + "..." if len(model) > 25 else model
        print(f"  {i+1:2d}. {model_short:28s} + {strategy:12s}: {format_metrics(metrics)}")

def save_detailed_statistics(stats: Dict, output_file: str):
    """Save detailed statistics to a JSON file."""
    
    # Add metadata
    detailed_stats = {
        'analysis_type': 'DIP_VIOLATION_DETECTION_CORRECTED',
        'focus': 'Dependency Inversion Principle violations only',
        'method': 'Using violation_match field for true/false classification',
        'metrics_included': ['accuracy', 'precision', 'recall', 'f1_score'],
        'statistics': stats,
        'summary': {
            'total_samples': stats['overall']['total_samples'],
            'overall_accuracy': stats['overall']['accuracy'],
            'overall_f1': stats['overall']['f1_score'],
            'overall_true_positives': stats['overall']['true_positives'],
            'overall_false_negatives': stats['overall']['false_negatives'],
            'strategies_analyzed': list(stats['by_strategy'].keys()),
            'models_analyzed': list(stats['by_model'].keys()),
            'languages_analyzed': list(stats['by_language'].keys())
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(detailed_stats, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Corrected detailed statistics saved to '{output_file}'")

def create_results_dataframe(stats: Dict) -> pd.DataFrame:
    """Create a pandas DataFrame with key results for easy analysis."""
    
    results_data = []
    
    # Add strategy results
    for strategy, metrics in stats['by_strategy'].items():
        results_data.append({
            'Category': 'Strategy',
            'Name': strategy,
            'Accuracy': metrics['accuracy'],
            'F1_Score': metrics['f1_score'],
            'Precision': metrics['precision'],
            'Recall': metrics['recall'],
            'True_Positives': metrics['true_positives'],
            'False_Negatives': metrics['false_negatives'],
            'Total_Samples': metrics['total_samples']
        })
    
    # Add model results (top 15 by F1 score)
    model_scores = [(metrics['f1_score'], model, metrics) 
                   for model, metrics in stats['by_model'].items()]
    model_scores.sort(reverse=True)
    
    for f1, model, metrics in model_scores[:15]:
        results_data.append({
            'Category': 'Model (Top 15)',
            'Name': model,
            'Accuracy': metrics['accuracy'],
            'F1_Score': metrics['f1_score'],
            'Precision': metrics['precision'],
            'Recall': metrics['recall'],
            'True_Positives': metrics['true_positives'],
            'False_Negatives': metrics['false_negatives'],
            'Total_Samples': metrics['total_samples']
        })
    
    # Add language results
    for language, metrics in stats['by_language'].items():
        results_data.append({
            'Category': 'Language',
            'Name': language,
            'Accuracy': metrics['accuracy'],
            'F1_Score': metrics['f1_score'],
            'Precision': metrics['precision'],
            'Recall': metrics['recall'],
            'True_Positives': metrics['true_positives'],
            'False_Negatives': metrics['false_negatives'],
            'Total_Samples': metrics['total_samples']
        })
    
    return pd.DataFrame(results_data)

# Main execution
if __name__ == "__main__":
    # File path to your results
    results_file = "reprocess_dip/detailed_results_dip_only.json"
    
    # Calculate statistics using CORRECTED method
    print("Analyzing DIP violation detection results (CORRECTED METHOD)...")
    statistics = analyze_dip_results_correct(results_file)
    
    if statistics:
        # Print summary
        print_statistics_summary(statistics)
        
        # Save detailed statistics
        save_detailed_statistics(statistics, "reprocess_dip/dip_statistics_analysis.json")
        
        # Create and save results DataFrame
        results_df = create_results_dataframe(statistics)
        results_df.to_csv("reprocess_dip/dip_results_summary.csv", index=False)
        print(f"✓ Corrected results summary saved to 'dip_results_summary.csv'")
        
        # Print DataFrame
        print(f"\nCORRECTED RESULTS SUMMARY TABLE:")
        print(results_df.to_string(index=False, float_format='%.3f'))
        
    else:
        print("No statistics could be calculated from the results file.")