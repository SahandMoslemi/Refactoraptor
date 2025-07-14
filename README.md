# Replication Package for 'Are We SOLID Yet? An Empirical Study on Prompting LLMs to Detect Design Principle Violations'

## Background & Motivation
Developers often overlook **SOLID principles**, leading to **maintainability** and **scalability** issues. While **LLMs** show promise in **code analysis**, their effectiveness in detecting and refactoring **OOP violations** remains unclear.

## Objectives
This project aims to develop a **locally deployable LLM-based tool** that detects and refactors violations in:

- **Single Responsibility Principle (SRP)**
- **Open-Closed Principle (OCP)**
- **Liskov Substitution Principle (LSP)**
- **Interface Segregation Principle (ISP)**
- **Dependency Inversion Principle**

Our goal is to systematically evaluate LLM performance across principles, programming languages, and prompt strategies.


## Dataset

We provide 240 synthetic examples covering all five SOLID principles, across:

- **4 programming languages**: Java, Python, Kotlin, and C#
- **3 difficulty levels**: Easy, Moderate, Hard
- **4 examples per principle × 3 levels × 4 languages**

### Dataset Location

- `dataset/creation_scenarios.md`: Describes the violation scenarios.
- `dataset/groundtruth/`: Ground-truth labeled samples.
- `dataset/completions/test/`: LLM outputs on test examples.


## Evaluation Methodology

- Each sample’s detected violation is compared against its ground truth label.
- Performance metrics include **accuracy** and **F1-score**, broken down by model, principle, language, and difficulty.

### Evaluation Artifacts

- `evaluation_final/`: Contains all accuracy/F1 plots and CSVs by model, strategy, language, and level.
- `detailed_results_final.json`: Full sample-level results including model, strategy, expected/detected violations, language, and difficulty level.



