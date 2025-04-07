package org.refactoraptor.backend;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service
public class PromptEngineeringService implements IPromptEngineeringService {

    @Override
    public Map<String, Object> getStrategies() {
        return Map.of();
    }
}