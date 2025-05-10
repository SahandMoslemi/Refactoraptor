package org.refactoraptor.backend.strategies;

public class EnsemblePromptEngineeringStrategy implements PromptEngineeringStrategy {
    @Override
    public String engineerPrompt(PromptEngineeringStrategy strategy, String source, String language) {
        return String.format("""
            Analyze the following %s code for SOLID principle violations:
            
            ```%s
            %s
            ```
            
            INSTRUCTIONS:
            1. Rate each SOLID principle (0-5 scale)
            2. Select the most impactful violation
            3. GENERATE COMPLETE REFACTORED CODE
            
            SOLID RATINGS:
            - SRP: [score] - [reasoning]
            - OCP: [score] - [reasoning]
            - LSP: [score] - [reasoning]
            - ISP: [score] - [reasoning]
            - DIP: [score] - [reasoning]
            
            MOST IMPACTFUL VIOLATION: [principle]
            
            REFACTORED CODE REQUIREMENT:
            You MUST provide a complete, compilable refactored version of the code.
            The refactored code must be at least as long as the original code.
            Do not use placeholders, comments, or ellipsis (...) to skip parts.
            
            FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
            [SOLID ratings above]
            
            **[VIOLATION TYPE]**
            
            ```%s
            [YOUR COMPLETE REFACTORED CODE GOES HERE]
            [DO NOT SKIP ANY PARTS]
            [MUST BE COMPLETE AND COMPILABLE]
            ```
            
            [Explanation of changes]
            
            REMEMBER: Incomplete code blocks will be considered invalid. You must write every line of the refactored code.
            """,
                language,
                language.toLowerCase(),
                source,
                language.toLowerCase()
        );

    }
}
