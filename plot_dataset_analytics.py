
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os


"""
Analyisis of cyclomatic_complexity_results.csv


Code Length Distribution Visualization for SOLID Principles Dataset

This script analyzes and visualizes code length distributions across different
violation types and difficulty levels from cyclomatic complexity data.

Required libraries: pandas, matplotlib, seaborn, numpy
Input file: cyclomatic_complexity_results.csv
"""

# Configuration
INPUT_FILE = 'cyclomatic_complexity_results.csv'
FIGURE_SIZE = (18, 12)
COLORS = {'EASY': '#2E8B57', 'MODERATE': '#FF8C00', 'HARD': '#DC143C'}
OUTPUT_FILE = 'plots/code_length_analysis.png'  # Optional: save plot
COMPLEXITY_OUTPUT_FILE = 'plots/cyclomatic_complexity_analysis.png'


def load_data(file_path):
    """Load and validate the CSV data."""
    try:
        df = pd.read_csv(file_path)
        print(f"Successfully loaded {len(df)} records from {file_path}")
        return df
    except FileNotFoundError:
        print(f"Error: File {file_path} not found!")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def create_scatter_plot(df, ax, x_col, y_col, title):
    """Create a scatter plot for code lengths by violation type and level."""
    violation_types = df['violation'].unique()
    
    for i, violation in enumerate(violation_types):
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)][y_col]
            if not data.empty:
                ax.scatter([i] * len(data), data, alpha=0.6, color=COLORS[level], 
                          label=level if i == 0 else "", s=30)
    
    ax.set_xlabel('Violation Type')
    ax.set_ylabel(y_col.replace('_', ' ').title())
    ax.set_title(title)
    ax.set_xticks(range(len(violation_types)))
    ax.set_xticklabels(violation_types)
    if 'input' in y_col.lower():
        ax.legend()
    ax.grid(True, alpha=0.3)


def create_box_plot(df, ax, y_col, title):
    """Create a box plot for code lengths."""
    violation_types = df['violation'].unique()
    data_list = []
    labels = []
    
    for violation in violation_types:
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)][y_col]
            if not data.empty:
                data_list.append(data)
                labels.append(f'{violation}\n{level}')
    
    bp = ax.boxplot(data_list, labels=labels, patch_artist=True)
    for patch, label in zip(bp['boxes'], labels):
        level = label.split('\n')[1]
        patch.set_facecolor(COLORS[level])
        patch.set_alpha(0.7)
    
    ax.set_title(title)
    ax.set_ylabel(y_col.replace('_', ' ').title())
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')


def create_heatmap(df, ax, col, title):
    """Create a heatmap of average code lengths."""
    pivot_data = df.groupby(['violation', 'level'])[col].mean().reset_index()
    pivot_data = pivot_data.pivot(index='violation', columns='level', values=col)
    
    sns.heatmap(pivot_data, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax, 
                cbar_kws={'label': 'Average Length'})
    ax.set_title(title)
    ax.set_xlabel('Difficulty Level')
    ax.set_ylabel('Violation Type')


def create_length_change_plot(df, ax):
    """Create a plot showing code length changes after fixing violations."""
    df['length_change'] = df['output_code_length'] - df['input_code_length']
    violation_types = df['violation'].unique()
    
    for i, violation in enumerate(violation_types):
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['length_change']
            if not data.empty:
                ax.scatter([i] * len(data), data, alpha=0.6, color=COLORS[level], s=30)
    
    ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax.set_xlabel('Violation Type')
    ax.set_ylabel('Length Change (Output - Input)')
    ax.set_title('Code Length Change After Fix')
    ax.set_xticks(range(len(violation_types)))
    ax.set_xticklabels(violation_types)
    ax.grid(True, alpha=0.3)


def print_summary_statistics(df):
    """Print comprehensive summary statistics."""
    print("\n" + "="*50)
    print("SUMMARY STATISTICS")
    print("="*50)
    print(f"Total records: {len(df)}")
    print(f"Violation types: {list(df['violation'].unique())}")
    print(f"Difficulty levels: {list(df['level'].unique())}")
    print(f"Languages: {list(df['language'].unique())}")
    
    print("\n" + "="*50)
    print("HIGHEST CODE LENGTHS")
    print("="*50)
    max_input = df.loc[df['input_code_length'].idxmax()]
    max_output = df.loc[df['output_code_length'].idxmax()]
    
    print(f"Highest input code length: {max_input['input_code_length']} characters")
    print(f"  - Violation: {max_input['violation']}, Level: {max_input['level']}, Language: {max_input['language']}")
    print(f"Highest output code length: {max_output['output_code_length']} characters")
    print(f"  - Violation: {max_output['violation']}, Level: {max_output['level']}, Language: {max_output['language']}")
    
    print("\n" + "="*50)
    print("AVERAGE CODE LENGTHS BY DIFFICULTY")
    print("="*50)
    avg_by_level = df.groupby('level')[['input_code_length', 'output_code_length']].mean()
    print(avg_by_level.round(2))
    
    print("\n" + "="*50)
    print("AVERAGE CODE LENGTHS BY VIOLATION TYPE")
    print("="*50)
    avg_by_violation = df.groupby('violation')[['input_code_length', 'output_code_length']].mean()
    print(avg_by_violation.round(2))


