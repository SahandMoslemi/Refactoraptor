#!/usr/bin/env python3
"""
Main script to run SOLID violation comparison analysis.
This script uses the SOLIDViolationComparator class to compare model outputs
against ground truth files and extract regex patterns.
"""

from violations_comparison import SOLIDViolationComparator
import sys
from pathlib import Path

def main():
    # Configure your paths here
    OUTPUT_BASE_DIR = "dataset/completions/test"
    GROUND_TRUTH_DIR = "dataset"
    
    # Verify paths exist
    if not Path(OUTPUT_BASE_DIR).exists():
        print(f"Error: Output directory not found: {OUTPUT_BASE_DIR}")
        print("Please update OUTPUT_BASE_DIR in this script to match your directory structure.")
        sys.exit(1)
    
    if not Path(GROUND_TRUTH_DIR).exists():
        print(f"Error: Ground truth directory not found: {GROUND_TRUTH_DIR}")
        print("Please update GROUND_TRUTH_DIR in this script to match your directory structure.")
        sys.exit(1)
    
    # Check ground truth file structure
    print("Checking ground truth files...")
    gt_dir = Path(GROUND_TRUTH_DIR)
    
    violation_files = []
    for violation in ['dip', 'isp', 'lsp', 'ocp', 'srp']:
        file_path = gt_dir / f'{violation}_violations.json'
        if file_path.exists():
            violation_files.append(file_path.name)
        else:
            print(f"✗ Missing: {file_path.name}")
    
    print(f"✓ Found ground truth files: {violation_files}")
    
    if len(violation_files) != 5:
        print("Warning: Not all SOLID violation ground truth files found!")
        print("Expected: dip_violations.json, isp_violations.json, lsp_violations.json, ocp_violations.json, srp_violations.json")
    
    # Check a sample output directory
    print("\nChecking output file structure...")
    sample_dirs = list(Path(OUTPUT_BASE_DIR).glob("dip--*"))
    if sample_dirs:
        sample_dir = sample_dirs[0]
        output_file = sample_dir / "output_test.jsonl"
        if output_file.exists():
            print(f"✓ Found output file: {output_file}")
        else:
            print(f"✗ Expected output file not found: {output_file}")
            # Check what files actually exist
            actual_files = list(sample_dir.glob("*.jsonl"))
            print(f"  Files found in {sample_dir.name}: {[f.name for f in actual_files]}")
    
    print("="*60)
    
    # Initialize comparator
    comparator = SOLIDViolationComparator(
        output_base_dir=OUTPUT_BASE_DIR,
        ground_truth_dir=GROUND_TRUTH_DIR
    )
    
    # Run full comparison
    print("Starting comparison analysis...")
    results = comparator.run_full_comparison()
    
    # Save extracted patterns for future use
    print("\nExtracting and saving regex patterns...")
    pattern_data = comparator.save_extracted_patterns("extracted_regex_patterns.json")
    
    # Print results to console
    print("\n" + "="*60)
    print("COMPARISON RESULTS")
    print("="*60)
    comparator.print_results(results)
    
    # Save detailed results
    print("\nSaving detailed results...")
    comparator.save_detailed_results(results, "comparison_results.json")
    print("✓ Detailed results saved to 'comparison_results.json'")
    
    # Print pattern extraction summary
    print(f"\n{'='*60}")
    print("REGEX PATTERN EXTRACTION SUMMARY")
    print(f"{'='*60}")
    print(f"✓ Total violations detected: {pattern_data['pattern_statistics']['total_violations_detected']}")
    print(f"✓ Languages processed: {', '.join(pattern_data['pattern_statistics']['languages_processed'])}")
    print(f"✓ Violation types found: {', '.join(pattern_data['pattern_statistics']['violation_types_found'])}")
    print(f"✓ Patterns saved to: extracted_regex_patterns.json")
    
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE!")
    print(f"{'='*60}")
    print("Files generated:")
    print("  - comparison_results.json      (Detailed comparison results)")
    print("  - extracted_regex_patterns.json   (Regex patterns for future use)")
    print("\nYou can now examine these files for detailed insights.")

if __name__ == "__main__":
    main()