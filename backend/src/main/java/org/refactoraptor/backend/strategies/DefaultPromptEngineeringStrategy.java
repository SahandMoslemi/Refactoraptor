package org.refactoraptor.backend.strategies;

public class DefaultPromptEngineeringStrategy implements PromptEngineeringStrategy {
    @Override
    public String engineerPrompt(PromptEngineeringStrategy strategy, String source, String language) {
        return "Identify the type of SOLID violation (Single Responsibility Principle, Open-Closed Principle, Liskov Substitution Principle, Interface Segregation Principle) in the following code and refactor it to comply with that principle" +
                "If you cannot find a violation, return NONE:\n" +
                source;
    }
}