def visualize_code_lengths(df, save_plot=False):
    """Create comprehensive visualization of code length distributions."""
    # Create figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=FIGURE_SIZE)
    fig.suptitle('Code Length Distribution by Violation Type and Difficulty Level', 
                 fontsize=16, fontweight='bold')
    
    # Plot 1: Input Code Length Scatter Plot
    create_scatter_plot(df, axes[0, 0], 'violation', 'input_code_length', 
                       'Input Code Length Distribution')
    
    # Plot 2: Output Code Length Scatter Plot
    create_scatter_plot(df, axes[0, 1], 'violation', 'output_code_length', 
                       'Output Code Length Distribution')
    
    # Plot 3: Input Code Length Box Plot
    create_box_plot(df, axes[0, 2], 'input_code_length', 'Input Code Length Box Plot')
    
    # Plot 4: Output Code Length Box Plot
    create_box_plot(df, axes[1, 0], 'output_code_length', 'Output Code Length Box Plot')
    
    # Plot 5: Heatmap of Average Input Code Lengths
    create_heatmap(df, axes[1, 1], 'input_code_length', 'Average Input Code Length Heatmap')
    
    # Plot 6: Code Length Change Plot
    create_length_change_plot(df, axes[1, 2])
    
    plt.tight_layout()
    
    if save_plot:
        plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
        print(f"Plot saved as {OUTPUT_FILE}")
    
    plt.show()


