package org.refactoraptor.backend.strategies;

public class EnsemblePromptEngineeringStrategy implements PromptEngineeringStrategy {
    @Override
    public String engineerPrompt(PromptEngineeringStrategy strategy, String source) {
        return "Rate this class on a scale from 0 (severe violation) to 5 (perfect compliance) for each SOLID principle:\n\n" +
               "SRP:\n" +
               "OCP:\n" +
               "LSP:\n" +
               "ISP:\n" +
               "DIP:\n\n" +
               "Provide reasoning for each score.\n" +
               "Then, pick the **single most violated** principle and refactor the code to fix it.\n\n" +
               "⚠️ **Important:** Your output must follow *exactly* this format, with no additional commentary before or after.\n\n" +
               "**<VIOLATION TYPE>**\n" +
               "```java\n" +
               "<Refactored code>\n" +
               "```\n" +
               "<Explanation of the refactoring>\n\n" +
               "Only output the text above. Do not include extra analysis or preamble.\n\n" +
               "Example:\n" +
               "**SRP**\n" +
               "```java\n" +
               "public class Example {\n" +
               "    public void exampleMethod() {\n" +
               "        // Example code\n" +
               "    }\n" +
               "}\n" +
               "```\n" +
               "This class violates the Single Responsibility Principle because it has multiple responsibilities.\n\n" +
               source;
    }
}
