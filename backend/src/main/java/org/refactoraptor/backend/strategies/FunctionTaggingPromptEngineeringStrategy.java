package org.refactoraptor.backend.strategies;

public class FunctionTaggingPromptEngineeringStrategy implements PromptEngineeringStrategy {

    @Override
    public String engineerPrompt(PromptEngineeringStrategy strategy, String source) {
        return "You are a software design assistant.\n\n" +
               "Your task is to:\n" +
               "1. Summarize the responsibility of each method in the code below.\n" +
               "2. Identify whether any methods or the class as a whole violate any SOLID principles.\n" +
               "3. Specify which principles are violated, and explain why.\n" +
               "4. Suggest improvements or a refactored version if a violation is detected.\n\n" +
               source;
    }
}