def create_complexity_comparison_plots(df, save_plot=False):
    """Create comprehensive cyclomatic complexity comparison visualizations."""
    # Ensure plots directory exists
    if save_plot:
        os.makedirs('plots', exist_ok=True)
    
    # Create figure with subplots for complexity analysis
    fig, axes = plt.subplots(2, 3, figsize=FIGURE_SIZE)
    fig.suptitle('Cyclomatic Complexity Analysis: Before vs After SOLID Violation Fixes', 
                 fontsize=16, fontweight='bold')
    
    violation_types = df['violation'].unique()
    
    # Plot 1: Input vs Output Complexity Scatter Plot
    ax1 = axes[0, 0]
    for level in ['EASY', 'MODERATE', 'HARD']:
        data = df[df['level'] == level]
        ax1.scatter(data['input_complexity'], data['output_complexity'], 
                   alpha=0.6, color=COLORS[level], label=level, s=40)
    
    # Add diagonal line (y=x) to show no change
    max_complexity = max(df['input_complexity'].max(), df['output_complexity'].max())
    ax1.plot([0, max_complexity], [0, max_complexity], 'k--', alpha=0.5, label='No Change')
    ax1.set_xlabel('Input Complexity')
    ax1.set_ylabel('Output Complexity') 
    ax1.set_title('Input vs Output Complexity')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Complexity Change by Violation Type
    ax2 = axes[0, 1]
    df['complexity_change'] = df['output_complexity'] - df['input_complexity']
    
    for i, violation in enumerate(violation_types):
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['complexity_change']
            if not data.empty:
                ax2.scatter([i] * len(data), data, alpha=0.6, color=COLORS[level], s=30)
    
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Violation Type')
    ax2.set_ylabel('Complexity Change (Output - Input)')
    ax2.set_title('Complexity Change After Fix')
    ax2.set_xticks(range(len(violation_types)))
    ax2.set_xticklabels(violation_types)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Box Plot + Scatter of Input Complexity by Violation and Level
    ax3 = axes[0, 2]
    complexity_data = []
    labels = []
    positions = []
    pos = 1
    
    for violation in violation_types:
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_complexity']
            if not data.empty:
                complexity_data.append(data)
                labels.append(f'{violation}\n{level}')
                positions.append(pos)
                pos += 1
    
    # Create box plot
    bp1 = ax3.boxplot(complexity_data, positions=positions, patch_artist=True, widths=0.6)
    
    # Color the boxes and add scatter points
    pos = 1
    for violation in violation_types:
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_complexity']
            if not data.empty:
                # Color the box
                if pos <= len(bp1['boxes']):
                    bp1['boxes'][pos-1].set_facecolor(COLORS[level])
                    bp1['boxes'][pos-1].set_alpha(0.7)
                
                # Add scatter points with jitter
                jitter = np.random.normal(0, 0.1, len(data))
                ax3.scatter([pos] * len(data) + jitter, data, 
                           alpha=0.6, color=COLORS[level], s=20, zorder=3)
                pos += 1
    
    ax3.set_title('Input Complexity Distribution (Box + Scatter)')
    ax3.set_ylabel('Input Complexity')
    ax3.set_xticks(positions)
    ax3.set_xticklabels(labels)
    plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
    
    # Plot 4: Heatmap of Average Input Complexity
    ax4 = axes[1, 0]
    pivot_input_complexity = df.groupby(['violation', 'level'])['input_complexity'].mean().reset_index()
    pivot_input_complexity = pivot_input_complexity.pivot(index='violation', columns='level', values='input_complexity')
    
    sns.heatmap(pivot_input_complexity, annot=True, fmt='.1f', cmap='Reds', ax=ax4, 
                cbar_kws={'label': 'Average Complexity'})
    ax4.set_title('Average Input Complexity Heatmap')
    ax4.set_xlabel('Difficulty Level')
    ax4.set_ylabel('Violation Type')
    
    # Plot 5: Heatmap of Average Output Complexity
    ax5 = axes[1, 1]
    pivot_output_complexity = df.groupby(['violation', 'level'])['output_complexity'].mean().reset_index()
    pivot_output_complexity = pivot_output_complexity.pivot(index='violation', columns='level', values='output_complexity')
    
    sns.heatmap(pivot_output_complexity, annot=True, fmt='.1f', cmap='Blues', ax=ax5, 
                cbar_kws={'label': 'Average Complexity'})
    ax5.set_title('Average Output Complexity Heatmap')
    ax5.set_xlabel('Difficulty Level')
    ax5.set_ylabel('Violation Type')
    
    # Plot 6: Box Plot + Scatter of Output Complexity by Violation and Level
    ax6 = axes[1, 2]
    output_complexity_data = []
    output_labels = []
    output_positions = []
    pos = 1
    
    for violation in violation_types:
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['output_complexity']
            if not data.empty:
                output_complexity_data.append(data)
                output_labels.append(f'{violation}\n{level}')
                output_positions.append(pos)
                pos += 1
    
    # Create box plot
    bp2 = ax6.boxplot(output_complexity_data, positions=output_positions, patch_artist=True, widths=0.6)
    
    # Color the boxes and add scatter points
    pos = 1
    for violation in violation_types:
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['output_complexity']
            if not data.empty:
                # Color the box
                if pos <= len(bp2['boxes']):
                    bp2['boxes'][pos-1].set_facecolor(COLORS[level])
                    bp2['boxes'][pos-1].set_alpha(0.7)
                
                # Add scatter points with jitter
                jitter = np.random.normal(0, 0.1, len(data))
                ax6.scatter([pos] * len(data) + jitter, data, 
                           alpha=0.6, color=COLORS[level], s=20, zorder=3)
                pos += 1
    
    ax6.set_title('Output Complexity Distribution (Box + Scatter)')
    ax6.set_ylabel('Output Complexity')
    ax6.set_xticks(output_positions)
    ax6.set_xticklabels(output_labels)
    plt.setp(ax6.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    if save_plot:
        plt.savefig(COMPLEXITY_OUTPUT_FILE, dpi=300, bbox_inches='tight')
        print(f"Complexity analysis plot saved as {COMPLEXITY_OUTPUT_FILE}")
    
    plt.show()


def print_complexity_statistics(df):
    """Print detailed cyclomatic complexity statistics."""
    print("\n" + "="*60)
    print("CYCLOMATIC COMPLEXITY ANALYSIS")
    print("="*60)
    
    # Calculate complexity changes
    df['complexity_change'] = df['output_complexity'] - df['input_complexity']
    df['complexity_reduction_percent'] = ((df['input_complexity'] - df['output_complexity']) / df['input_complexity']) * 100
    
    print(f"Total records analyzed: {len(df)}")
    
    # Overall complexity statistics
    print(f"\nOverall Input Complexity: Mean={df['input_complexity'].mean():.2f}, Max={df['input_complexity'].max()}")
    print(f"Overall Output Complexity: Mean={df['output_complexity'].mean():.2f}, Max={df['output_complexity'].max()}")
    print(f"Average Complexity Change: {df['complexity_change'].mean():.2f}")
    
    # Find extremes
    max_input_complexity = df.loc[df['input_complexity'].idxmax()]
    max_output_complexity = df.loc[df['output_complexity'].idxmax()]
    max_increase = df.loc[df['complexity_change'].idxmax()]
    max_decrease = df.loc[df['complexity_change'].idxmin()]
    
    print(f"\n" + "="*60)
    print("COMPLEXITY EXTREMES")
    print("="*60)
    print(f"Highest Input Complexity: {max_input_complexity['input_complexity']}")
    print(f"  - {max_input_complexity['violation']}, {max_input_complexity['level']}, {max_input_complexity['language']}")
    
    print(f"Highest Output Complexity: {max_output_complexity['output_complexity']}")
    print(f"  - {max_output_complexity['violation']}, {max_output_complexity['level']}, {max_output_complexity['language']}")
    
    print(f"Largest Complexity Increase: +{max_increase['complexity_change']}")
    print(f"  - {max_increase['violation']}, {max_increase['level']}, {max_increase['language']}")
    
    print(f"Largest Complexity Decrease: {max_decrease['complexity_change']}")
    print(f"  - {max_decrease['violation']}, {max_decrease['level']}, {max_decrease['language']}")
    
    # Statistics by violation type
    print(f"\n" + "="*60)
    print("COMPLEXITY BY VIOLATION TYPE")
    print("="*60)
    complexity_by_violation = df.groupby('violation')[['input_complexity', 'output_complexity', 'complexity_change']].agg(['mean', 'std', 'min', 'max'])
    print(complexity_by_violation.round(2))
    
    # Statistics by difficulty level
    print(f"\n" + "="*60)
    print("COMPLEXITY BY DIFFICULTY LEVEL")
    print("="*60)
    complexity_by_level = df.groupby('level')[['input_complexity', 'output_complexity', 'complexity_change']].agg(['mean', 'std', 'min', 'max'])
    print(complexity_by_level.round(2))
    
    # Effectiveness analysis
    print(f"\n" + "="*60)
    print("COMPLEXITY REDUCTION EFFECTIVENESS")
    print("="*60)
    
    improved = df[df['complexity_change'] < 0]
    worsened = df[df['complexity_change'] > 0]
    unchanged = df[df['complexity_change'] == 0]
    
    print(f"Cases with improved complexity: {len(improved)} ({len(improved)/len(df)*100:.1f}%)")
    print(f"Cases with worsened complexity: {len(worsened)} ({len(worsened)/len(df)*100:.1f}%)")
    print(f"Cases with unchanged complexity: {len(unchanged)} ({len(unchanged)/len(df)*100:.1f}%)")
    
    if len(improved) > 0:
        print(f"Average improvement: {improved['complexity_change'].mean():.2f} ({improved['complexity_reduction_percent'].mean():.1f}%)")
    if len(worsened) > 0:
        print(f"Average worsening: {worsened['complexity_change'].mean():.2f}")


def compare_cyclomatic_complexity(file_path=INPUT_FILE, save_plot=False):
    """Main function to analyze and compare cyclomatic complexity."""
    # Load data
    df = load_data(file_path)
    if df is None:
        return
    
    # Create complexity visualizations
    create_complexity_comparison_plots(df, save_plot)
    
    # Print detailed statistics
    print_complexity_statistics(df)


def analyze_code_complexity(file_path=INPUT_FILE, save_plot=False):
    """Main analysis function."""
    # Ensure plots directory exists
    if save_plot:
        os.makedirs('plots', exist_ok=True)
    
    # Load data
    df = load_data(file_path)
    if df is None:
        return
    
    # Create visualizations
    visualize_code_lengths(df, save_plot)
    
    # Print statistics
    print_summary_statistics(df)



if __name__ == "__main__":
    # Run the code length analysis
    analyze_code_complexity(
        file_path=INPUT_FILE,
        save_plot=True
    )
    
    # Run the cyclomatic complexity comparison
    compare_cyclomatic_complexity(
        file_path=INPUT_FILE,
        save_plot=True
    )






















import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os


"""
Individual Input Distribution Analysis for SOLID Principles Dataset

This script creates individual plots for:
1. Input complexity distribution
2. Input code length distribution

Required libraries: pandas, matplotlib, seaborn, numpy
Input file: cyclomatic_complexity_results.csv
"""

# Configuration
INPUT_FILE = 'cyclomatic_complexity_results.csv'
COLORS = {'EASY': '#2E8B57', 'MODERATE': '#FF8C00', 'HARD': '#DC143C'}
PLOTS_DIR = 'plots'


def load_data(file_path):
    """Load and validate the CSV data."""
    try:
        df = pd.read_csv(file_path)
        print(f"Successfully loaded {len(df)} records from {file_path}")
        return df
    except FileNotFoundError:
        print(f"Error: File {file_path} not found!")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def plot_input_complexity_distribution(df, save_plot=False):
    """Create comprehensive input complexity distribution plot."""
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Input Complexity Distribution Analysis', fontsize=16, fontweight='bold')
    
    violation_types = df['violation'].unique()
    
    # Plot 1: Scatter plot by violation type and level
    ax1 = axes[0, 0]
    for i, violation in enumerate(violation_types):
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_complexity']
            if not data.empty:
                ax1.scatter([i] * len(data), data, alpha=0.6, color=COLORS[level], 
                          label=level if i == 0 else "", s=40)
    
    ax1.set_xlabel('Violation Type')
    ax1.set_ylabel('Input Complexity')
    # ax1.set_title('Input Complexity by Violation Type and Level')
    ax1.set_xticks(range(len(violation_types)))
    ax1.set_xticklabels(violation_types)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Box plot with scatter overlay
    ax2 = axes[0, 1]
    complexity_data = []
    labels = []
    positions = []
    pos = 1
    
    for violation in violation_types:
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_complexity']
            if not data.empty:
                complexity_data.append(data)
                labels.append(f'{violation}\n{level}')
                positions.append(pos)
                pos += 1
    
    # Create box plot
    bp = ax2.boxplot(complexity_data, positions=positions, patch_artist=True, widths=0.6)
    
    # Color the boxes and add scatter points
    pos = 1
    for violation in violation_types:
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_complexity']
            if not data.empty:
                # Color the box
                if pos <= len(bp['boxes']):
                    bp['boxes'][pos-1].set_facecolor(COLORS[level])
                    bp['boxes'][pos-1].set_alpha(0.7)
                
                # Add scatter points with jitter
                jitter = np.random.normal(0, 0.1, len(data))
                ax2.scatter([pos] * len(data) + jitter, data, 
                           alpha=0.6, color=COLORS[level], s=20, zorder=3)
                pos += 1
    
    ax2.set_title('Input Complexity Distribution (Box + Scatter)')
    ax2.set_ylabel('Input Complexity')
    ax2.set_xticks(positions)
    ax2.set_xticklabels(labels)
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    
    # Plot 3: Heatmap of average input complexity
    ax3 = axes[1, 0]
    pivot_input_complexity = df.groupby(['violation', 'level'])['input_complexity'].mean().reset_index()
    pivot_input_complexity = pivot_input_complexity.pivot(index='violation', columns='level', values='input_complexity')
    
    sns.heatmap(pivot_input_complexity, annot=True, fmt='.1f', cmap='Reds', ax=ax3, 
                cbar_kws={'label': 'Average Complexity'})
    ax3.set_title('Average Input Complexity Heatmap')
    ax3.set_xlabel('Difficulty Level')
    ax3.set_ylabel('Violation Type')
    
    # Plot 4: Histogram/Distribution by level
    ax4 = axes[1, 1]
    for level in ['EASY', 'MODERATE', 'HARD']:
        data = df[df['level'] == level]['input_complexity']
        if not data.empty:
            ax4.hist(data, alpha=0.6, color=COLORS[level], label=level, bins=20)
    
    ax4.set_xlabel('Input Complexity')
    ax4.set_ylabel('Frequency')
    ax4.set_title('Input Complexity Distribution by Difficulty Level')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_plot:
        os.makedirs(PLOTS_DIR, exist_ok=True)
        output_file = os.path.join(PLOTS_DIR, 'input_complexity_distribution.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Input complexity distribution plot saved as {output_file}")
    
    plt.show()


def plot_input_code_length_distribution(df, save_plot=False):
    """Create comprehensive input code length distribution plot."""
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Input Code Length Distribution Analysis', fontsize=16, fontweight='bold')
    
    violation_types = df['violation'].unique()
    
    # Plot 1: Scatter plot by violation type and level
    ax1 = axes[0, 0]
    for i, violation in enumerate(violation_types):
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_code_length']
            if not data.empty:
                ax1.scatter([i] * len(data), data, alpha=0.6, color=COLORS[level], 
                          label=level if i == 0 else "", s=40)
    
    ax1.set_xlabel('Violation Type')
    ax1.set_ylabel('Input Code Length')
    # ax1.set_title('Input Code Length by Violation Type and Level')
    ax1.set_xticks(range(len(violation_types)))
    ax1.set_xticklabels(violation_types)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Box plot with scatter overlay
    ax2 = axes[0, 1]
    length_data = []
    labels = []
    positions = []
    pos = 1
    
    for violation in violation_types:
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_code_length']
            if not data.empty:
                length_data.append(data)
                labels.append(f'{violation}\n{level}')
                positions.append(pos)
                pos += 1
    
    # Create box plot
    bp = ax2.boxplot(length_data, positions=positions, patch_artist=True, widths=0.6)
    
    # Color the boxes and add scatter points
    pos = 1
    for violation in violation_types:
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_code_length']
            if not data.empty:
                # Color the box
                if pos <= len(bp['boxes']):
                    bp['boxes'][pos-1].set_facecolor(COLORS[level])
                    bp['boxes'][pos-1].set_alpha(0.7)
                
                # Add scatter points with jitter
                jitter = np.random.normal(0, 0.1, len(data))
                ax2.scatter([pos] * len(data) + jitter, data, 
                           alpha=0.6, color=COLORS[level], s=20, zorder=3)
                pos += 1
    
    ax2.set_title('Input Code Length Distribution (Box + Scatter)')
    ax2.set_ylabel('Input Code Length')
    ax2.set_xticks(positions)
    ax2.set_xticklabels(labels)
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    
    # Plot 3: Heatmap of average input code length
    ax3 = axes[1, 0]
    pivot_input_length = df.groupby(['violation', 'level'])['input_code_length'].mean().reset_index()
    pivot_input_length = pivot_input_length.pivot(index='violation', columns='level', values='input_code_length')
    
    sns.heatmap(pivot_input_length, annot=True, fmt='.0f', cmap='Blues', ax=ax3, 
                cbar_kws={'label': 'Average Code Length'})
    ax3.set_title('Average Input Code Length Heatmap')
    ax3.set_xlabel('Difficulty Level')
    ax3.set_ylabel('Violation Type')
    
    # Plot 4: Histogram/Distribution by level
    ax4 = axes[1, 1]
    for level in ['EASY', 'MODERATE', 'HARD']:
        data = df[df['level'] == level]['input_code_length']
        if not data.empty:
            ax4.hist(data, alpha=0.6, color=COLORS[level], label=level, bins=20)
    
    ax4.set_xlabel('Input Code Length')
    ax4.set_ylabel('Frequency')
    ax4.set_title('Input Code Length Distribution by Difficulty Level')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_plot:
        os.makedirs(PLOTS_DIR, exist_ok=True)
        output_file = os.path.join(PLOTS_DIR, 'input_code_length_distribution.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Input code length distribution plot saved as {output_file}")
    
    plt.show()


def print_input_statistics(df):
    """Print statistics for input complexity and code length."""
    print("\n" + "="*60)
    print("INPUT DISTRIBUTION STATISTICS")
    print("="*60)
    
    print(f"Total records: {len(df)}")
    print(f"Violation types: {list(df['violation'].unique())}")
    print(f"Difficulty levels: {list(df['level'].unique())}")
    
    # Input complexity statistics
    print("\n" + "="*60)
    print("INPUT COMPLEXITY STATISTICS")
    print("="*60)
    print(f"Mean: {df['input_complexity'].mean():.2f}")
    print(f"Median: {df['input_complexity'].median():.2f}")
    print(f"Standard deviation: {df['input_complexity'].std():.2f}")
    print(f"Min: {df['input_complexity'].min()}")
    print(f"Max: {df['input_complexity'].max()}")
    
    # Find highest complexity case
    max_complexity = df.loc[df['input_complexity'].idxmax()]
    print(f"\nHighest complexity case: {max_complexity['input_complexity']}")
    print(f"  - Violation: {max_complexity['violation']}")
    print(f"  - Level: {max_complexity['level']}")
    print(f"  - Language: {max_complexity['language']}")
    
    # Complexity by level
    print("\nComplexity by difficulty level:")
    complexity_by_level = df.groupby('level')['input_complexity'].agg(['mean', 'median', 'std', 'min', 'max'])
    print(complexity_by_level.round(2))
    
    # Complexity by violation type
    print("\nComplexity by violation type:")
    complexity_by_violation = df.groupby('violation')['input_complexity'].agg(['mean', 'median', 'std', 'min', 'max'])
    print(complexity_by_violation.round(2))
    
    # Input code length statistics
    print("\n" + "="*60)
    print("INPUT CODE LENGTH STATISTICS")
    print("="*60)
    print(f"Mean: {df['input_code_length'].mean():.2f}")
    print(f"Median: {df['input_code_length'].median():.2f}")
    print(f"Standard deviation: {df['input_code_length'].std():.2f}")
    print(f"Min: {df['input_code_length'].min()}")
    print(f"Max: {df['input_code_length'].max()}")
    
    # Find longest code case
    max_length = df.loc[df['input_code_length'].idxmax()]
    print(f"\nLongest code case: {max_length['input_code_length']} characters")
    print(f"  - Violation: {max_length['violation']}")
    print(f"  - Level: {max_length['level']}")
    print(f"  - Language: {max_length['language']}")
    
    # Code length by level
    print("\nCode length by difficulty level:")
    length_by_level = df.groupby('level')['input_code_length'].agg(['mean', 'median', 'std', 'min', 'max'])
    print(length_by_level.round(2))
    
    # Code length by violation type
    print("\nCode length by violation type:")
    length_by_violation = df.groupby('violation')['input_code_length'].agg(['mean', 'median', 'std', 'min', 'max'])
    print(length_by_violation.round(2))


def analyze_input_distributions(file_path=INPUT_FILE, save_plots=False):
    """Main function to analyze input distributions."""
    # Load data
    df = load_data(file_path)
    if df is None:
        return
    
    # Create input complexity distribution plot
    plot_input_complexity_distribution(df, save_plots)
    
    # Create input code length distribution plot
    plot_input_code_length_distribution(df, save_plots)
    
    # Print statistics
    print_input_statistics(df)


if __name__ == "__main__":
    # Run the input distribution analysis
    analyze_input_distributions(
        file_path=INPUT_FILE,
        save_plots=True
    )






































import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os


"""
Box Plot Distribution Analysis for SOLID Principles Dataset

This script creates individual box plot visualizations for:
1. Input complexity distribution (box plot with scatter overlay)
2. Input code length distribution (box plot with scatter overlay)

Required libraries: pandas, matplotlib, seaborn, numpy
Input file: cyclomatic_complexity_results.csv
"""

# Configuration
INPUT_FILE = 'cyclomatic_complexity_results.csv'
COLORS = {'EASY': '#2E8B57', 'MODERATE': '#FF8C00', 'HARD': '#DC143C'}
PLOTS_DIR = 'plots'


def load_data(file_path):
    """Load and validate the CSV data."""
    try:
        df = pd.read_csv(file_path)
        print(f"Successfully loaded {len(df)} records from {file_path}")
        return df
    except FileNotFoundError:
        print(f"Error: File {file_path} not found!")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def plot_input_complexity_boxplot(df, save_plot=False):
    """Create box plot with scatter overlay for input complexity distribution."""
    
    # Create figure
    plt.figure(figsize=(14, 8))
    
    violation_types = df['violation'].unique()
    
    # Prepare data for box plot
    complexity_data = []
    labels = []
    positions = []
    pos = 1
    
    for violation in violation_types:
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_complexity']
            if not data.empty:
                complexity_data.append(data)
                labels.append(f'{violation} {level}')  # Single line format
                positions.append(pos)
                pos += 1
    
    # Create box plot
    bp = plt.boxplot(complexity_data, positions=positions, patch_artist=True, widths=0.6)
    
    # Color the boxes and add scatter points
    pos = 1
    for violation in violation_types:
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_complexity']
            if not data.empty:
                # Color the box
                if pos <= len(bp['boxes']):
                    bp['boxes'][pos-1].set_facecolor(COLORS[level])
                    bp['boxes'][pos-1].set_alpha(0.7)
                
                # Add scatter points with jitter
                jitter = np.random.normal(0, 0.1, len(data))
                plt.scatter([pos] * len(data) + jitter, data, 
                           alpha=0.6, color=COLORS[level], s=30, zorder=3)
                pos += 1
    
    plt.title('Input Complexity Distribution (Box Plot with Scatter)', fontsize=14, fontweight='bold')
    plt.ylabel('Input Complexity', fontsize=12)
    plt.xlabel('Violation Type and Difficulty Level', fontsize=12)
    plt.xticks(positions, labels)
    plt.setp(plt.gca().get_xticklabels(), rotation=45, ha='right')
    
    # Remove top and right spines
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add legend
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                 markerfacecolor=COLORS[level], markersize=8, label=level)
                      for level in ['EASY', 'MODERATE', 'HARD']]
    plt.legend(handles=legend_elements, title='Difficulty Level', loc='upper right')
    
    plt.tight_layout()
    
    if save_plot:
        os.makedirs(PLOTS_DIR, exist_ok=True)
        output_file = os.path.join(PLOTS_DIR, 'input_complexity_boxplot.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Input complexity box plot saved as {output_file}")
    
    plt.show()


def plot_input_code_length_boxplot(df, save_plot=False):
    """Create box plot with scatter overlay for input code length distribution."""
    
    # Create figure
    plt.figure(figsize=(14, 8))
    
    violation_types = df['violation'].unique()
    
    # Prepare data for box plot
    length_data = []
    labels = []
    positions = []
    pos = 1
    
    for violation in violation_types:
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_code_length']
            if not data.empty:
                length_data.append(data)
                labels.append(f'{violation}\n{level}')
                positions.append(pos)
                pos += 1
    
    # Create box plot
    bp = plt.boxplot(length_data, positions=positions, patch_artist=True, widths=0.6)
    
    # Color the boxes and add scatter points
    pos = 1
    for violation in violation_types:
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_code_length']
            if not data.empty:
                # Color the box
                if pos <= len(bp['boxes']):
                    bp['boxes'][pos-1].set_facecolor(COLORS[level])
                    bp['boxes'][pos-1].set_alpha(0.7)
                
                # Add scatter points with jitter
                jitter = np.random.normal(0, 0.1, len(data))
                plt.scatter([pos] * len(data) + jitter, data, 
                           alpha=0.6, color=COLORS[level], s=30, zorder=3)
                pos += 1
    
    plt.title('Input Code Length Distribution (Box Plot with Scatter)', fontsize=14, fontweight='bold')
    plt.ylabel('Input Code Length', fontsize=12)
    plt.xlabel('Violation Type and Difficulty Level', fontsize=12)
    plt.xticks(positions, labels)
    plt.setp(plt.gca().get_xticklabels(), rotation=45, ha='right')
    
    # Remove top and right spines
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add legend
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                 markerfacecolor=COLORS[level], markersize=8, label=level)
                      for level in ['EASY', 'MODERATE', 'HARD']]
    plt.legend(handles=legend_elements, title='Difficulty Level', loc='upper right')
    
    plt.tight_layout()
    
    if save_plot:
        os.makedirs(PLOTS_DIR, exist_ok=True)
        output_file = os.path.join(PLOTS_DIR, 'input_code_length_boxplot.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Input code length box plot saved as {output_file}")
    
    plt.show()


def print_boxplot_statistics(df):
    """Print summary statistics for the box plot visualizations."""
    print("\n" + "="*60)
    print("BOX PLOT DISTRIBUTION STATISTICS")
    print("="*60)
    
    print(f"Total records: {len(df)}")
    print(f"Violation types: {list(df['violation'].unique())}")
    print(f"Difficulty levels: {list(df['level'].unique())}")
    
    # Input complexity quartile statistics
    print("\n" + "="*60)
    print("INPUT COMPLEXITY - QUARTILE STATISTICS BY GROUP")
    print("="*60)
    
    for violation in df['violation'].unique():
        print(f"\n{violation}:")
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_complexity']
            if not data.empty:
                q1 = data.quantile(0.25)
                median = data.median()
                q3 = data.quantile(0.75)
                iqr = q3 - q1
                print(f"  {level:8}: Q1={q1:5.1f}, Median={median:5.1f}, Q3={q3:5.1f}, IQR={iqr:5.1f}, n={len(data)}")
    
    # Input code length quartile statistics
    print("\n" + "="*60)
    print("INPUT CODE LENGTH - QUARTILE STATISTICS BY GROUP")
    print("="*60)
    
    for violation in df['violation'].unique():
        print(f"\n{violation}:")
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_code_length']
            if not data.empty:
                q1 = data.quantile(0.25)
                median = data.median()
                q3 = data.quantile(0.75)
                iqr = q3 - q1
                print(f"  {level:8}: Q1={q1:6.0f}, Median={median:6.0f}, Q3={q3:6.0f}, IQR={iqr:6.0f}, n={len(data)}")


def plot_combined_input_boxplots(df, save_plot=False):
    """Create combined box plots for both input complexity and code length distributions."""
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
    
    violation_types = df['violation'].unique()
    
    # Plot 1: Input Complexity
    complexity_data = []
    labels = []
    positions = []
    pos = 1
    
    for violation in violation_types:
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_complexity']
            if not data.empty:
                complexity_data.append(data)
                labels.append(f'{violation}\n{level}')
                positions.append(pos)
                pos += 1
    
    # Create box plot for complexity
    bp1 = ax1.boxplot(complexity_data, positions=positions, patch_artist=True, widths=0.6)
    
    # Color the boxes and add scatter points for complexity
    pos = 1
    for violation in violation_types:
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_complexity']
            if not data.empty:
                # Color the box
                if pos <= len(bp1['boxes']):
                    bp1['boxes'][pos-1].set_facecolor(COLORS[level])
                    bp1['boxes'][pos-1].set_alpha(0.7)
                
                # Add scatter points with jitter
                jitter = np.random.normal(0, 0.1, len(data))
                ax1.scatter([pos] * len(data) + jitter, data, 
                           alpha=0.6, color=COLORS[level], s=30, zorder=3)
                pos += 1
    
    ax1.set_ylabel('Input Complexity', fontsize=20)
    ax1.set_xticks(positions)
    ax1.set_xticklabels([])  # Remove x-axis labels for upper plot
    
    # Remove top and right spines for complexity plot
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # Plot 2: Input Code Length
    length_data = []
    length_labels = []
    length_positions = []
    pos = 1
    
    for violation in violation_types:
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_code_length']
            if not data.empty:
                length_data.append(data)
                length_labels.append(f'{violation} {level}')  # Single line format
                length_positions.append(pos)
                pos += 1
    
    # Create box plot for code length
    bp2 = ax2.boxplot(length_data, positions=length_positions, patch_artist=True, widths=0.6)
    
    # Color the boxes and add scatter points for code length
    pos = 1
    for violation in violation_types:
        for level in ['EASY', 'MODERATE', 'HARD']:
            data = df[(df['violation'] == violation) & (df['level'] == level)]['input_code_length']
            if not data.empty:
                # Color the box
                if pos <= len(bp2['boxes']):
                    bp2['boxes'][pos-1].set_facecolor(COLORS[level])
                    bp2['boxes'][pos-1].set_alpha(0.7)
                
                # Add scatter points with jitter
                jitter = np.random.normal(0, 0.1, len(data))
                ax2.scatter([pos] * len(data) + jitter, data, 
                           alpha=0.6, color=COLORS[level], s=30, zorder=3)
                pos += 1
    
    ax2.set_ylabel('Input Code Length', fontsize=20)
    ax2.set_xticks(length_positions)
    ax2.set_xticklabels(length_labels)
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right', fontsize=18)
    
    # Remove top and right spines for code length plot
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    # Add legend to the first subplot
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                 markerfacecolor=COLORS[level], markersize=12, label=level)
                      for level in ['EASY', 'MODERATE', 'HARD']]
    ax1.legend(handles=legend_elements, title='Difficulty Level', loc='upper right', 
               fontsize=16, title_fontsize=18)
    
    plt.tight_layout()
    
    if save_plot:
        os.makedirs(PLOTS_DIR, exist_ok=True)
        output_file = os.path.join(PLOTS_DIR, 'combined_input_boxplots.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Combined input box plots saved as {output_file}")
    
    plt.show()


def analyze_input_boxplots(file_path=INPUT_FILE, save_plots=False):
    """Main function to create box plot visualizations for input distributions."""
    # Load data
    df = load_data(file_path)
    if df is None:
        return
    
    # Create combined box plots
    plot_combined_input_boxplots(df, save_plots)
    
    # Create individual box plots (optional)
    # plot_input_complexity_boxplot(df, save_plots)
    # plot_input_code_length_boxplot(df, save_plots)
    
    # Print box plot specific statistics
    print_boxplot_statistics(df)


if __name__ == "__main__":
    # Run the box plot analysis
    analyze_input_boxplots(
        file_path=INPUT_FILE,
        save_plots=True
    )