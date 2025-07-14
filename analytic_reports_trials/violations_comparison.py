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
        self.extracted_patterns = {
            'violations': defaultdict(list),
            'code_structures': defaultdict(list),
            'language_patterns': defaultdict(list),
            'refactoring_patterns': defaultdict(list)
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

    def load_ground_truth_file(self, file_path: Path) -> List[Dict]:
        """Load ground truth JSON file with code_examples structure."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Extract code_examples if present
                if 'code_examples' in data:
                    return data['code_examples']
                return data if isinstance(data, list) else [data]
        except Exception as e:
            print(f"Error loading ground truth {file_path}: {e}")
            return []

    def load_all_ground_truth(self) -> Dict[str, List[Dict]]:
        """Load ground truth data from separate files for each violation type."""
        all_gt_data = {}
        
        # Load separate files for each violation type
        for violation_type in self.violation_types:
            gt_file = self.ground_truth_dir / f'{violation_type}_violations.json'
            if gt_file.exists():
                gt_data = self.load_ground_truth_file(gt_file)
                all_gt_data[violation_type] = gt_data
                print(f"✓ Loaded {len(gt_data)} examples from {gt_file.name}")
            else:
                print(f"✗ Ground truth file not found: {gt_file}")
        
        print(f"Ground truth summary: {[(k, len(v)) for k, v in all_gt_data.items()]}")
        return all_gt_data
    
    def extract_violation_type(self, text: str) -> Optional[str]:
        """Extract violation type from model response using regex."""
        # Look for **VIOLATION_TYPE** pattern
        match = re.search(self.regex_patterns['violation_extraction'], text, re.IGNORECASE)
        if match:
            violation = match.group(1).upper()
            self.extracted_patterns['violations']['detected'].append(violation)
            return violation
        
        # Check for **NONE** response
        if re.search(self.regex_patterns['none_response'], text, re.IGNORECASE):
            self.extracted_patterns['violations']['none_detected'].append(text[:100])
            return 'NONE'
        
        return None
    
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
    
    def find_ground_truth_by_input(self, output_item: Dict, ground_truth_items: List[Dict]) -> Optional[Dict]:
        """Find matching ground truth item by comparing input code."""
        output_input = output_item.get('input', '').strip()
        
        for gt_item in ground_truth_items:
            gt_input = gt_item.get('input', '').strip()
            
            # Try exact match first
            if output_input == gt_input:
                return gt_item
            
            # Try similarity match (remove whitespace differences)
            output_normalized = re.sub(r'\s+', ' ', output_input)
            gt_normalized = re.sub(r'\s+', ' ', gt_input)
            
            if output_normalized == gt_normalized:
                return gt_item
            
            # Try high similarity match
            similarity = difflib.SequenceMatcher(None, output_input, gt_input).ratio()
            if similarity > 0.9:
                return gt_item
        
        return None
    
    def compare_single_output(self, output_item: Dict, ground_truth_items: List[Dict]) -> Dict:
        """Compare single output item against ground truth."""
        output_id = output_item.get('id')
        raw_response = output_item.get('raw_response', '')
        expected_violation = output_item.get('violation_type', '').upper()
        language = output_item.get('language', 'UNKNOWN')
        
        # Find matching ground truth item by input similarity
        gt_item = self.find_ground_truth_by_input(output_item, ground_truth_items)
        
        if not gt_item:
            return {
                'id': output_id,
                'status': 'ERROR',
                'error': 'No matching ground truth found',
                'language': language
            }
        
        # Extract violation type from model response
        extracted_violation = self.extract_violation_type(raw_response)
        gt_violation = gt_item.get('violation', '').upper()
        
        # Compare violation detection
        violation_match = extracted_violation == gt_violation
        
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
            'expected_violation': gt_violation,
            'detected_violation': extracted_violation,
            'violation_match': violation_match,
            'code_blocks': code_blocks,
            'language_analysis': language_analysis,
            'violation_analysis': violation_analysis,
            'response_length': len(raw_response),
            'ground_truth_level': gt_item.get('level', 'UNKNOWN'),
            'similarity_to_gt': difflib.SequenceMatcher(
                None, 
                output_item.get('input', ''), 
                gt_item.get('input', '')
            ).ratio()
        }
    
    def process_violation_type(self, violation_type: str, violation_groups: Dict, gt_data: List[Dict], results: Dict) -> None:
        """Process a single violation type and update results."""
        # Compare each output item
        violation_results = []
        for output_item in violation_groups[violation_type]:
            result = self.compare_single_output(output_item, gt_data)
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
        
        # Load all ground truth data
        all_gt_data = self.load_all_ground_truth()
        
        if not all_gt_data:
            return {
                'model': model_folder,
                'prompt_type': prompt_type,
                'status': 'ERROR',
                'error': 'No ground truth data loaded'
            }
        
        # Compare each violation type
        for violation_type in self.violation_types:
            if violation_type not in violation_groups:
                continue
                
            # Get ground truth data for this violation type
            if violation_type not in all_gt_data:
                print(f"  Warning: No ground truth data found for {violation_type}")
                continue
                
            gt_data = all_gt_data[violation_type]
            print(f"  Processing {len(violation_groups[violation_type])} {violation_type} items against {len(gt_data)} ground truth examples")
            
            # Process this violation type
            self.process_violation_type(violation_type, violation_groups, gt_data, results)
        
        return results
    
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
        
        for model_folder in model_folders:
            model_results = {}
            
            for prompt_type in self.prompt_types:
                print(f"Processing {model_folder} - {prompt_type}...")
                result = self.compare_model_outputs(model_folder, prompt_type)
                
                # Ensure result is not None
                if result is None:
                    result = {
                        'model': model_folder,
                        'prompt_type': prompt_type,
                        'status': 'ERROR',
                        'error': 'Comparison returned None'
                    }
                
                model_results[prompt_type] = result
            
            all_results[model_folder] = model_results
        
        return all_results
    
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


# Example usage
if __name__ == "__main__":
    # Initialize comparator
    comparator = SOLIDViolationComparator(
        output_base_dir="dataset/completions/test",
        ground_truth_dir="dataset"
    )
    
    # Run full comparison
    print("Starting comparison...")
    results = comparator.run_full_comparison()
    
    # Save extracted patterns for future use
    pattern_data = comparator.save_extracted_patterns("extracted_regex_patterns.json")
    
    # Print results
    comparator.print_results(results)
    
    # Save detailed results
    comparator.save_detailed_results(results, "comparison_results.json")
    print("\nDetailed results saved to 'comparison_results.json'")
    
    # Print pattern extraction summary
    print(f"\n{'='*60}")
    print("REGEX PATTERN EXTRACTION SUMMARY")
    print(f"{'='*60}")
    print(f"Total violations detected: {pattern_data['pattern_statistics']['total_violations_detected']}")
    print(f"Languages processed: {', '.join(pattern_data['pattern_statistics']['languages_processed'])}")
    print(f"Violation types found: {', '.join(pattern_data['pattern_statistics']['violation_types_found'])}")
    print(f"Patterns saved to: extracted_regex_patterns.json")