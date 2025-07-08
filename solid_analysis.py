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

if __name__ == "__main__":
    main()