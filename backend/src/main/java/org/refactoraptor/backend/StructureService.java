package org.refactoraptor.backend;

import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class StructureService {

    public Map<String, Object> getStructure(){
        Map<String, Object> properties = Map.of(
                "type", Map.of("type", "string"), // Type of SOLID violation
                "refactored_code", Map.of("type", "string"), // Refactored code
                "explanation", Map.of("type", "string") // Explanation of the refactoring
        );
        List<String> required = List.of("type", "refactored_code", "explanation");
        return Map.of("type", "object", "properties", properties, "required", required);
    }
}
