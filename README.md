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

## Tool Installation

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
python3 -m pip install requests
```

To run:

```bash
python processing_pipeline.py
```

Python pipeline connects to the backend application, so make sure you run it concurrently. 



