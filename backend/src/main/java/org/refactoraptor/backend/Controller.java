package org.refactoraptor.backend;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.xml.transform.Source;
import java.util.Map;


@RestController
public class Controller {

    private final OllamaService ollamaService;
    private final IPromptEngineeringService promptEngineeringService;

    public Controller(OllamaService ollamaService, IPromptEngineeringService promptEngineeringService) {
        this.ollamaService = ollamaService;
        this.promptEngineeringService = promptEngineeringService;
    }
    @CrossOrigin(origins = "http://localhost:3000")
    @GetMapping("/models")
    public Map<String, Object> getModels() {
        return ollamaService.getModels();
    }

    @CrossOrigin(origins = "http://localhost:3000")
    @GetMapping("/strategies")
    public Map<String, Object> getStrategies() {
        return promptEngineeringService.getStrategies();
    }

    @CrossOrigin(origins = "http://localhost:3000")
    @PostMapping("/refactor")
    public Map<String, Object> refactor(
            @RequestBody Map<String, String> params) {
        return ollamaService.refactor(params.get("model"),
                PromptEngineeringStrategy.valueOf(params.get("strategy")),
                params.get("source"));
    }
}
