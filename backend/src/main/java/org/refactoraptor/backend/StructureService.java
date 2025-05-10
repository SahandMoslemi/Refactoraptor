package org.refactoraptor.backend;

import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class StructureService {

    public Map<String, Object> getStructure(){
        Map<String, Object> properties = Map.of(
                "violation_type", Map.of("type", "string"), // Type of SOLID violation
                "refactored_code", Map.of("type", "string"), // Refactored code
                "explanation", Map.of("type", "string") // Explanation of the refactoring
        );
        List<String> required = List.of("violation_type", "refactored_code", "explanation");
        return Map.of("type", "object", "properties", properties, "required", required);
    }

    public Map<String, Object> parseUnstructuredContent(String content) {
        Map<String, Object> result = new HashMap<>();

        // Extract violation
        String violation = extractViolation(content);
        result.put("violation", violation);

        // Extract code block
        String code = extractCode(content);
        result.put("refactoredCode", code);

        // Extract explanation at the end.
        String explanation = extractExplanation(content);
        result.put("explanation", explanation);

        if (explanation.isEmpty()) {
            Map<String, Object> unparsedResponse = Map.of();
            unparsedResponse.put("explanation", content);
            return unparsedResponse;
        }
        return result;
    }

    private String extractViolation(String content) {
        int newline = content.indexOf("\n");
        return (newline > 0) ? content.substring(0, newline).trim() : "Unknown";
    }

    private String extractCode(String content) {
        int start = content.indexOf("```java");
        int end = content.indexOf("```", start + 7);
        if (start != -1 && end != -1) {
            return content.substring(start + 7, end).trim();
        }
        return "";
    }

    private String extractExplanation(String content) {
        int lastBacktick = content.lastIndexOf("```");
        if (lastBacktick != -1 && lastBacktick + 3 < content.length()) {
            return content.substring(lastBacktick + 3).trim();
        }
        return "";
    }
}
