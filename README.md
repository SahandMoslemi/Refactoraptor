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

## Introduced Dataset

We have prepared multiple examples for each SOLI violation. Spefically, our dataset includes examples across difficulty levels (`EASY`, `MODERATE` and `HARD`) and programming languages (`Java`, `Python`, `Kotlin` and `C#`). For instance, for SRP, we have 48 examples (4 examples * 3 difficulties * 4 programming languages). In total, we have 192 examples.

## Installation

### Frontend

Inside `frontend` directory, run the following commands: 

```bash
npm install
npm run dev
```

### Backend

Change to `backend` directory.

```bash
cd backend/
```

Build the project using Maven: This will compile the code, run tests, and package the application into a JAR file.  

```bash
mvn clean package
```
Run the Spring Boot application: After the build is successful, you can run the generated JAR file (usually located in the target directory).  

```bash
java -jar target/BackendApplication.jar
```
Access the application: By default, Spring Boot applications run on http://localhost:8080. You can access the endpoints defined in your Controller class.

To use OpenAI, you have to set a valid api key in the resources. Change the `api.key` field to the actual api key inside `backend/src/main/resources/application.yml". 
After restart, you can use the OpenAI controller endpoints in Refactoraptor backend.

### Python Pipeline

A python script can be used to generate output using different prompt strategies. Change into `dataset` directory. 

```bash
cd dataset/
```

You can change which models and strategies to test by editing the macros in the top of Python script. Install the dependencies via: 
```bash
python3 -m pip install tqdm
```

To run:

```bash
python processing_pipeline.py
```

Python pipeline connects to the backend application, so make sure you run it concurrently. 
