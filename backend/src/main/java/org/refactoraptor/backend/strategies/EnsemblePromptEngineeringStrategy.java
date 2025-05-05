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
               "Provide reasoning for each score. Pick the most violated, and refactor the following code so as to fix that SOLID violation:\n" +
               source;
    }
}
