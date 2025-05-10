package org.refactoraptor.backend;

import org.refactoraptor.backend.strategies.PromptEngineeringStrategy;
import org.springframework.stereotype.Service;

@Service
public class PromptService {

    private final PromptEngineeringService promptEngineeringService;

    public PromptService(PromptEngineeringService promptEngineeringService) {
        this.promptEngineeringService = promptEngineeringService;
    }

    public String generatePrompt(String strategy, String source, String language) {
        PromptEngineeringStrategy promptEngineeringStrategy = promptEngineeringService.getStrategy(strategy);
        return promptEngineeringStrategy.engineerPrompt(promptEngineeringStrategy, source, language);
    }

    private String generateDefaultPrompt(String source) {
        return "Identify the type of SOLID violation (Single Responsibility Principle, Open-Closed Principle, Liskov Substitution Principle, Interface Segregation Principle) in the following code and refactor it to comply with that principle:\n" +
                source;
    }
}
