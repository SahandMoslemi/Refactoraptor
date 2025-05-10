package org.refactoraptor.backend.strategies;

public interface PromptEngineeringStrategy {

    String engineerPrompt(PromptEngineeringStrategy strategy, String source, String language);
}
