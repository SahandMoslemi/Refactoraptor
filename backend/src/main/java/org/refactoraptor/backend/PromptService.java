package org.refactoraptor.backend;

import org.springframework.stereotype.Service;

@Service
public class PromptService {

    public String generatePrompt(PromptEngineeringStrategy strategy, String source) {
        switch (strategy) { // TODO: clear violation of OCP, will fix
            case DEFAULT:
                return generateDefaultPrompt(source);
            default:
                throw new IllegalArgumentException("Unknown strategy: " + strategy);
        }
    }

    private String generateDefaultPrompt(String source) {
        return "Identify the type of SOLID violation (Single Responsibility Principle, Open-Closed Principle, Liskov Substitution Principle, Interface Segregation Principle) in the following code and refactor it to comply with that principle:\n" +
                source;
    }
}
