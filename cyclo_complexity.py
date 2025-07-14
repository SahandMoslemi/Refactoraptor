import json
import os
import re
from typing import Dict, List, Tuple
import pandas as pd

class CyclomaticComplexityCalculator:
    """
    Calculate cyclomatic complexity for Java code snippets.
    Cyclomatic complexity = E - N + 2P
    Where E = edges, N = nodes, P = connected components
    
    For practical purposes, we count decision points + 1:
    - if, else if, while, for, do-while, switch, case, catch, &&, ||, ?:
    """
    
    def __init__(self):
        # Java decision keywords and operators
        self.decision_keywords = [
            r'\bif\b', r'\belse\s+if\b', r'\bwhile\b', r'\bfor\b', 
            r'\bdo\b', r'\bswitch\b', r'\bcase\b', r'\bcatch\b',
            r'\&\&', r'\|\|', r'\?.*:'
        ]
        
    def calculate_complexity(self, code: str) -> int:
        """
        Calculate cyclomatic complexity for a given code snippet.
        """
        if not code or not isinstance(code, str):
            return 1  # Base complexity for empty or invalid code
            
        complexity = 1  # Base complexity
        
        # Remove comments and strings to avoid false positives
        cleaned_code = self._remove_comments_and_strings(code)
        
        # Count decision points
        for pattern in self.decision_keywords:
            matches = re.findall(pattern, cleaned_code, re.IGNORECASE)
            complexity += len(matches)
            
        return complexity
    
    def _remove_comments_and_strings(self, code: str) -> str:
        """
        Remove comments and string literals to avoid counting keywords inside them.
        """
        # Remove single-line comments
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        
        # Remove multi-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Remove string literals (simplified - doesn't handle escaped quotes perfectly)
        code = re.sub(r'"[^"]*"', '""', code)
        code = re.sub(r"'[^']*'", "''", code)
        
        return code
    
    def process_violation_file(self, file_path: str) -> List[Dict]:
        """
        Process a single violation JSON file and calculate complexities.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
        
        results = []
        
        # Handle different JSON structures
        if isinstance(data, dict) and 'code_examples' in data:
            examples = data['code_examples']
        elif isinstance(data, list):
            examples = data
        else:
            print(f"Unexpected JSON structure in {file_path}")
            return []
        
        for i, example in enumerate(examples):
            if not isinstance(example, dict):
                continue
                
            input_code = example.get('input', '')
            output_code = example.get('output', '')
            
            input_complexity = self.calculate_complexity(input_code)
            output_complexity = self.calculate_complexity(output_code)
            
            result = {
                'file': os.path.basename(file_path),
                'example_index': i,
                'language': example.get('language', 'Unknown'),
                'level': example.get('level', 'Unknown'),
                'violation': example.get('violation', 'Unknown'),
                'input_complexity': input_complexity,
                'output_complexity': output_complexity,
                'complexity_reduction': input_complexity - output_complexity,
                'input_code_length': len(input_code) if input_code else 0,
                'output_code_length': len(output_code) if output_code else 0
            }
            
            results.append(result)
        
        return results
    
    def process_dataset_folder(self, dataset_path: str) -> pd.DataFrame:
        """
        Process all *_violations.json files in the dataset folder.
        """
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset folder not found: {dataset_path}")
        
        all_results = []
        
        # Find all *_violations.json files
        violation_files = []
        for file in os.listdir(dataset_path):
            print(file)
            if file.endswith('_violations.json'):
                violation_files.append(os.path.join(dataset_path, file))
        
        if not violation_files:
            print("No *_violations.json files found in the dataset folder")
            return pd.DataFrame()
        
        print(f"Found {len(violation_files)} violation files:")
        for file in violation_files:
            print(f"  - {os.path.basename(file)}")
        
        # Process each file
        for file_path in violation_files:
            print(f"\nProcessing {os.path.basename(file_path)}...")
            results = self.process_violation_file(file_path)
            all_results.extend(results)
            print(f"  Processed {len(results)} examples")
        
        # Create DataFrame
        df = pd.DataFrame(all_results)
        
        if not df.empty:
            print(f"\nTotal examples processed: {len(df)}")
            print(f"Average input complexity: {df['input_complexity'].mean():.2f}")
            print(f"Average output complexity: {df['output_complexity'].mean():.2f}")
            print(f"Average complexity reduction: {df['complexity_reduction'].mean():.2f}")
        
        return df
    
    def generate_summary_report(self, df: pd.DataFrame) -> str:
        """
        Generate a summary report of the complexity analysis.
        """
        if df.empty:
            return "No data to analyze."
        
        report = []
        report.append("CYCLOMATIC COMPLEXITY ANALYSIS REPORT")
        report.append("=" * 50)
        report.append("")
        
        # Overall statistics
        report.append("OVERALL STATISTICS:")
        report.append(f"Total examples: {len(df)}")
        report.append(f"Total files: {df['file'].nunique()}")
        report.append(f"Average input complexity: {df['input_complexity'].mean():.2f}")
        report.append(f"Average output complexity: {df['output_complexity'].mean():.2f}")
        report.append(f"Average complexity reduction: {df['complexity_reduction'].mean():.2f}")
        report.append("")
        
        # By file statistics
        report.append("STATISTICS BY FILE:")
        file_stats = df.groupby('file').agg({
            'input_complexity': ['count', 'mean', 'max'],
            'output_complexity': ['mean', 'max'],
            'complexity_reduction': 'mean'
        }).round(2)
        
        for file in df['file'].unique():
            file_data = df[df['file'] == file]
            report.append(f"\n{file}:")
            report.append(f"  Examples: {len(file_data)}")
            report.append(f"  Avg input complexity: {file_data['input_complexity'].mean():.2f}")
            report.append(f"  Avg output complexity: {file_data['output_complexity'].mean():.2f}")
            report.append(f"  Avg complexity reduction: {file_data['complexity_reduction'].mean():.2f}")
        
        # By violation type
        if 'violation' in df.columns:
            report.append("\nSTATISTICS BY VIOLATION TYPE:")
            violation_stats = df.groupby('violation').agg({
                'input_complexity': 'mean',
                'output_complexity': 'mean',
                'complexity_reduction': 'mean'
            }).round(2)
            
            for violation in df['violation'].unique():
                if violation != 'Unknown':
                    violation_data = df[df['violation'] == violation]
                    report.append(f"\n{violation}:")
                    report.append(f"  Examples: {len(violation_data)}")
                    report.append(f"  Avg input complexity: {violation_data['input_complexity'].mean():.2f}")
                    report.append(f"  Avg output complexity: {violation_data['output_complexity'].mean():.2f}")
                    report.append(f"  Avg complexity reduction: {violation_data['complexity_reduction'].mean():.2f}")
        
        return "\n".join(report)

def main():
    """
    Main function to run the cyclomatic complexity analysis.
    """
    # Initialize calculator
    calculator = CyclomaticComplexityCalculator()
    
    # Set dataset path (modify this to match your folder structure)
    dataset_path = "dataset/groundtruth" 
    
    try:
        # Process all violation files
        df = calculator.process_dataset_folder(dataset_path)
        
        if df.empty:
            print("No data was processed. Please check your dataset folder and file formats.")
            return
        
        # Save results to CSV
        output_file = "cyclomatic_complexity_results.csv"
        df.to_csv(output_file, index=False)
        print(f"\nResults saved to: {output_file}")
        
        # Generate and save summary report
        report = calculator.generate_summary_report(df)
        report_file = "complexity_analysis_report.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"Summary report saved to: {report_file}")
        
        # Print summary to console
        print("\n" + report)
        
        # Display top 10 most complex examples
        print("\nTOP 10 MOST COMPLEX INPUT EXAMPLES:")
        top_complex = df.nlargest(10, 'input_complexity')[['file', 'example_index', 'input_complexity', 'output_complexity', 'complexity_reduction']]
        print(top_complex.to_string(index=False))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()