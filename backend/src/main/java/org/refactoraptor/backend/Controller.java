package org.refactoraptor.backend;

import org.springframework.web.bind.annotation.*;

import java.util.Map;


@RestController
public class Controller {

    private final OllamaService ollamaService;

    public Controller(OllamaService ollamaService) {
        this.ollamaService = ollamaService;
    }

    @GetMapping("/models")
    public Map<String, Object> getModels() {
        return ollamaService.getModels();
    }

    @PostMapping("/refactor")
    public Map<String, Object> refactor(
            @RequestBody Map<String, String> params) {
        return ollamaService.refactor(params.get("model"),
                PromptEngineeringStrategy.valueOf(params.get("strategy")),
                params.get("source"));
    }
}
