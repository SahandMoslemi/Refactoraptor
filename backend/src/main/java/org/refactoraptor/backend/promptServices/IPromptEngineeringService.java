package org.refactoraptor.backend.promptServices;

import org.refactoraptor.backend.strategies.PromptEngineeringStrategy;

import java.util.List;

public interface IPromptEngineeringService
{
    List<String> getStrategies();

    PromptEngineeringStrategy getStrategy(String strategy);
}