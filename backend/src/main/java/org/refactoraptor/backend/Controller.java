package org.refactoraptor.backend;

import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;


@RestController
public class Controller {

    private final OllamaService ollamaService;
    private final IPromptEngineeringService promptEngineeringService;

    private final OpenaiService openaiService;

    public Controller(OllamaService ollamaService, OpenaiService openaiService, IPromptEngineeringService promptEngineeringService) {
        this.ollamaService = ollamaService;
        this.openaiService = openaiService;
        this.promptEngineeringService = promptEngineeringService;
    }
    @CrossOrigin(origins = "http://localhost:3000")
    @GetMapping("/models")
    public Map<String, Object> getModels() throws IOException {
        return ollamaService.getModels();
    }

    @GetMapping("/models-online")
    public Map<String, Object> getOnlineModels() throws IOException {
        return openaiService.getModels();
    }
  
    @CrossOrigin(origins = "http://localhost:3000")
    @GetMapping("/strategies")
    public List<String> getStrategies() {
        return promptEngineeringService.getStrategies();
    }

    @CrossOrigin(origins = "http://localhost:3000")
    @PostMapping("/refactor")
    public Map<String, Object> refactor(
            @RequestBody Map<String, String> params) {
        return ollamaService.refactor(params.get("model"),
                params.get("strategy"),
                Double.parseDouble(params.get("temperature")),
                params.get("source"),
                Integer.parseInt(params.getOrDefault("try_count", "1")));
    }

    @PostMapping("/refactor-online")
    public Map<String, Object> refactorOnline(
            @RequestBody Map<String, String> params) throws IOException {
        return openaiService.refactor(params.get("model"),
                params.get("strategy"),
                Double.parseDouble(params.get("temperature")),
                params.get("source"));
    }
}
