package org.refactoraptor.backend;

import org.refactoraptor.backend.strategies.*;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class PromptEngineeringService implements IPromptEngineeringService {

    private static final Map<String, PromptEngineeringStrategy> STRATEGIES = Map.of(
            "DEFAULT", new DefaultPromptEngineeringStrategy(),
            "ENSEMBLE", new EnsemblePromptEngineeringStrategy(),
            "TAGGING", new ExampleBasedPromptEngineeringStrategy(),
            "SMELL", new CodeSmellPromptEngineeringStrategy()
    );

    @Override
    public List<String> getStrategies() {
        return List.copyOf(STRATEGIES.keySet());
    }

    @Override
    public PromptEngineeringStrategy getStrategy(String strategy) {
        return STRATEGIES.getOrDefault(strategy, STRATEGIES.get("DEFAULT"));
    }
}