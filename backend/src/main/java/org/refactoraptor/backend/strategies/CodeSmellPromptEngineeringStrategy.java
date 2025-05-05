package org.refactoraptor.backend.strategies;

public class CodeSmellPromptEngineeringStrategy implements PromptEngineeringStrategy {
    @Override
    public String engineerPrompt(PromptEngineeringStrategy strategy, String source) {
        return "You are a code quality assistant trained to detect design problems in object-oriented code.\n\n" +
               "Your task has two steps:\n\n" +
               "---\n\n" +
               "**Step 1: Identify any code smells present in the following code.**\n" +
               "Use common smells like:\n" +
               "- God Object (does too many things)\n" +
               "- Feature Envy (method accesses other class's data)\n" +
               "- Shotgun Surgery (small changes affect many places)\n" +
               "- Concrete Dependency (relies on specific implementations)\n" +
               "- Large Interface (methods unused by client classes)\n" +
               "- Others you may observe\n" +
               "List each smell with a one-sentence description.\n\n" +
               "**Step 2: For each code smell, identify which SOLID principle it may violate.**\n" +
               "List the principle (SRP, OCP, LSP, ISP, DIP), explain why it applies, and refactor the following code so to fix the most violated SOLID principle.\n\n" +
               source;
    }
}
