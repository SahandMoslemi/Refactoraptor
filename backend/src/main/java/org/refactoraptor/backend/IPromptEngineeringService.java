package org.refactoraptor.backend;

import org.springframework.web.client.RestTemplate;

import java.util.Map;

public interface IPromptEngineeringService
{
    public Map<String, Object> getStrategies();
}