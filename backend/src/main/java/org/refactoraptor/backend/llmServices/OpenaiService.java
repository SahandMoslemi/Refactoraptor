package org.refactoraptor.backend.llmServices;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.refactoraptor.backend.StructureService;
import org.refactoraptor.backend.filtering.FilteringService;
import org.refactoraptor.backend.promptServices.PromptService;
import org.refactoraptor.backend.timer.DurationTimer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class OpenaiService {

    @Value("${openai.url}")
    private String openaiUrl;

    @Value("${openai.api.key}")
    private String apiKey;

    private final PromptService promptService;
    private final StructureService structureService;

    private final FilteringService openaiModelFilteringService;

    private final List<String> availableModelKeysForRefactoring = List.of(
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-4.1-mini",
            "gpt-4.1",
            "o4-mini",
            "o3-mini"
    );
    private final ObjectMapper objectMapper = new ObjectMapper(); // JSON serializer

    public OpenaiService(PromptService promptService, StructureService structureService, FilteringService openaiModelFilteringService) {
        this.promptService = promptService;
        this.structureService = structureService;
        this.openaiModelFilteringService = openaiModelFilteringService;
        AddDefaultKeysToFilteringService();
    }

    private void AddDefaultKeysToFilteringService() {
        for (String key : availableModelKeysForRefactoring) {
            openaiModelFilteringService.registerKey(key, true);
        }
    }

    public Map<String, Object> getModels() throws IOException {
        URL url = new URL(openaiUrl + "/v1/models");
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");

        connection.setRequestProperty("Authorization", "Bearer " + apiKey);
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setConnectTimeout(5000);
        connection.setReadTimeout(5000);

        int responseCode = connection.getResponseCode();
        InputStream inputStream = (responseCode >= 200 && responseCode < 300)
                ? connection.getInputStream()
                : connection.getErrorStream();

        try (BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream))) {
            Map<String, Object> rawResponse = objectMapper.readValue(reader, new TypeReference<>() {});
            List<Map<String, Object>> data = (List<Map<String, Object>>) rawResponse.get("data");

            List<Map<String, String>> transformedModels = data.stream()
                    .map(model -> {
                        String id = (String) model.get("id");

                        return Map.of(
                                "name", id,
                                "model", id);
                    })
                    .collect(Collectors.toList());

            for (int i = 0; i < transformedModels.size(); i++) {
                String modelKey = (String) transformedModels.get(i).get("name");
                if (!openaiModelFilteringService.filter(modelKey)) {
                    transformedModels.remove(i);
                    i--;
                }
            }
            return Map.of("models", transformedModels);
        } catch (IOException e) {
            e.printStackTrace(); // Optional: log properly in production
            return Map.of("error", "Failed to parse response");
        } finally {
            connection.disconnect();
        }
    }

    public Map<String, Object> refactor(String model, String strategy, double temperature, String source, String language)
            throws IOException {
        String userPrompt = promptService.generatePrompt(strategy, source, language);

        List<Map<String, String>> messages = new ArrayList<>();

        Map<String, Object> structure = structureService.getStructure();
        messages.add(Map.of(
                "role", "system",
                "content", "Please respond using this JSON structure:\n" + objectMapper.writeValueAsString(structure)
        ));

        messages.add(Map.of(
                "role", "user",
                "content", userPrompt
        ));

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("model", model);
        requestBody.put("temperature", temperature);
        requestBody.put("messages", messages);

        URL url = new URL(openaiUrl + "/v1/chat/completions");
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("POST");
        connection.setDoOutput(true);

        connection.setRequestProperty("Content-Type", "application/json");
        connection.setRequestProperty("Authorization", "Bearer " + apiKey);

        try (OutputStream os = connection.getOutputStream()) {
            objectMapper.writeValue(os, requestBody);
        } catch (IOException e) {
            return Map.of();
        }

        var durationTimer = new DurationTimer();
        durationTimer.start();
        int responseCode = connection.getResponseCode();
        InputStream inputStream = (responseCode >= 200 && responseCode < 300) ?
                connection.getInputStream() : connection.getErrorStream();
        durationTimer.stop();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream))) {
            Map<String, Object> response = objectMapper.readValue(reader, Map.class);
            List<Map<String, Object>> choices = (List<Map<String, Object>>) response.get("choices");
            if (choices != null && !choices.isEmpty()) {
                Map<String, Object> firstChoice = choices.get(0);
                Map<String, Object> message = (Map<String, Object>) firstChoice.get("message");
                String content = (String) message.get("content");
                content = content.replace("*", "");
                ObjectMapper mapper = new ObjectMapper();

                Map<String, Object> userResponse = new HashMap<>();
                try {
                    userResponse = mapper.readValue(content, Map.class);
                }
                catch (Exception e) {
                    userResponse = structureService.parseUnstructuredContent(content);
                }

                userResponse.put("total_duration", durationTimer.getElapsedTimeNanos());
                return userResponse;
            }
            return Map.of();
        }
        catch (IOException e) {
            return Map.of();
        }
    }
}
