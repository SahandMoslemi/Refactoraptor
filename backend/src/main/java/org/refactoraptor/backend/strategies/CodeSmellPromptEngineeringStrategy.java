package org.refactoraptor.backend.strategies;

public class CodeSmellPromptEngineeringStrategy implements PromptEngineeringStrategy {
    @Override
    public String engineerPrompt(PromptEngineeringStrategy strategy, String source, String language) {
        return "First, identify any code smells (e.g., God Object, Interface Bloat, Inappropriate Intimacy).\n" +
               "Then, map each smell to a relevant SOLID principle.\n" +
               "After that, rate the code from 0 (bad) to 5 (good) on:\n" +
               "SRP, OCP, LSP, ISP, DIP.\n\n" +
               "Then, pick the **single most violated** principle and refactor the code to fix it.\n\n" +
                "If there is no violation, you can return NONE." +
               "**Important:** Your output must follow *exactly* this format, with no additional commentary before or after.\n\n" +
               "**<VIOLATION TYPE>**\n" +
               "```" + language.toLowerCase() + "\n" +
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
