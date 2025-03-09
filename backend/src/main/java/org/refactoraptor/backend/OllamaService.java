package org.refactoraptor.backend;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service
public class OllamaService {

    @Value("${ollama.url}")
    private String ollamaUrl;

    public Map<String, Object> getModels() {
        RestTemplate restTemplate = new RestTemplate();
        return restTemplate.getForObject(ollamaUrl + "/tags", Map.class);
    }

}
