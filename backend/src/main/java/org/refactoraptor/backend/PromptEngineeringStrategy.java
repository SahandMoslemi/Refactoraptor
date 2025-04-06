package org.refactoraptor.backend;

// TODO: turn into a strategy pattern
public enum PromptEngineeringStrategy {
    DEFAULT("default");

    private final String name;

    PromptEngineeringStrategy(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }
}
