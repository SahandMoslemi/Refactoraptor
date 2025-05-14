package org.refactoraptor.backend.strategies;

public class KnownViolationPromptEngineeringStrategy implements PromptEngineeringStrategy{

    @Override
    public String engineerPrompt(PromptEngineeringStrategy strategy, String source, String language) {
        return "Refactor the following " + language + " code that has a SOLID violation. " +
                "The type of violation will be given to you at the end of the prompt. " +
                "**Important:** Your output must follow *exactly* this format, with no additional commentary before or after.\n\n" +
                "**<VIOLATION TYPE>**\n" +
                "```" + language.toLowerCase() + "\n" +
                "<Refactored code>\n" +
                "```\n" +
                "<Explanation of the refactoring>\n\n" +
                "Only output the text above. Do not include extra analysis or preamble.\n\n" +
                source;
    }
}
