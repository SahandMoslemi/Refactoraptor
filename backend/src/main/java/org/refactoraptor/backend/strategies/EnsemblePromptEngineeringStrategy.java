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
               "Then, compare the severity of each violation and pick the **single most impactful** one in terms of maintainability. Refactor the code to address that principle.\n\n" +
               "If multiple principles are equally violated, pick one arbitrarily, but do not always default to SRP.\n\n" +
               "⚠️ **Important:** Your output must follow *exactly* this format, with no additional commentary before or after.\n\n" +
               "**<VIOLATION TYPE>**\n" +
               "```java\n" +
               "<Refactored code>\n" +
               "```\n" +
               "<Explanation of the refactoring>\n\n" +
               source;
    }
}
