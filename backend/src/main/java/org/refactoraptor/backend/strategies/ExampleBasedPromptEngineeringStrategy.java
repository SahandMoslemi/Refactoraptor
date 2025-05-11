package org.refactoraptor.backend.strategies;

public class ExampleBasedPromptEngineeringStrategy implements PromptEngineeringStrategy {

    @Override
    public String engineerPrompt(PromptEngineeringStrategy strategy, String source, String language) {
        return "You are an expert in identifying and refactoring SOLID principle violations in " + language + " code. Your task is to analyze the code provided and respond in the exact format below, without any additional text or commentary.\n\n" +
                "You must provide the following three parts in your response:\n" +
                "1. The violated SOLID principle (e.g., SRP, OCP, LSP, ISP, DIP). If no violation exists, respond with **NONE**.\n" +
                "2. A complete refactored version of the code that removes the violation. YOU MUST RETURN ONLY THE CODE BLOCK.\n" +
                "3. A brief explanation of the violation and the refactoring.\n\n" +
                "Use these criteria to detect violations:\n" +
                "- **SRP**: A class does too many unrelated tasks.\n" +
                "- **OCP**: Multiple `if-else` or `switch` blocks for logic that should be handled by polymorphism.\n" +
                "- **LSP**: Subclasses override behavior in a way that breaks the contract of the base class (e.g., throw exceptions).\n" +
                "- **ISP**: Interfaces that are too large or force implementing unnecessary methods.\n" +
                "- **DIP**: High-level classes directly depend on low-level classes instead of abstractions.\n\n" +
                "If more than one violation is present, report only the most prominent one.\n\n" +
                "**IMPORTANT:** Follow this output format *exactly*. Do not include greetings, summaries, or comments before or after the output:\n\n" +
                "**<VIOLATION TYPE>**\n" +
                "```" + language.toLowerCase() + "\n" +
                "<Refactored code>\n" +
                "```\n" +
                "<Explanation of the refactoring>\n\n" +
                "Example output:\n" +
                "**SRP**\n" +
                "```java\n" +
                "public class ReportGenerator {\n" +
                "    public String generateReport() {\n" +
                "        return \"Report data\";\n" +
                "    }\n" +
                "}\n" +
                "```\n" +
                "The class previously handled both data generation and file I/O. Now it only generates the report, following SRP.\n\n" +
                "Here is the code:\n" +
                source;
    }
}
