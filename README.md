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

## Evaluation Methodology
- We will generate synthetic Java, C#, C++ and Python code snippets as evaluation data. These code snippets will be labeled with corresponding SOLI violations. These will serve as ground truth for classification.
- Initially, the detection will be checked against the ground truth. If the detection is true positive, original code snippet and refactored code will be provided to **ChatGPT-4o** with appropriate prompts, to assess the correctness of detection and quality of refactoring.
- We will conduct a user survey on the accuracy of the refactoring tool, if time permits.

## Team Work Distribution
- Backend development will be done by: M. Buğra Kurnaz & Rafi Çoktalaş
- Frontend development will be done by: Arçin Ülkü Ergüzen & Fatih Pehlivan
- We will split SOLI principles as follows: 
    - **Single Responsibility Principle (SRP)**: Rafi Çoktalaş
    - **Open-Closed Principle (OCP)**: Fatih Pehlivan
    - **Liskov Substitution Principle (LSP)**: M. Buğra Kurnaz
    - **Interface Segregation Principle (ISP)**: Arçin Ülkü Ergüzen
- Each member will be responsible for creating code snippets for their assigned principle.
- Research of prompt engineering will be a collaborative effort. 
