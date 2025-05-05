package org.refactoraptor.backend;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.*;

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

        int responseCode = connection.getResponseCode();
        InputStream inputStream = (responseCode >= 200 && responseCode < 300)
                ? connection.getInputStream()
                : connection.getErrorStream();

        try (BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream))) {
            return objectMapper.readValue(reader, Map.class);
        } catch (IOException e) {
            return Map.of();
        }
    }

    public Map<String, Object> refactor(String model, PromptEngineeringStrategy strategy, double temperature, String source)
            throws IOException {
        String userPrompt = promptService.generatePrompt(strategy, source);

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
            return response;
        }
        catch (IOException e) {
            return Map.of();
        }
    }
}
