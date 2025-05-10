package org.refactoraptor.backend.strategies;

public class ExampleBasedPromptEngineeringStrategy implements PromptEngineeringStrategy {

    @Override
    public String engineerPrompt(PromptEngineeringStrategy strategy, String source) {
        return "You are going to find SOLID principles violations in the following code. You will provide the following three answers:\n" +
                "1. The SOLID violation, (like ISP, LSP etc.) If there is no violation, give NONE.\n" +
                "2. You will refactor the code so it does not have the violation.\n" +
                "3. You will give a brief explanation of the violation.\n" +
                "You will know ISP violations by long interfaces that can be better written shorter.\n" +
                "You will know LSP violations by derived classes throwing exceptions in base class methods.\n" +
                "You will know OCP violations by lots of if-else and switch statements, especially nested.\n" +
                "You will know SRP violations by a class that tries to do too many things at once. Do not say SRP very quickly, if the others are there, answer with them.\n" +
                "You will know DIP violations by high-level modules depending on low-level modules directly, instead of through abstractions.\n" +
                "You will give only one of the violations if there are multiple. Pick the one that is most prominent.\n" +
                "Here is the code: " +
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
