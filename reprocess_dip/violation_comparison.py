import re
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import difflib
from collections import defaultdict
from datetime import datetime

class SOLIDViolationComparator:
    def __init__(self, output_base_dir: str, ground_truth_dir: str):
        self.output_base_dir = Path(output_base_dir)
        self.ground_truth_dir = Path(ground_truth_dir)
        # Updated to only process DIP violations
        self.violation_types = ['dip']  # Only DIP
        self.prompt_types = ['default', 'ensemble', 'example', 'smell']
        self.results = []
        self.multiple_violations_cases = []  # Store cases with multiple violations
        self.failed_extraction_cases = []  # Store cases where regex failed to extract
        self.extracted_patterns = {
            'violations': defaultdict(list),
            'code_structures': defaultdict(list),
            'language_patterns': defaultdict(list),
            'refactoring_patterns': defaultdict(list)
        }
        
        # Strategy-specific regex patterns for violation extraction
        self.strategy_regex_patterns = {
            # For ensemble: Look for "MOST IMPACTFUL VIOLATION:" followed by the violation
            # Also supports the original asterisks format as fallback
            'ensemble': r"(?:MOST IMPACTFUL VIOLATION:\s*([A-Z]{2,3}|NONE)|\*\*([A-Z]{2,3}|NONE)\*\*)",
            'example': r"\*\*([A-Z]{2,3}|NONE)\*\*", 
            'smell': r"\*\*([A-Z]{2,3}|NONE)\*\*",
            'default': r"\b(SRP|OCP|LSP|ISP|DIP|NONE)\b"
        }
        
        # Enhanced regex patterns for SOLID violations
        self.regex_patterns = {
            # Basic violation detection - updated to catch all SOLID principles
            'violation_extraction': r'\*\*([A-Z]{3})\*\*',
            'none_response': r'\*\*NONE\*\*',
            
            # Code block extraction by language
            'java_code_block': r'```java\n(.*?)\n```',
            'python_code_block': r'```python\n(.*?)\n```',
            'kotlin_code_block': r'```kotlin\n(.*?)\n```',
            'csharp_code_block': r'```(?:c#|csharp)\n(.*?)\n```',
            'generic_code_block': r'```(?:\w+)?\n(.*?)\n```',
            
            # Language-specific patterns
            'java_interface': r'(?:public\s+)?interface\s+(\w+)',
            'java_class': r'(?:public\s+)?class\s+(\w+)(?:\s+implements\s+(\w+))?',
            'java_constructor_injection': r'public\s+\w+\s*\(\s*\w+\s+\w+\s*\)',
            
            'python_class': r'class\s+(\w+)(?:\s*\([^)]*\))?:',
            'python_init_injection': r'def\s+__init__\s*\(\s*self\s*,\s*\w+',
            
            'kotlin_interface': r'interface\s+(\w+)',
            'kotlin_class': r'class\s+(\w+)(?:\s*:\s*(\w+))?',
            'kotlin_constructor': r'constructor\s*\(\s*\w+\s*:\s*\w+\s*\)',
            
            'csharp_interface': r'(?:public\s+)?interface\s+I(\w+)',
            'csharp_class': r'(?:public\s+)?class\s+(\w+)(?:\s*:\s*I?(\w+))?',
            'csharp_constructor_injection': r'public\s+\w+\s*\(\s*I?\w+\s+\w+\s*\)',
            
            # SOLID-specific patterns - Only DIP patterns needed now
            'dip_patterns': {
                'interface_creation': r'(?:interface|abstract\s+class)\s+\w+',
                'dependency_injection': r'(?:constructor|__init__|init)\s*\([^)]*\w+\s+\w+',
                'abstraction_usage': r'private\s+(?:final\s+)?\w+\s+\w+;|self\.\w+\s*=\s*\w+',
            },
            
            # Quality assessment patterns
            'good_practices': {
                'proper_naming': r'(?:I[A-Z]\w+|Abstract\w+|\w+Interface)',
                'constructor_injection': r'(?:constructor|__init__)\s*\([^)]*\w+Service\w*',
                'composition_over_inheritance': r'private\s+(?:final\s+)?\w+\s+\w+;',
            }
        }
    
    def load_jsonl_file(self, file_path: Path) -> List[Dict]:
        """Load JSONL file and return list of dictionaries."""
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data.append(json.loads(line))
            return data
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return []
    
    def extract_violations_by_strategy(self, text: str, strategy: str) -> List[str]:
        """Extract violations using strategy-specific regex patterns."""
        # Get the appropriate regex pattern for the strategy
        pattern = self.strategy_regex_patterns.get(strategy, self.strategy_regex_patterns['default'])
        
        # Use a set to collect unique violations
        unique_violations = set()
        
        if strategy == 'ensemble':
            # Special handling for ensemble pattern which has multiple capture groups
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Group 1 is for "MOST IMPACTFUL VIOLATION:" format
                # Group 2 is for "**VIOLATION**" format
                violation = match.group(1) or match.group(2)
                if violation:
                    violation = violation.upper()
                    # Validate it's a known SOLID principle or NONE
                    if violation in ['SRP', 'OCP', 'LSP', 'ISP', 'DIP', 'NONE']:
                        unique_violations.add(violation)
        else:
            # Standard handling for other strategies
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                violation = match.upper()
                # Validate it's a known SOLID principle or NONE
                if violation in ['SRP', 'OCP', 'LSP', 'ISP', 'DIP', 'NONE']:
                    unique_violations.add(violation)
        
        # Convert set back to list
        violations_found = list(unique_violations)
        
        return violations_found

    def extract_violation_type(self, text: str, strategy: str, output_item: Dict) -> Optional[str]:
        """Extract violation type using strategy-specific patterns with strict validation."""
        violations_found = self.extract_violations_by_strategy(text, strategy)
        
        # Case 1: No violations found - FAIL and extract for manual review
        if not violations_found:
            failed_case = {
                'id': output_item.get('id'),
                'model': output_item.get('model', 'UNKNOWN'),
                'strategy': strategy,
                'language': output_item.get('language', 'UNKNOWN'),
                'expected_violation': output_item.get('violation_type', '').upper(),
                'reason': 'NO_MATCH',
                'pattern_used': self.strategy_regex_patterns.get(strategy),
                'raw_response': text,
                'input_code': output_item.get('input', ''),
                'folder_source': f"{output_item.get('violation_type', 'unknown').lower()}--{output_item.get('model', 'unknown')}--{strategy}"
            }
            self.failed_extraction_cases.append(failed_case)
            return None
        
        # Case 2: Multiple UNIQUE violations found - FAIL and extract for manual review
        if len(violations_found) > 1:
            multiple_violation_case = {
                'id': output_item.get('id'),
                'model': output_item.get('model', 'UNKNOWN'),
                'strategy': strategy,
                'language': output_item.get('language', 'UNKNOWN'),
                'expected_violation': output_item.get('violation_type', '').upper(),
                'all_violations_found': violations_found,
                'reason': 'MULTIPLE_UNIQUE_VIOLATIONS',
                'pattern_used': self.strategy_regex_patterns.get(strategy),
                'raw_response': text,
                'input_code': output_item.get('input', ''),
                'folder_source': f"{output_item.get('violation_type', 'unknown').lower()}--{output_item.get('model', 'unknown')}--{strategy}"
            }
            self.multiple_violations_cases.append(multiple_violation_case)
            return None
        
        # Case 3: Exactly one UNIQUE violation found - SUCCESS
        violation = violations_found[0]
        self.extracted_patterns['violations']['detected'].append(violation)
        return violation
    
    def extract_code_blocks_by_language(self, text: str) -> Dict[str, List[str]]:
        """Extract code blocks organized by programming language."""
        code_blocks = {}
        
        languages = ['java', 'python', 'kotlin', 'csharp']
        for lang in languages:
            pattern_key = f'{lang}_code_block'
            if pattern_key in self.regex_patterns:
                blocks = re.findall(self.regex_patterns[pattern_key], text, re.DOTALL | re.IGNORECASE)
                if blocks:
                    code_blocks[lang] = blocks
                    self.extracted_patterns['language_patterns'][lang].extend(blocks)
        
        # Generic code block extraction as fallback
        generic_blocks = re.findall(self.regex_patterns['generic_code_block'], text, re.DOTALL | re.IGNORECASE)
        if generic_blocks and not code_blocks:
            code_blocks['generic'] = generic_blocks
        
        return code_blocks
    
    def analyze_language_specific_patterns(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze language-specific patterns in code."""
        analysis = {
            'interfaces': [],
            'classes': [],
            'has_dependency_injection': False,
            'language_quality_score': 0
        }
        
        if language == 'java':
            analysis['interfaces'] = re.findall(self.regex_patterns['java_interface'], code, re.IGNORECASE)
            analysis['classes'] = re.findall(self.regex_patterns['java_class'], code, re.IGNORECASE)
            analysis['has_dependency_injection'] = bool(
                re.search(self.regex_patterns['java_constructor_injection'], code, re.IGNORECASE)
            )
        elif language == 'python':
            analysis['classes'] = re.findall(self.regex_patterns['python_class'], code, re.IGNORECASE)
            analysis['has_dependency_injection'] = bool(
                re.search(self.regex_patterns['python_init_injection'], code, re.IGNORECASE)
            )
        elif language == 'kotlin':
            analysis['interfaces'] = re.findall(self.regex_patterns['kotlin_interface'], code, re.IGNORECASE)
            analysis['classes'] = re.findall(self.regex_patterns['kotlin_class'], code, re.IGNORECASE)
            analysis['has_dependency_injection'] = bool(
                re.search(self.regex_patterns['kotlin_constructor'], code, re.IGNORECASE)
            )
        elif language in ['csharp', 'c#']:
            analysis['interfaces'] = re.findall(self.regex_patterns['csharp_interface'], code, re.IGNORECASE)
            analysis['classes'] = re.findall(self.regex_patterns['csharp_class'], code, re.IGNORECASE)
            analysis['has_dependency_injection'] = bool(
                re.search(self.regex_patterns['csharp_constructor_injection'], code, re.IGNORECASE)
            )
        
        # Calculate quality score
        score = 0
        if analysis['interfaces']:
            score += 2
        if analysis['classes']:
            score += 1
        if analysis['has_dependency_injection']:
            score += 3
        
        analysis['language_quality_score'] = score
        return analysis
    
    def analyze_violation_specific_patterns(self, code: str, violation_type: str) -> Dict[str, Any]:
        """Analyze patterns specific to violation types - Only DIP patterns needed."""
        analysis = {
            'violation_addressed': False,
            'refactoring_quality': 'low',
            'specific_patterns': []
        }
        
        # Only process DIP since that's what we're focusing on
        if violation_type == 'DIP':
            patterns = self.regex_patterns['dip_patterns']
            for pattern_name, pattern in patterns.items():
                matches = re.findall(pattern, code, re.IGNORECASE | re.DOTALL)
                if matches:
                    analysis['specific_patterns'].append({
                        'pattern': pattern_name,
                        'matches': matches
                    })
                    self.extracted_patterns['refactoring_patterns']['dip'].extend(matches)
            
            # DIP quality assessment
            has_interface = bool(re.search(patterns['interface_creation'], code, re.IGNORECASE))
            has_injection = bool(re.search(patterns['dependency_injection'], code, re.IGNORECASE))
            
            if has_interface and has_injection:
                analysis['refactoring_quality'] = 'high'
                analysis['violation_addressed'] = True
            elif has_interface or has_injection:
                analysis['refactoring_quality'] = 'medium'
        
        return analysis
    
    def compare_single_output(self, output_item: Dict, strategy: str) -> Dict:
        """Compare single output item using built-in ground truth."""
        output_id = output_item.get('id')
        raw_response = output_item.get('raw_response', '')
        # Use the violation_type from the output file as ground truth
        expected_violation = output_item.get('violation_type', '').upper()
        language = output_item.get('language', 'UNKNOWN')
        
        # Extract violation using strategy-specific pattern
        extracted_violation = self.extract_violation_type(raw_response, strategy, output_item)
        
        # If extraction failed (None returned), mark as FAIL
        if extracted_violation is None:
            return {
                'id': output_id,
                'status': 'FAIL',
                'language': language,
                'expected_violation': expected_violation,
                'detected_violation': None,
                'failure_reason': 'EXTRACTION_FAILED',
                'violation_match': False,
                'code_blocks': {},
                'language_analysis': {},
                'violation_analysis': {},
                'response_length': len(raw_response),
                'model': output_item.get('model', 'UNKNOWN'),
                'strategy': strategy
            }
        
        # Compare violation detection
        violation_match = extracted_violation == expected_violation
        
        # Extract and analyze code blocks by language
        code_blocks = self.extract_code_blocks_by_language(raw_response)
        
        # Analyze language-specific patterns
        language_analysis = {}
        violation_analysis = {}
        
        if code_blocks and extracted_violation and extracted_violation != 'NONE':
            for lang, blocks in code_blocks.items():
                if blocks:
                    primary_code = blocks[0]
                    language_analysis[lang] = self.analyze_language_specific_patterns(primary_code, lang)
                    violation_analysis[lang] = self.analyze_violation_specific_patterns(
                        primary_code, extracted_violation
                    )
        
        return {
            'id': output_id,
            'status': 'PASS' if violation_match else 'FAIL',
            'language': language,
            'expected_violation': expected_violation,
            'detected_violation': extracted_violation,
            'violation_match': violation_match,
            'failure_reason': None if violation_match else 'WRONG_VIOLATION',
            'code_blocks': code_blocks,
            'language_analysis': language_analysis,
            'violation_analysis': violation_analysis,
            'response_length': len(raw_response),
            'model': output_item.get('model', 'UNKNOWN'),
            'strategy': strategy
        }
    
    def process_violation_type(self, violation_type: str, violation_groups: Dict, results: Dict, strategy: str) -> None:
        """Process a single violation type and update results."""
        # Compare each output item (no need for separate ground truth)
        violation_results = []
        for output_item in violation_groups[violation_type]:
            result = self.compare_single_output(output_item, strategy)
            violation_results.append(result)
            
            # Update overall stats
            if result['status'] == 'PASS':
                results['overall_stats']['total_pass'] += 1
            elif result['status'] == 'FAIL':
                results['overall_stats']['total_fail'] += 1
            else:
                results['overall_stats']['total_error'] += 1
            
            # Track languages
            lang = result.get('language', 'UNKNOWN')
            results['overall_stats']['languages'][lang] += 1
        
        # Calculate violation-specific stats
        pass_count = sum(1 for r in violation_results if r['status'] == 'PASS')
        fail_count = sum(1 for r in violation_results if r['status'] == 'FAIL')
        error_count = sum(1 for r in violation_results if r['status'] == 'ERROR')
        
        results['violation_results'][violation_type] = {
            'items': violation_results,
            'stats': {
                'total': len(violation_results),
                'pass': pass_count,
                'fail': fail_count,
                'error': error_count,
                'accuracy': pass_count / len(violation_results) if violation_results else 0
            }
        }
        
        print(f"    {violation_type.upper()}: {pass_count}/{len(violation_results)} passed ({pass_count/len(violation_results)*100:.1f}%)")

    def compare_model_outputs(self, model_folder: str, prompt_type: str) -> Dict:
        """Compare outputs for a specific model and prompt type."""
        output_file = self.output_base_dir / model_folder / 'output_test.jsonl'
        
        if not output_file.exists():
            return {
                'model': model_folder,
                'prompt_type': prompt_type,
                'status': 'ERROR',
                'error': f'Output file not found: {output_file}'
            }
        
        # Load output data
        output_data = self.load_jsonl_file(output_file)
        
        if not output_data:
            return {
                'model': model_folder,
                'prompt_type': prompt_type,
                'status': 'ERROR',
                'error': f'No data loaded from {output_file}'
            }
        
        print(f"  Loaded {len(output_data)} items from {output_file.name}")
        
        # Group outputs by violation type - only keep DIP
        violation_groups = defaultdict(list)
        for item in output_data:
            violation_type = item.get('violation_type', '').lower()
            if violation_type == 'dip':  # Only process DIP violations
                violation_groups[violation_type].append(item)
        
        print(f"  DIP items found: {len(violation_groups.get('dip', []))}")
        
        results = {
            'model': model_folder,
            'prompt_type': prompt_type,
            'total_items': len(violation_groups.get('dip', [])),
            'violation_results': {},
            'overall_stats': {
                'total_pass': 0,
                'total_fail': 0,
                'total_error': 0,
                'languages': defaultdict(int)
            }
        }
        
        # Process only DIP violation type
        if 'dip' in violation_groups and violation_groups['dip']:
            print(f"  Processing {len(violation_groups['dip'])} DIP items")
            self.process_violation_type('dip', violation_groups, results, prompt_type)
        else:
            print(f"  No DIP items found in {model_folder}")
        
        return results
    
    def parse_folder_name(self, folder_name: str) -> Dict[str, str]:
        """Parse folder name to extract violation type, model, and strategy."""
        # Expected format: violation--model--strategy
        parts = folder_name.split('--')
        if len(parts) >= 3:
            return {
                'violation_type': parts[0],
                'model': '--'.join(parts[1:-1]),  # Handle models with -- in name
                'strategy': parts[-1]
            }
        return {
            'violation_type': 'unknown',
            'model': folder_name,
            'strategy': 'unknown'
        }

    def run_full_comparison(self) -> Dict:
        """Run comparison for all models and prompt types - DIP only."""
        all_results = {}
        
        # Get all model folders - only look for DIP folders
        all_folders = [d.name for d in self.output_base_dir.iterdir() if d.is_dir()]
        
        # Look for folders starting with 'dip--'
        dip_folders = [folder for folder in all_folders if folder.startswith('dip--')]
        
        print(f"Found DIP folders: {len(dip_folders)}")
        for folder in dip_folders[:5]:  # Show first 5 as example
            print(f"  {folder}")
        
        if not dip_folders:
            print("No DIP folders found!")
            return {}
        
        print(f"Processing {len(dip_folders)} DIP model folders...")
        print("Note: Using built-in ground truth from violation_type field")
        
        for model_folder in dip_folders:
            # Parse the folder name to get the actual strategy
            folder_info = self.parse_folder_name(model_folder)
            actual_strategy = folder_info['strategy']
            
            print(f"Processing {model_folder} (strategy: {actual_strategy})...")
            
            # Only process the actual strategy from the folder name
            result = self.compare_model_outputs(model_folder, actual_strategy)
            
            # Ensure result is not None
            if result is None:
                result = {
                    'model': model_folder,
                    'prompt_type': actual_strategy,
                    'status': 'ERROR',
                    'error': 'Comparison returned None'
                }
            
            # Store result using the folder name as key
            all_results[model_folder] = {
                actual_strategy: result
            }
        
        return all_results
    
    def calculate_detailed_statistics(self, all_results: Dict) -> Dict:
        """Calculate comprehensive statistics including F1 scores for DIP only."""
        from collections import defaultdict
        
        # Initialize counters for DIP only
        violation_stats = {}
        overall_stats = {
            'true_positives': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'true_negatives': 0,
            'total_samples': 0
        }
        
        # Initialize DIP stats only
        violation_stats['DIP'] = {
            'true_positives': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'true_negatives': 0,
            'total_samples': 0,
            'by_language': defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0}),
            'by_model': defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0}),
            'by_strategy': defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0})
        }
        
        # Process all results
        for model_folder, model_data in all_results.items():
            for prompt_type, results in model_data.items():
                if results.get('status') == 'ERROR':
                    continue
                
                for violation_type, violation_data in results.get('violation_results', {}).items():
                    expected_violation = violation_type.upper()
                    
                    for item in violation_data.get('items', []):
                        detected_violation = item.get('detected_violation')
                        language = item.get('language', 'UNKNOWN')
                        model = item.get('model', 'UNKNOWN')
                        strategy = item.get('strategy', 'UNKNOWN')
                        
                        # Calculate confusion matrix values for DIP
                        if expected_violation == 'DIP' and detected_violation == 'DIP':
                            # True Positive
                            violation_stats['DIP']['true_positives'] += 1
                            violation_stats['DIP']['by_language'][language]['tp'] += 1
                            violation_stats['DIP']['by_model'][model]['tp'] += 1
                            violation_stats['DIP']['by_strategy'][strategy]['tp'] += 1
                            overall_stats['true_positives'] += 1
                                
                        elif expected_violation != 'DIP' and detected_violation == 'DIP':
                            # False Positive
                            violation_stats['DIP']['false_positives'] += 1
                            violation_stats['DIP']['by_language'][language]['fp'] += 1
                            violation_stats['DIP']['by_model'][model]['fp'] += 1
                            violation_stats['DIP']['by_strategy'][strategy]['fp'] += 1
                            overall_stats['false_positives'] += 1
                                
                        elif expected_violation == 'DIP' and detected_violation != 'DIP':
                            # False Negative
                            violation_stats['DIP']['false_negatives'] += 1
                            violation_stats['DIP']['by_language'][language]['fn'] += 1
                            violation_stats['DIP']['by_model'][model]['fn'] += 1
                            violation_stats['DIP']['by_strategy'][strategy]['fn'] += 1
                            overall_stats['false_negatives'] += 1
                                
                        else:
                            # True Negative
                            violation_stats['DIP']['true_negatives'] += 1
                            violation_stats['DIP']['by_language'][language]['tn'] += 1
                            violation_stats['DIP']['by_model'][model]['tn'] += 1
                            violation_stats['DIP']['by_strategy'][strategy]['tn'] += 1
                            overall_stats['true_negatives'] += 1
                        
                        violation_stats['DIP']['total_samples'] += 1
                        overall_stats['total_samples'] += 1
        
        return self.calculate_metrics(violation_stats, overall_stats)
    
    def calculate_metrics(self, violation_stats: Dict, overall_stats: Dict) -> Dict:
        """Calculate precision, recall, F1, and accuracy from confusion matrix."""
        
        def safe_divide(numerator, denominator):
            return numerator / denominator if denominator > 0 else 0.0
        
        def calculate_metrics_for_category(stats):
            tp = stats['tp'] if isinstance(stats, dict) and 'tp' in stats else stats.get('true_positives', 0)
            fp = stats['fp'] if isinstance(stats, dict) and 'fp' in stats else stats.get('false_positives', 0)
            fn = stats['fn'] if isinstance(stats, dict) and 'fn' in stats else stats.get('false_negatives', 0)
            tn = stats['tn'] if isinstance(stats, dict) and 'tn' in stats else stats.get('true_negatives', 0)
            
            precision = safe_divide(tp, tp + fp)
            recall = safe_divide(tp, tp + fn)
            f1 = safe_divide(2 * precision * recall, precision + recall)
            accuracy = safe_divide(tp + tn, tp + fp + fn + tn)
            
            return {
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'accuracy': accuracy,
                'true_positives': tp,
                'false_positives': fp,
                'false_negatives': fn,
                'true_negatives': tn,
                'total_samples': tp + fp + fn + tn
            }
        
        # Calculate overall metrics
        overall_metrics = calculate_metrics_for_category(overall_stats)
        
        # Calculate DIP-specific metrics
        detailed_stats = {
            'overall': overall_metrics,
            'by_violation_type': {},
            'summary': {
                'violation_analyzed': 'DIP',
                'f1_score': 0.0
            }
        }
        
        # Process DIP stats
        if 'DIP' in violation_stats:
            stats = violation_stats['DIP']
            violation_metrics = calculate_metrics_for_category(stats)
            
            # Add breakdown by language, model, strategy
            violation_metrics['by_language'] = {}
            violation_metrics['by_model'] = {}
            violation_metrics['by_strategy'] = {}
            
            for language, lang_stats in stats['by_language'].items():
                violation_metrics['by_language'][language] = calculate_metrics_for_category(lang_stats)
            
            for model, model_stats in stats['by_model'].items():
                violation_metrics['by_model'][model] = calculate_metrics_for_category(model_stats)
            
            for strategy, strategy_stats in stats['by_strategy'].items():
                violation_metrics['by_strategy'][strategy] = calculate_metrics_for_category(strategy_stats)
            
            detailed_stats['by_violation_type']['DIP'] = violation_metrics
            detailed_stats['summary']['f1_score'] = violation_metrics['f1_score']
        
        return detailed_stats
    
    def save_detailed_statistics(self, all_results: Dict, output_file: str = "detailed_statistics_dip.json"):
        """Save comprehensive statistics for DIP only."""
        stats = self.calculate_detailed_statistics(all_results)
        
        # Add metadata
        final_stats = {
            'generation_timestamp': datetime.now().isoformat(),
            'analysis_metadata': {
                'total_models_analyzed': len(all_results),
                'violation_types_tested': ['dip'],  # Only DIP
                'prompt_strategies_tested': self.prompt_types,
                'total_samples_processed': stats['overall']['total_samples'],
                'focus': 'DIP (Dependency Inversion Principle) violations only'
            },
            'statistics': stats
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_stats, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Detailed DIP statistics saved to '{output_file}'")
        
        # Print summary to console
        self.print_statistics_summary(stats)
        
        return final_stats
    
    def print_statistics_summary(self, stats: Dict):
        """Print a summary of key statistics to console - DIP focused."""
        print(f"\n{'='*60}")
        print("DIP VIOLATION DETECTION PERFORMANCE SUMMARY")
        print(f"{'='*60}")
        
        overall = stats['overall']
        print(f"Overall DIP Performance:")
        print(f"  Accuracy: {overall['accuracy']:.3f}")
        print(f"  Precision: {overall['precision']:.3f}")
        print(f"  Recall: {overall['recall']:.3f}")
        print(f"  F1 Score: {overall['f1_score']:.3f}")
        print(f"  Total Samples: {overall['total_samples']}")
        
        if 'DIP' in stats['by_violation_type']:
            dip_metrics = stats['by_violation_type']['DIP']
            print(f"\nDIP-Specific Performance:")
            print(f"  Accuracy: {dip_metrics['accuracy']:.3f}")
            print(f"  Precision: {dip_metrics['precision']:.3f}")
            print(f"  Recall: {dip_metrics['recall']:.3f}")
            print(f"  F1 Score: {dip_metrics['f1_score']:.3f}")
            
            # Show performance by strategy
            if dip_metrics.get('by_strategy'):
                print(f"\nPerformance by Strategy:")
                for strategy, metrics in dip_metrics['by_strategy'].items():
                    print(f"  {strategy}:")
                    print(f"    Accuracy: {metrics['accuracy']:.3f}")
                    print(f"    F1 Score: {metrics['f1_score']:.3f}")
            
            # Show performance by language
            if dip_metrics.get('by_language'):
                print(f"\nPerformance by Language:")
                for language, metrics in dip_metrics['by_language'].items():
                    print(f"  {language}:")
                    print(f"    Accuracy: {metrics['accuracy']:.3f}")
                    print(f"    F1 Score: {metrics['f1_score']:.3f}")
        
        return stats
    
    def save_multiple_violation_cases(self, output_file: str):
        """Save cases where models detected multiple violations for manual review."""
        if not self.multiple_violations_cases:
            print("No multiple violation cases found.")
            return
        
        # Organize by model for easier review (DIP focused)
        organized_cases = defaultdict(list)
        
        for case in self.multiple_violations_cases:
            model = case['model']
            organized_cases[model].append(case)
        
        output_data = {
            'summary': {
                'total_cases': len(self.multiple_violations_cases),
                'focus': 'DIP violations with multiple detections',
                'by_model': {model: len(cases) for model, cases in organized_cases.items()}
            },
            'cases_by_model': dict(organized_cases),
            'all_cases': self.multiple_violations_cases
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Found {len(self.multiple_violations_cases)} DIP cases with multiple violations")
        print(f"✓ Multiple violations cases saved to '{output_file}'")
        
        # Print summary
        print("\nMultiple Violations Summary (DIP focus):")
        for model, cases in organized_cases.items():
            print(f"  {model}: {len(cases)} cases")
        
        return output_data
    
    def save_extracted_patterns(self, output_file: str = "extracted_regex_patterns_dip.json"):
        """Save all extracted regex patterns for DIP analysis."""
        patterns_data = {
            'extraction_timestamp': datetime.now().isoformat(),
            'focus': 'DIP (Dependency Inversion Principle) violations only',
            'regex_patterns_used': self.regex_patterns,
            'extracted_examples': {
                'violations_detected': dict(self.extracted_patterns['violations']),
                'language_specific_code': dict(self.extracted_patterns['language_patterns']),
                'dip_refactoring_patterns': dict(self.extracted_patterns['refactoring_patterns']),
                'code_structures': dict(self.extracted_patterns['code_structures'])
            },
            'pattern_statistics': {
                'total_violations_detected': sum(
                    len(examples) for examples in self.extracted_patterns['violations'].values()
                ),
                'languages_processed': list(self.extracted_patterns['language_patterns'].keys()),
                'dip_patterns_found': list(self.extracted_patterns['refactoring_patterns'].keys())
            },
            'recommended_dip_patterns': {
                'interface_detection': r'(?:interface|abstract\s+class)\s+\w+',
                'dependency_injection_detection': r'(?:constructor|__init__|init)\s*\([^)]*\w+\s+\w+',
                'abstraction_usage': r'private\s+(?:final\s+)?\w+\s+\w+;|self\.\w+\s*=\s*\w+',
                'quality_assessment': r'(?:I[A-Z]\w+|Abstract\w+|\w+Interface)'
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(patterns_data, f, indent=2, ensure_ascii=False)
        
        print(f"DIP-focused patterns saved to '{output_file}'")
        return patterns_data
    
    def generate_summary_report(self, all_results: Dict) -> str:
        """Generate a comprehensive summary report for DIP analysis."""
        report = []
        report.append("="*80)
        report.append("DIP VIOLATION DETECTION COMPARISON REPORT")
        report.append("="*80)
        
        # Overall statistics
        total_models = len(all_results)
        total_comparisons = sum(
            len(model_data) for model_data in all_results.values() if model_data
        )
        
        report.append(f"\nTOTAL DIP MODELS: {total_models}")
        report.append(f"TOTAL DIP COMPARISONS: {total_comparisons}")
        report.append(f"FOCUS: Dependency Inversion Principle (DIP) violations only")
        
        # Aggregate language statistics
        all_languages = defaultdict(int)
        total_accuracy_sum = 0
        total_experiments = 0
        
        # Model-wise results
        for model_name, model_data in all_results.items():
            if not model_data:
                continue
                
            report.append(f"\n{'-'*60}")
            report.append(f"DIP MODEL: {model_name}")
            report.append(f"{'-'*60}")
            
            for prompt_type, results in model_data.items():
                if not results:
                    report.append(f"  {prompt_type.upper()}: ERROR - No results returned")
                    continue
                    
                if results.get('status') == 'ERROR':
                    report.append(f"  {prompt_type.upper()}: ERROR - {results.get('error', 'Unknown error')}")
                    continue
                
                stats = results.get('overall_stats', {})
                total = stats.get('total_pass', 0) + stats.get('total_fail', 0) + stats.get('total_error', 0)
                accuracy = stats.get('total_pass', 0) / total if total > 0 else 0
                
                total_accuracy_sum += accuracy
                total_experiments += 1
                
                # Update language statistics
                for lang, count in stats.get('languages', {}).items():
                    all_languages[lang] += count
                
                report.append(f"  {prompt_type.upper()}:")
                report.append(f"    Total DIP Items: {total}")
                report.append(f"    DIP Accuracy: {accuracy:.1%}")
                report.append(f"    Pass: {stats.get('total_pass', 0)}, Fail: {stats.get('total_fail', 0)}, Error: {stats.get('total_error', 0)}")
                
                # Language breakdown
                if stats.get('languages'):
                    lang_info = ", ".join([f"{lang}: {count}" for lang, count in stats['languages'].items()])
                    report.append(f"    Languages: {lang_info}")
                
                # DIP-specific stats
                for violation_type, violation_data in results.get('violation_results', {}).items():
                    if violation_data and 'stats' in violation_data and violation_type == 'dip':
                        v_stats = violation_data['stats']
                        report.append(f"    DIP: {v_stats.get('accuracy', 0):.1%} ({v_stats.get('pass', 0)}/{v_stats.get('total', 0)})")
        
        # Overall summary
        if total_experiments > 0:
            overall_accuracy = total_accuracy_sum / total_experiments
            report.append(f"\n{'='*40}")
            report.append(f"OVERALL DIP PERFORMANCE SUMMARY")
            report.append(f"{'='*40}")
            report.append(f"Average DIP Accuracy: {overall_accuracy:.1%}")
            report.append(f"Total DIP Experiments: {total_experiments}")
            
            if all_languages:
                report.append(f"\nDIP Language Distribution:")
                for lang, count in sorted(all_languages.items(), key=lambda x: x[1], reverse=True):
                    percentage = count / sum(all_languages.values()) * 100
                    report.append(f"  {lang}: {count} ({percentage:.1f}%)")
        
        return '\n'.join(report)
    
    def save_detailed_results(self, all_results: Dict, output_file: str):
        """Save detailed DIP results to JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    def print_results(self, all_results: Dict):
        """Print formatted DIP results to console."""
        summary = self.generate_summary_report(all_results)
        print(summary)
    
    def save_failed_extraction_cases(self, output_file: str):
        """Save failed extraction cases for manual review - DIP focused."""
        if not self.failed_extraction_cases:
            print("No failed extraction cases found.")
            return
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.failed_extraction_cases, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Failed DIP extraction cases saved to '{output_file}'")
        print(f"  Total failed DIP cases: {len(self.failed_extraction_cases)}")


# Main execution
if __name__ == "__main__":
    # Configure your paths here
    OUTPUT_BASE_DIR = "dataset/completions/test"
    GROUND_TRUTH_DIR = "dataset"  # Not used anymore, but kept for compatibility
    
    print("="*60)
    print("DIP VIOLATION COMPARISON ANALYSIS")
    print("="*60)
    print("FOCUS: Dependency Inversion Principle (DIP) violations only")
    print("Using built-in ground truth from violation_type field")
    print(f"Output directory: {OUTPUT_BASE_DIR}")
    print("✓ Processing only DIP folders (dip--*)")
    print("✓ Fixed: Multiple mentions of same violation treated as single violation")
    print("="*60)
    
    # Initialize comparator
    comparator = SOLIDViolationComparator(
        output_base_dir=OUTPUT_BASE_DIR,
        ground_truth_dir=GROUND_TRUTH_DIR
    )
    
    # Save detailed comparison results
    all_results = comparator.run_full_comparison()
    comparator.save_detailed_results(all_results, "detailed_results_dip_only.json")

    # Save multiple violations cases
    comparator.save_multiple_violation_cases("multiple_violations_dip_review.json")

    # Save failed extraction cases
    comparator.save_failed_extraction_cases("failed_extraction_dip_review.json")

    # Save performance metrics
    comparator.save_detailed_statistics(all_results, "detailed_statistics_dip_only.json")

    # Save DIP-specific patterns
    comparator.save_extracted_patterns("extracted_regex_patterns_dip_only.json")

    # Optional: Print results to console
    comparator.print_results(all_results)