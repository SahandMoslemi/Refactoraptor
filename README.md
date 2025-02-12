# Refactoraptor 🦖

## Background & Motivation
Developers often overlook **SOLID principles**, leading to **maintainability** and **scalability** issues. While **LLMs** show promise in **code analysis**, their effectiveness in detecting and refactoring **OOP violations** remains unclear.

## Objectives
This project aims to develop a **locally deployable LLM-based tool** that detects and refactors violations in:

- **Single Responsibility Principle (SRP)**
- **Open-Closed Principle (OCP)**
- **Liskov Substitution Principle (LSP)**
- **Interface Segregation Principle (ISP)**

The goal is to assess **LLM performance and limitations** in **automated code quality improvements**.

## Methodology
1. Users will **input a code snippet** or a **set of files**.
2. The UI will allow the selection of a **locally installed LLM**, automatically listed via **Ollama CLI/API**.
3. A **prompt engineering strategy** will be chosen to guide the analysis.
4. The tool will **identify violations** and suggest **refactoring solutions**, displaying results interactively.

## Expected Outcomes
- A **functional and locally runnable tool** capable of detecting **SOLID principle violations**.
- **Comparative analysis** of different **prompt strategies** and **small LLMs**.

## Evaluation Metrics
- The tool’s **input and output** will be evaluated using **ChatGPT-4o**, assessing the **degree of improvement achieved**.
