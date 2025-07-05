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
        self.violation_types = ['dip', 'isp', 'lsp', 'ocp', 'srp']
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
            'ensemble': r"\*\*([A-Z]{2,3}|NONE)\*\*",
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
            
            # SOLID-specific patterns for all violation types
            'dip_patterns': {
                'interface_creation': r'(?:interface|abstract\s+class)\s+\w+',
                'dependency_injection': r'(?:constructor|__init__|init)\s*\([^)]*\w+\s+\w+',
                'abstraction_usage': r'private\s+(?:final\s+)?\w+\s+\w+;|self\.\w+\s*=\s*\w+',
            },
            
            'srp_patterns': {
                'class_separation': r'class\s+\w+.*?(?=class|\Z)',
                'method_extraction': r'(?:public|private|def)\s+\w+\s*\([^)]*\)',
                'responsibility_split': r'class\s+\w*(?:Service|Manager|Handler|Controller)',
            },
            
            'isp_patterns': {
                'interface_segregation': r'interface\s+\w+\s*\{[^}]*\}',
                'small_interfaces': r'interface\s+\w+\s*\{[^{]*(?:\w+\s*\([^)]*\);?\s*){1,3}[^}]*\}',
                'multiple_interfaces': r'class\s+\w+\s+implements\s+\w+(?:\s*,\s*\w+)+',
            },
            
            'lsp_patterns': {
                'proper_inheritance': r'class\s+\w+\s+extends\s+\w+',
                'override_behavior': r'@Override|override\s+',
                'exception_throwing': r'throw\s+new\s+\w+Exception',
            },
            
            'ocp_patterns': {
                'polymorphism_usage': r'@Override|override\s+',
                'interface_implementation': r'implements\s+\w+',
                'abstract_methods': r'abstract\s+\w+\s+\w+\s*\(',
                'if_else_chains': r'if\s*\([^)]+\)\s*\{[^}]*\}\s*else\s*if',
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
        violations_found = []
        
        # Get the appropriate regex pattern for the strategy
        pattern = self.strategy_regex_patterns.get(strategy, self.strategy_regex_patterns['default'])
        
        # Find all matches
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        for match in matches:
            violation = match.upper()
            # Validate it's a known SOLID principle or NONE
            if violation in ['SRP', 'OCP', 'LSP', 'ISP', 'DIP', 'NONE']:
                violations_found.append(violation)
        
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
        
        # Case 2: Multiple violations found - FAIL and extract for manual review
        if len(violations_found) > 1:
            multiple_violation_case = {
                'id': output_item.get('id'),
                'model': output_item.get('model', 'UNKNOWN'),
                'strategy': strategy,
                'language': output_item.get('language', 'UNKNOWN'),
                'expected_violation': output_item.get('violation_type', '').upper(),
                'all_violations_found': violations_found,
                'reason': 'MULTIPLE_VIOLATIONS',
                'pattern_used': self.strategy_regex_patterns.get(strategy),
                'raw_response': text,
                'input_code': output_item.get('input', ''),
                'folder_source': f"{output_item.get('violation_type', 'unknown').lower()}--{output_item.get('model', 'unknown')}--{strategy}"
            }
            self.multiple_violations_cases.append(multiple_violation_case)
            return None
        
        # Case 3: Exactly one violation found - SUCCESS
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
        """Analyze patterns specific to violation types."""
        analysis = {
            'violation_addressed': False,
            'refactoring_quality': 'low',
            'specific_patterns': []
        }
        
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
        
        elif violation_type == 'SRP':
            patterns = self.regex_patterns['srp_patterns']
            for pattern_name, pattern in patterns.items():
                matches = re.findall(pattern, code, re.IGNORECASE | re.DOTALL)
                if matches:
                    analysis['specific_patterns'].append({
                        'pattern': pattern_name,
                        'matches': matches
                    })
                    self.extracted_patterns['refactoring_patterns']['srp'].extend(matches)
            
            # SRP assessment - multiple classes or clear separation
            class_matches = re.findall(patterns['class_separation'], code, re.IGNORECASE | re.DOTALL)
            if len(class_matches) > 1:
                analysis['violation_addressed'] = True
                analysis['refactoring_quality'] = 'medium'
        
        elif violation_type == 'ISP':
            patterns = self.regex_patterns['isp_patterns']
            for pattern_name, pattern in patterns.items():
                matches = re.findall(pattern, code, re.IGNORECASE | re.DOTALL)
                if matches:
                    analysis['specific_patterns'].append({
                        'pattern': pattern_name,
                        'matches': matches
                    })
                    self.extracted_patterns['refactoring_patterns']['isp'].extend(matches)
            
            # ISP assessment - multiple small interfaces
            interface_matches = re.findall(patterns['small_interfaces'], code, re.IGNORECASE | re.DOTALL)
            if len(interface_matches) > 1:
                analysis['violation_addressed'] = True
                analysis['refactoring_quality'] = 'medium'
        
        elif violation_type == 'LSP':
            patterns = self.regex_patterns['lsp_patterns']
            for pattern_name, pattern in patterns.items():
                matches = re.findall(pattern, code, re.IGNORECASE | re.DOTALL)
                if matches:
                    analysis['specific_patterns'].append({
                        'pattern': pattern_name,
                        'matches': matches
                    })
                    self.extracted_patterns['refactoring_patterns']['lsp'].extend(matches)
            
            # LSP assessment - proper inheritance without breaking contracts
            has_override = bool(re.search(patterns['override_behavior'], code, re.IGNORECASE))
            has_exceptions = bool(re.search(patterns['exception_throwing'], code, re.IGNORECASE))
            
            if has_override and not has_exceptions:
                analysis['violation_addressed'] = True
                analysis['refactoring_quality'] = 'medium'
        
        elif violation_type == 'OCP':
            patterns = self.regex_patterns['ocp_patterns']
            for pattern_name, pattern in patterns.items():
                matches = re.findall(pattern, code, re.IGNORECASE | re.DOTALL)
                if matches:
                    analysis['specific_patterns'].append({
                        'pattern': pattern_name,
                        'matches': matches
                    })
                    self.extracted_patterns['refactoring_patterns']['ocp'].extend(matches)
            
            # OCP assessment - polymorphism usage instead of if-else
            has_polymorphism = bool(re.search(patterns['polymorphism_usage'], code, re.IGNORECASE))
            has_interfaces = bool(re.search(patterns['interface_implementation'], code, re.IGNORECASE))
            
            if has_polymorphism and has_interfaces:
                analysis['violation_addressed'] = True
                analysis['refactoring_quality'] = 'high'
            elif has_polymorphism or has_interfaces:
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
        
        # Group outputs by violation type
        violation_groups = defaultdict(list)
        for item in output_data:
            violation_type = item.get('violation_type', '').lower()
            violation_groups[violation_type].append(item)
        
        print(f"  Violation groups found: {dict((k, len(v)) for k, v in violation_groups.items())}")
        
        # Debug: Show a sample of what violation types are in the data
        sample_violations = [item.get('violation_type', 'UNKNOWN') for item in output_data[:10]]
        print(f"  Sample violation types from data: {sample_violations}")
        
        results = {
            'model': model_folder,
            'prompt_type': prompt_type,
            'total_items': len(output_data),
            'violation_results': {},
            'overall_stats': {
                'total_pass': 0,
                'total_fail': 0,
                'total_error': 0,
                'languages': defaultdict(int)
            }
        }
        
        # Process each violation type found in the data
        for violation_type in violation_groups.keys():
            if violation_type in self.violation_types:
                print(f"  Processing {len(violation_groups[violation_type])} {violation_type} items")
                # Process this violation type (no external ground truth needed)
                self.process_violation_type(violation_type, violation_groups, results, prompt_type)
            else:
                print(f"  Skipping unknown violation type: {violation_type}")
        
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
        """Run comparison for all models and prompt types."""
        all_results = {}
        
        # Get all model folders - check for all SOLID violation types
        all_folders = [d.name for d in self.output_base_dir.iterdir() if d.is_dir()]
        
        # Look for folders starting with different violation types
        violation_folders = defaultdict(list)
        for folder in all_folders:
            for violation_type in self.violation_types:
                if folder.startswith(f'{violation_type}--'):
                    violation_folders[violation_type].append(folder)
        
        print(f"Found folders by violation type:")
        for violation_type, folders in violation_folders.items():
            print(f"  {violation_type.upper()}: {len(folders)} folders")
        
        # Process all folders for all violation types
        model_folders = []
        for folders in violation_folders.values():
            model_folders.extend(folders)
        
        if not model_folders:
            print("No violation-specific folders found!")
            return {}
        
        print(f"Processing {len(model_folders)} total model folders...")
        print("Note: Using built-in ground truth from violation_type field")
        
        for model_folder in model_folders:
            # Parse the folder name to get the actual strategy
            folder_info = self.parse_folder_name(model_folder)
            actual_strategy = folder_info['strategy']
            
            print(f"Processing {model_folder} (strategy: {actual_strategy})...")
            
            # Only process the actual strategy from the folder name, not all strategies
            result = self.compare_model_outputs(model_folder, actual_strategy)
            
            # Ensure result is not None
            if result is None:
                result = {
                    'model': model_folder,
                    'prompt_type': actual_strategy,
                    'status': 'ERROR',
                    'error': 'Comparison returned None'
                }
            
            # Store result using the folder name as key, but only for the actual strategy
            all_results[model_folder] = {
                actual_strategy: result
            }
        
        return all_results
    
    def calculate_detailed_statistics(self, all_results: Dict) -> Dict:
        """Calculate comprehensive statistics including F1 scores for each violation type."""
        from collections import defaultdict
        
        # Initialize counters for each violation type
        violation_stats = {}
        overall_stats = {
            'true_positives': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'true_negatives': 0,
            'total_samples': 0
        }
        
        # Initialize per-violation stats
        for violation_type in self.violation_types:
            violation_stats[violation_type.upper()] = {
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
                        
                        # Calculate confusion matrix values
                        for vtype in self.violation_types:
                            vtype_upper = vtype.upper()
                            
                            if expected_violation == vtype_upper and detected_violation == vtype_upper:
                                # True Positive
                                violation_stats[vtype_upper]['true_positives'] += 1
                                violation_stats[vtype_upper]['by_language'][language]['tp'] += 1
                                violation_stats[vtype_upper]['by_model'][model]['tp'] += 1
                                violation_stats[vtype_upper]['by_strategy'][strategy]['tp'] += 1
                                if vtype_upper == expected_violation:
                                    overall_stats['true_positives'] += 1
                                    
                            elif expected_violation != vtype_upper and detected_violation == vtype_upper:
                                # False Positive
                                violation_stats[vtype_upper]['false_positives'] += 1
                                violation_stats[vtype_upper]['by_language'][language]['fp'] += 1
                                violation_stats[vtype_upper]['by_model'][model]['fp'] += 1
                                violation_stats[vtype_upper]['by_strategy'][strategy]['fp'] += 1
                                if vtype_upper == expected_violation:
                                    overall_stats['false_positives'] += 1
                                    
                            elif expected_violation == vtype_upper and detected_violation != vtype_upper:
                                # False Negative
                                violation_stats[vtype_upper]['false_negatives'] += 1
                                violation_stats[vtype_upper]['by_language'][language]['fn'] += 1
                                violation_stats[vtype_upper]['by_model'][model]['fn'] += 1
                                violation_stats[vtype_upper]['by_strategy'][strategy]['fn'] += 1
                                if vtype_upper == expected_violation:
                                    overall_stats['false_negatives'] += 1
                                    
                            else:
                                # True Negative
                                violation_stats[vtype_upper]['true_negatives'] += 1
                                violation_stats[vtype_upper]['by_language'][language]['tn'] += 1
                                violation_stats[vtype_upper]['by_model'][model]['tn'] += 1
                                violation_stats[vtype_upper]['by_strategy'][strategy]['tn'] += 1
                                if vtype_upper == expected_violation:
                                    overall_stats['true_negatives'] += 1
                            
                            violation_stats[vtype_upper]['total_samples'] += 1
                        
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
        
        # Calculate per-violation metrics
        detailed_stats = {
            'overall': overall_metrics,
            'by_violation_type': {},
            'summary': {
                'best_performing_violation': None,
                'worst_performing_violation': None,
                'best_f1_score': 0.0,
                'worst_f1_score': 1.0
            }
        }
        
        for violation_type, stats in violation_stats.items():
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
            
            detailed_stats['by_violation_type'][violation_type] = violation_metrics
            
            # Track best/worst performing violations
            f1_score = violation_metrics['f1_score']
            if f1_score > detailed_stats['summary']['best_f1_score']:
                detailed_stats['summary']['best_f1_score'] = f1_score
                detailed_stats['summary']['best_performing_violation'] = violation_type
            
            if f1_score < detailed_stats['summary']['worst_f1_score']:
                detailed_stats['summary']['worst_f1_score'] = f1_score
                detailed_stats['summary']['worst_performing_violation'] = violation_type
        
        return detailed_stats
    
    def save_detailed_statistics(self, all_results: Dict, output_file: str = "detailed_statistics.json"):
        """Save comprehensive statistics including F1 scores to a file."""
        stats = self.calculate_detailed_statistics(all_results)
        
        # Add metadata
        final_stats = {
            'generation_timestamp': datetime.now().isoformat(),
            'analysis_metadata': {
                'total_models_analyzed': len(all_results),
                'violation_types_tested': self.violation_types,
                'prompt_strategies_tested': self.prompt_types,
                'total_samples_processed': stats['overall']['total_samples']
            },
            'statistics': stats
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_stats, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Detailed statistics saved to '{output_file}'")
        
        # Print summary to console
        self.print_statistics_summary(stats)
        
        return final_stats
    
    def print_statistics_summary(self, stats: Dict):
        """Print a summary of key statistics to console."""
        print(f"\n{'='*60}")
        print("PERFORMANCE STATISTICS SUMMARY")
        print(f"{'='*60}")
        
        overall = stats['overall']
        print(f"Overall Performance:")
        print(f"  Accuracy: {overall['accuracy']:.3f}")
        print(f"  Precision: {overall['precision']:.3f}")
        print(f"  Recall: {overall['recall']:.3f}")
        print(f"  F1 Score: {overall['f1_score']:.3f}")
        print(f"  Total Samples: {overall['total_samples']}")
        
        print(f"\nPer-Violation Performance:")
        for violation_type, metrics in stats['by_violation_type'].items():
            print(f"  {violation_type}:")
            print(f"    Accuracy: {metrics['accuracy']:.3f}")
            print(f"    Precision: {metrics['precision']:.3f}")
            print(f"    Recall: {metrics['recall']:.3f}")
            print(f"    F1 Score: {metrics['f1_score']:.3f}")
        
        summary = stats['summary']
        print(f"\nBest Performing: {summary['best_performing_violation']} (F1: {summary['best_f1_score']:.3f})")
        print(f"Worst Performing: {summary['worst_performing_violation']} (F1: {summary['worst_f1_score']:.3f})")
        
        return stats
    def save_multiple_violation_cases(self, output_file: str):
        """Save cases where models detected multiple violations for manual review."""
        if not self.multiple_violations_cases:
            print("No multiple violation cases found.")
            return
        
        # Organize by violation type and model for easier review
        organized_cases = defaultdict(lambda: defaultdict(list))
        
        for case in self.multiple_violations_cases:
            expected_violation = case['expected_violation']
            model = case['model']
            organized_cases[expected_violation][model].append(case)
        
        output_data = {
            'summary': {
                'total_cases': len(self.multiple_violations_cases),
                'by_violation_type': {
                    violation: sum(len(models[model]) for model in models)
                    for violation, models in organized_cases.items()
                },
                'by_model': defaultdict(int)
            },
            'cases_by_violation_type': dict(organized_cases),
            'all_cases': self.multiple_violations_cases
        }
        
        # Count by model
        for case in self.multiple_violations_cases:
            output_data['summary']['by_model'][case['model']] += 1
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Found {len(self.multiple_violations_cases)} cases with multiple violations")
        print(f"✓ Multiple violations cases saved to '{output_file}'")
        
        # Print summary
        print("\nMultiple Violations Summary:")
        for violation, models in organized_cases.items():
            total_for_violation = sum(len(cases) for cases in models.values())
            print(f"  {violation}: {total_for_violation} cases")
            for model, cases in models.items():
                print(f"    - {model}: {len(cases)} cases")
        
        return output_data
    
    def save_extracted_patterns(self, output_file: str = "extracted_regex_patterns.json"):
        """Save all extracted regex patterns to a separate file for later use."""
        patterns_data = {
            'extraction_timestamp': datetime.now().isoformat(),
            'regex_patterns_used': self.regex_patterns,
            'extracted_examples': {
                'violations_detected': dict(self.extracted_patterns['violations']),
                'language_specific_code': dict(self.extracted_patterns['language_patterns']),
                'refactoring_patterns': dict(self.extracted_patterns['refactoring_patterns']),
                'code_structures': dict(self.extracted_patterns['code_structures'])
            },
            'pattern_statistics': {
                'total_violations_detected': sum(
                    len(examples) for examples in self.extracted_patterns['violations'].values()
                ),
                'languages_processed': list(self.extracted_patterns['language_patterns'].keys()),
                'violation_types_found': list(self.extracted_patterns['refactoring_patterns'].keys())
            },
            'recommended_patterns_for_future_use': {
                'high_confidence_violation_detection': [
                    r'\*\*([A-Z]{3})\*\*',
                    r'\*\*NONE\*\*'
                ],
                'code_block_extraction': [
                    r'```java\n(.*?)\n```',
                    r'```python\n(.*?)\n```',
                    r'```kotlin\n(.*?)\n```',
                    r'```(?:c#|csharp)\n(.*?)\n```'
                ],
                'quality_assessment': [
                    r'(?:public\s+)?interface\s+(\w+)',
                    r'(?:constructor|__init__)\s*\([^)]*\w+\s+\w+',
                    r'class\s+\w+.*?(?=class|\Z)'
                ]
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(patterns_data, f, indent=2, ensure_ascii=False)
        
        print(f"Extracted patterns saved to '{output_file}'")
        return patterns_data
    
    def generate_summary_report(self, all_results: Dict) -> str:
        """Generate a comprehensive summary report."""
        report = []
        report.append("="*80)
        report.append("SOLID VIOLATION DETECTION COMPARISON REPORT")
        report.append("="*80)
        
        # Overall statistics
        total_models = len(all_results)
        total_comparisons = sum(
            len(model_data) for model_data in all_results.values() if model_data
        )
        
        report.append(f"\nTOTAL MODELS: {total_models}")
        report.append(f"TOTAL COMPARISONS: {total_comparisons}")
        
        # Aggregate language statistics
        all_languages = defaultdict(int)
        total_accuracy_sum = 0
        total_experiments = 0
        
        # Model-wise results
        for model_name, model_data in all_results.items():
            if not model_data:
                continue
                
            report.append(f"\n{'-'*60}")
            report.append(f"MODEL: {model_name}")
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
                report.append(f"    Total Items: {total}")
                report.append(f"    Accuracy: {accuracy:.1%}")
                report.append(f"    Pass: {stats.get('total_pass', 0)}, Fail: {stats.get('total_fail', 0)}, Error: {stats.get('total_error', 0)}")
                
                # Language breakdown
                if stats.get('languages'):
                    lang_info = ", ".join([f"{lang}: {count}" for lang, count in stats['languages'].items()])
                    report.append(f"    Languages: {lang_info}")
                
                # Violation-specific stats
                for violation_type, violation_data in results.get('violation_results', {}).items():
                    if violation_data and 'stats' in violation_data:
                        v_stats = violation_data['stats']
                        report.append(f"    {violation_type.upper()}: {v_stats.get('accuracy', 0):.1%} ({v_stats.get('pass', 0)}/{v_stats.get('total', 0)})")
        
        # Overall summary
        if total_experiments > 0:
            overall_accuracy = total_accuracy_sum / total_experiments
            report.append(f"\n{'='*40}")
            report.append(f"OVERALL PERFORMANCE SUMMARY")
            report.append(f"{'='*40}")
            report.append(f"Average Accuracy: {overall_accuracy:.1%}")
            report.append(f"Total Experiments: {total_experiments}")
            
            if all_languages:
                report.append(f"\nLanguage Distribution:")
                for lang, count in sorted(all_languages.items(), key=lambda x: x[1], reverse=True):
                    percentage = count / sum(all_languages.values()) * 100
                    report.append(f"  {lang}: {count} ({percentage:.1f}%)")
        
        return '\n'.join(report)
    
    def save_detailed_results(self, all_results: Dict, output_file: str):
        """Save detailed results to JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    def print_results(self, all_results: Dict):
        """Print formatted results to console."""
        summary = self.generate_summary_report(all_results)
        print(summary)
    
    def save_failed_extraction_cases(self, output_file: str):
        """Save failed extraction cases for manual review."""
        if not self.failed_extraction_cases:
            print("No failed extraction cases found.")
            return
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.failed_extraction_cases, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Failed extraction cases saved to '{output_file}'")
        print(f"  Total failed cases: {len(self.failed_extraction_cases)}")


# Main execution
if __name__ == "__main__":
    # Configure your paths here
    OUTPUT_BASE_DIR = "dataset/completions/test"
    GROUND_TRUTH_DIR = "dataset"  # Not used anymore, but kept for compatibility
    
    print("="*60)
    print("SOLID VIOLATION COMPARISON ANALYSIS")
    print("="*60)
    print("Using built-in ground truth from violation_type field")
    print(f"Output directory: {OUTPUT_BASE_DIR}")
    print("="*60)
    
    # Initialize comparator
    comparator = SOLIDViolationComparator(
        output_base_dir=OUTPUT_BASE_DIR,
        ground_truth_dir=GROUND_TRUTH_DIR
    )
    
    # Save detailed comparison results
    all_results = comparator.run_full_comparison()
    comparator.save_detailed_results(all_results, "detailed_results_v4.json")

    # Save multiple violations cases
    comparator.save_multiple_violation_cases("multiple_violations_for_review_v4.json")

    # Save failed extraction cases
    comparator.save_failed_extraction_cases("failed_extraction_for_review_v4.json")

    # Save performance metrics
    comparator.save_detailed_statistics(all_results, "detailed_statistics_v4.json")

    # Optional: Print results to console
    comparator.print_results(all_results)
