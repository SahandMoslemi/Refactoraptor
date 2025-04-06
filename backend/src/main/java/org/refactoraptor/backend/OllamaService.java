package org.refactoraptor.backend;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
public class OllamaService {

    @Value("${ollama.url}")
    private String ollamaUrl;

    private PromptService promptService;

    private StructureService structureService;

    public OllamaService(PromptService promptService, StructureService structureService) {
        this.promptService = promptService;
        this.structureService = structureService;
    }

    public Map<String, Object> getModels() {
        RestTemplate restTemplate = new RestTemplate();
        return restTemplate.getForObject(ollamaUrl + "/tags", Map.class);
    }

    public Map<String, Object> refactor(String model, PromptEngineeringStrategy strategy, String source) {
        RestTemplate restTemplate = new RestTemplate();

        // Construct the request body
        Map<String, Object> requestBody = new HashMap<>();

        requestBody.put("model", model);
        requestBody.put("stream", false);

        String prompt = promptService.generatePrompt(strategy, source);
        requestBody.put("prompt", prompt);

        Map<String, Object> structure = structureService.getStructure();
        requestBody.put("format", structure);

        Map<String, Object> response = restTemplate.postForObject(ollamaUrl + "/generate", requestBody, Map.class);
        return response;
    }

}
