import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style for better-looking plots
plt.style.use('default')
sns.set_palette("husl")

def load_and_clean_data():
    """Load and clean the CSV files"""
    # Load the data
    language_df = pd.read_csv('metrics_by_language.csv')
    model_df = pd.read_csv('metrics_by_model.csv')
    strategy_df = pd.read_csv('metrics_by_strategy.csv')
    
    # Clean language names - standardize C# variants
    language_df['language'] = language_df['language'].replace('CSHARP', 'C#')
    
    # Convert language names to title case for consistency
    language_df['language'] = language_df['language'].replace({
        'JAVA': 'Java',
        'PYTHON': 'Python',
        'KOTLIN': 'Kotlin'
    })
    
    return language_df, model_df, strategy_df

def plot_accuracy_by_language_and_violation(language_df):
    """Plot 1: Detection accuracy across programming languages and SOLID principles"""
    
    # Filter for the four main languages
    target_languages = ['Java', 'Python', 'Kotlin', 'C#']
    filtered_df = language_df[language_df['language'].isin(target_languages)]
    
    # Group by language and violation to get average accuracy
    accuracy_pivot = filtered_df.groupby(['language', 'violation'])['accuracy'].mean().reset_index()
    accuracy_pivot_table = accuracy_pivot.pivot(index='violation', columns='language', values='accuracy')
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create heatmap
    sns.heatmap(accuracy_pivot_table, 
                annot=True, 
                fmt='.3f', 
                cmap='RdYlBu_r',
                cbar_kws={'label': 'Detection Accuracy'},
                ax=ax)
    
    plt.title('Detection Accuracy Across Programming Languages and SOLID Principles', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Programming Language', fontsize=12, fontweight='bold')
    plt.ylabel('SOLID Principle', fontsize=12, fontweight='bold')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    
    # Add grid for better readability
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_f1_scores_by_strategy_and_model(model_df):
    """Plot 2: F1-scores of SOLID violation detection across prompt strategies and models"""
    
    # Group by strategy and model to get average F1 scores across all violations
    f1_grouped = model_df.groupby(['strategy', 'model'])['f1_score'].mean().reset_index()
    
    # Create pivot table for heatmap
    f1_pivot = f1_grouped.pivot(index='strategy', columns='model', values='f1_score')
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Shorten model names for better display
    model_names = {
        'codellama70b-temp0:latest': 'CodeLlama 70B',
        'deepseek33b-temp0:latest': 'DeepSeek 33B',
        'gpt-4o-mini': 'GPT-4o Mini',
        'qwen2.5-coder32b-temp0:latest': 'Qwen2.5 Coder 32B'
    }
    
    f1_pivot.columns = [model_names.get(col, col) for col in f1_pivot.columns]
    
    # Create heatmap
    sns.heatmap(f1_pivot, 
                annot=True, 
                fmt='.3f', 
                cmap='viridis',
                cbar_kws={'label': 'Average F1-Score'},
                ax=ax)
    
    plt.title('F1-Scores of SOLID Violation Detection Across Prompt Strategies and Models', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Model', fontsize=12, fontweight='bold')
    plt.ylabel('Prompt Strategy', fontsize=12, fontweight='bold')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    return fig

def create_additional_analysis_plot(language_df, model_df):
    """Additional plot: Compare F1 scores across strategies for each SOLID principle"""
    
    # Group by violation and strategy to get average F1 scores
    violation_strategy = model_df.groupby(['violation', 'strategy'])['f1_score'].mean().reset_index()
    
    # Create subplot for each SOLID principle
    fig, axes = plt.subplots(1, 5, figsize=(20, 4))
    fig.suptitle('F1-Scores by Strategy for Each SOLID Principle', fontsize=16, fontweight='bold')
    
    violations = sorted(violation_strategy['violation'].unique())
    strategies = sorted(violation_strategy['strategy'].unique())
    
    for i, violation in enumerate(violations):
        data = violation_strategy[violation_strategy['violation'] == violation]
        
        # Create bar plot
        axes[i].bar(data['strategy'], data['f1_score'], alpha=0.8)
        axes[i].set_title(f'{violation}', fontweight='bold')
        axes[i].set_ylabel('F1-Score' if i == 0 else '')
        axes[i].set_xlabel('Strategy')
        axes[i].tick_params(axis='x', rotation=45)
        axes[i].grid(True, alpha=0.3)
        
        # Set consistent y-axis limits
        axes[i].set_ylim(0, max(violation_strategy['f1_score']) * 1.1)
    
    plt.tight_layout()
    return fig

def plot_gpt_model_analysis(model_df, language_df):
    """GPT-4o Mini specific analysis plots"""
    
    # Filter for GPT-4o Mini model
    gpt_data = model_df[model_df['model'] == 'gpt-4o-mini'].copy()
    
    if gpt_data.empty:
        print("No GPT-4o Mini data found in the dataset.")
        return None, None
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    #fig.suptitle('GPT-4o Mini Performance Analysis', fontsize=18, fontweight='bold', y=0.98)
    
    # Plot 1: F1-scores by strategy and violation (heatmap)
    f1_pivot = gpt_data.pivot(index='violation', columns='strategy', values='f1_score')
    sns.heatmap(f1_pivot, 
                annot=True, 
                fmt='.3f', 
                cmap='Blues',
                cbar_kws={'label': 'F1-Score'},
                ax=ax1)
    ax1.set_title('F1-Scores by Strategy and SOLID Principle', fontweight='bold')
    ax1.set_xlabel('Strategy')
    ax1.set_ylabel('SOLID Principle')
    
    # Plot 2: Accuracy by strategy and violation (heatmap)
    acc_pivot = gpt_data.pivot(index='violation', columns='strategy', values='accuracy')
    sns.heatmap(acc_pivot, 
                annot=True, 
                fmt='.3f', 
                cmap='Greens',
                cbar_kws={'label': 'Accuracy'},
                ax=ax2)
    ax2.set_title('Accuracy by Strategy and SOLID Principle', fontweight='bold')
    ax2.set_xlabel('Strategy')
    ax2.set_ylabel('SOLID Principle')
    
    # Plot 3: Performance metrics comparison (bar chart)
    """ metrics_by_strategy = gpt_data.groupby('strategy')[['accuracy', 'precision', 'recall', 'f1_score']].mean()
    x = np.arange(len(metrics_by_strategy.index))
    width = 0.2
    
    ax3.bar(x - 1.5*width, metrics_by_strategy['accuracy'], width, label='Accuracy', alpha=0.8)
    ax3.bar(x - 0.5*width, metrics_by_strategy['precision'], width, label='Precision', alpha=0.8)
    ax3.bar(x + 0.5*width, metrics_by_strategy['recall'], width, label='Recall', alpha=0.8)
    ax3.bar(x + 1.5*width, metrics_by_strategy['f1_score'], width, label='F1-Score', alpha=0.8)
    
    ax3.set_title('Performance Metrics by Strategy', fontweight='bold')
    ax3.set_xlabel('Strategy')
    ax3.set_ylabel('Score')
    ax3.set_xticks(x)
    ax3.set_xticklabels(metrics_by_strategy.index)
    ax3.legend()
    ax3.grid(True, alpha=0.3) """
    
    # Plot 4: F1-scores by SOLID principle (bar chart)
    f1_by_violation = gpt_data.groupby('violation')['f1_score'].mean().sort_values(ascending=False)
    colors = plt.cm.viridis(np.linspace(0, 1, len(f1_by_violation)))
    bars = ax4.bar(f1_by_violation.index, f1_by_violation.values, color=colors, alpha=0.8)
    ax4.set_title('Average F1-Score by SOLID Principle', fontweight='bold')
    ax4.set_xlabel('SOLID Principle')
    ax4.set_ylabel('Average F1-Score')
    ax4.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, value in zip(bars, f1_by_violation.values):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005, 
                f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    return fig

def plot_gpt_comparison_with_others(model_df):
    """Compare GPT-4o Mini with other models"""
    
    # Create comparison plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('GPT-4o Mini vs Other Models Comparison', fontsize=16, fontweight='bold')
    
    # Plot 1: Average F1-scores by model
    model_performance = model_df.groupby('model')['f1_score'].mean().sort_values(ascending=False)
    
    # Color GPT-4o Mini differently
    colors = ['#ff7f0e' if 'gpt-4o-mini' in model else '#1f77b4' for model in model_performance.index]
    
    # Shorten model names for display
    model_names = {
        'codellama70b-temp0:latest': 'CodeLlama 70B',
        'deepseek33b-temp0:latest': 'DeepSeek 33B',
        'gpt-4o-mini': 'GPT-4o Mini',
        'qwen2.5-coder32b-temp0:latest': 'Qwen2.5 Coder 32B'
    }
    
    display_names = [model_names.get(model, model) for model in model_performance.index]
    
    bars1 = ax1.bar(display_names, model_performance.values, color=colors, alpha=0.8)
    ax1.set_title('Average F1-Score by Model', fontweight='bold')
    ax1.set_ylabel('Average F1-Score')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, value in zip(bars1, model_performance.values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005, 
                f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # Plot 2: F1-scores by strategy for each model
    strategy_model_performance = model_df.groupby(['strategy', 'model'])['f1_score'].mean().reset_index()
    strategy_pivot = strategy_model_performance.pivot(index='strategy', columns='model', values='f1_score')
    strategy_pivot.columns = [model_names.get(col, col) for col in strategy_pivot.columns]
    
    strategy_pivot.plot(kind='bar', ax=ax2, alpha=0.8)
    ax2.set_title('F1-Scores by Strategy and Model', fontweight='bold')
    ax2.set_xlabel('Strategy')
    ax2.set_ylabel('F1-Score')
    ax2.tick_params(axis='x', rotation=45)
    ax2.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def main():
    """Main function to generate all plots"""
    # Load and clean data
    language_df, model_df, strategy_df = load_and_clean_data()
    
    # Create plots
    print("Creating Plot 1: Detection Accuracy by Language and SOLID Principle...")
    fig1 = plot_accuracy_by_language_and_violation(language_df)
    plt.show()
    
    print("\nCreating Plot 2: F1-Scores by Strategy and Model...")
    fig2 = plot_f1_scores_by_strategy_and_model(model_df)
    plt.show()
    
    print("\nCreating Additional Analysis: F1-Scores by Strategy for Each SOLID Principle...")
    fig3 = create_additional_analysis_plot(language_df, model_df)
    plt.show()
    
    print("\nCreating GPT-4o Mini Specific Analysis...")
    fig4 = plot_gpt_model_analysis(model_df, language_df)
    if fig4:
        plt.show()
    
    print("\nCreating GPT-4o Mini Comparison with Other Models...")
    fig5 = plot_gpt_comparison_with_others(model_df)
    plt.show()
    
    # Print summary statistics
    print("\n" + "="*50)
    print("SUMMARY STATISTICS")
    print("="*50)
    
    print("\nLanguage Performance (Average Accuracy):")
    lang_performance = language_df.groupby('language')['accuracy'].mean().sort_values(ascending=False)
    for lang, acc in lang_performance.items():
        print(f"  {lang}: {acc:.3f}")
    
    print("\nModel Performance (Average F1-Score):")
    model_performance = model_df.groupby('model')['f1_score'].mean().sort_values(ascending=False)
    for model, f1 in model_performance.items():
        print(f"  {model}: {f1:.3f}")
    
    print("\nStrategy Performance (Average F1-Score):")
    strategy_performance = model_df.groupby('strategy')['f1_score'].mean().sort_values(ascending=False)
    for strategy, f1 in strategy_performance.items():
        print(f"  {strategy}: {f1:.3f}")
    
    # GPT-4o Mini specific statistics
    gpt_data = model_df[model_df['model'] == 'gpt-4o-mini']
    if not gpt_data.empty:
        print("\n" + "="*50)
        print("GPT-4o MINI SPECIFIC STATISTICS")
        print("="*50)
        
        print("\nGPT-4o Mini Performance by Strategy:")
        gpt_strategy_performance = gpt_data.groupby('strategy')['f1_score'].mean().sort_values(ascending=False)
        for strategy, f1 in gpt_strategy_performance.items():
            print(f"  {strategy}: {f1:.3f}")
        
        print("\nGPT-4o Mini Performance by SOLID Principle:")
        gpt_violation_performance = gpt_data.groupby('violation')['f1_score'].mean().sort_values(ascending=False)
        for violation, f1 in gpt_violation_performance.items():
            print(f"  {violation}: {f1:.3f}")
        
        print(f"\nGPT-4o Mini Overall Average F1-Score: {gpt_data['f1_score'].mean():.3f}")
        print(f"GPT-4o Mini Overall Average Accuracy: {gpt_data['accuracy'].mean():.3f}")
        
        # Best and worst performing combinations
        best_combo = gpt_data.loc[gpt_data['f1_score'].idxmax()]
        worst_combo = gpt_data.loc[gpt_data['f1_score'].idxmin()]
        
        print(f"\nBest GPT-4o Mini Performance:")
        print(f"  Strategy: {best_combo['strategy']}, Violation: {best_combo['violation']}")
        print(f"  F1-Score: {best_combo['f1_score']:.3f}, Accuracy: {best_combo['accuracy']:.3f}")
        
        print(f"\nWorst GPT-4o Mini Performance:")
        print(f"  Strategy: {worst_combo['strategy']}, Violation: {worst_combo['violation']}")
        print(f"  F1-Score: {worst_combo['f1_score']:.3f}, Accuracy: {worst_combo['accuracy']:.3f}")

if __name__ == "__main__":
    main()