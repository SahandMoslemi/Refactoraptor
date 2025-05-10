package org.refactoraptor.backend;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
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
    private final ObjectMapper objectMapper = new ObjectMapper(); // JSON serializer

    public OpenaiService(PromptService promptService, StructureService structureService) {
        this.promptService = promptService;
        this.structureService = structureService;
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

            List<Map<String, Object>> transformedModels = data.stream()
                    .map(model -> {
                        String id = (String) model.get("id");
                        long created = (model.get("created") instanceof Number) ? ((Number) model.get("created")).longValue() : System.currentTimeMillis() / 1000;

                        return Map.of(
                                "name", id,
                                "model", id,
                                "modified_at", "",
                                "size", 0L, // Placeholder
                                "digest", UUID.randomUUID().toString().replace("-", ""), // Placeholder
                                "details", Map.of(
                                        "parent_model", "",
                                        "format", "gguf",
                                        "family", guessFamily(id),
                                        "families", List.of(guessFamily(id)),
                                        "parameter_size", guessSize(id),
                                        "quantization_level", "Q4_0"
                                )
                        );
                    })
                    .collect(Collectors.toList());

            return Map.of("models", transformedModels);
        } catch (IOException e) {
            e.printStackTrace(); // Optional: log properly in production
            return Map.of("error", "Failed to parse response");
        } finally {
            connection.disconnect();
        }
    }

    // Helper methods to "guess" metadata
    private String guessFamily(String id) {
        if (id.contains("llama")) return "llama";
        if (id.contains("qwen")) return "qwen2";
        if (id.contains("dall-e")) return "dalle";
        if (id.contains("gpt")) return "gpt";
        return "unknown";
    }

    private String guessSize(String id) {
        if (id.contains("7b")) return "7.3B";
        if (id.contains("12b")) return "12.2B";
        return "unknown";
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

        int responseCode = connection.getResponseCode();
        InputStream inputStream = (responseCode >= 200 && responseCode < 300) ?
                connection.getInputStream() : connection.getErrorStream();

        try (BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream))) {
            Map<String, Object> response = objectMapper.readValue(reader, Map.class);
            List<Map<String, Object>> choices = (List<Map<String, Object>>) response.get("choices");
            if (choices != null && !choices.isEmpty()) {
                Map<String, Object> firstChoice = choices.get(0);
                Map<String, Object> message = (Map<String, Object>) firstChoice.get("message");
                String content = (String) message.get("content");
                content = content.replace("*", "");
                ObjectMapper mapper = new ObjectMapper();
                try {
                    return mapper.readValue(content, Map.class);
                }
                catch (Exception e) {
                    return structureService.parseUnstructuredContent(content);
                }
            }
            return Map.of();
        }
        catch (IOException e) {
            return Map.of();
        }
    }
}
