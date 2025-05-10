package org.refactoraptor.backend;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

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

    public Map<String, Object> refactor(String model, String strategy, double temperature, String source, int tryCount, String language) {
        RestTemplate restTemplate = new RestTemplate();

        // Construct the request body
        Map<String, Object> requestBody = new HashMap<>();

        requestBody.put("model", model);
        requestBody.put("stream", false);

        String prompt = promptService.generatePrompt(strategy, source, language);
        requestBody.put("prompt", prompt);

//        Map<String, Object> structure = structureService.getStructure();
//        requestBody.put("format", structure);

        Map<String, Object> options = new HashMap<>();
        options.put("temperature", temperature);
        requestBody.put("options", options);
        for (int i = 0; i < tryCount; i++) {
            Map<String, Object> response = restTemplate.postForObject(ollamaUrl + "/generate", requestBody, Map.class);
            ParsedOutput po = parse(response.get("response").toString());
            Map<String, Object> parsedResponse = new HashMap<>();
            parsedResponse.put("violation_type", po.violationType);
            parsedResponse.put("refactored_code", po.refactoredCode);
            parsedResponse.put("explanation", po.explanation);
            System.out.println(parse(response.get("response").toString()));
            if (po.isValid() || i == tryCount - 1) {
                return parsedResponse;
            }
        }
        return null;
    }

    public static class ParsedOutput {
        public String violationType;
        public String refactoredCode;
        public String explanation;

        @Override
        public String toString() {
            return "Violation: " + violationType + "\n\n" +
                   "Code:\n" + refactoredCode + "\n\n" +
                   "Explanation:\n" + explanation;
        }

        public boolean isValid() {
            return violationType != null && refactoredCode != null && explanation != null;
        }
    }

    public static ParsedOutput parse(String input) {
        ParsedOutput result = new ParsedOutput();

        // Extract violation type from the first **<TYPE (Explanation)>**
        Matcher violationMatcher = Pattern.compile("\\*\\*(\\w+)\\*\\*").matcher(input);
        if (violationMatcher.find()) {
            result.violationType = violationMatcher.group(1);
        }

        // Extract refactored code between ```java ... ```
        Matcher codeMatcher = Pattern.compile("```java\\s*(.*?)\\s*```", Pattern.DOTALL).matcher(input);
        if (codeMatcher.find()) {
            result.refactoredCode = codeMatcher.group(1);
        }

        // Extract explanation (text after the code block and before next **)
        Matcher explanationMatcher = Pattern.compile("```java.*?```\\s*(.*?)\\n\\*\\*", Pattern.DOTALL).matcher(input);
        if (explanationMatcher.find()) {
            result.explanation = explanationMatcher.group(1).trim();
        }

        return result;
    }

}
