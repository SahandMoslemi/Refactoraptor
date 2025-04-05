package org.refactoraptor.backend;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;


@RestController
public class Controller {

    private final OllamaService ollamaService;
    private final IPromptEngineeringService promptEngineeringService;

    public Controller(OllamaService ollamaService, IPromptEngineeringService promptEngineeringService) {
        this.ollamaService = ollamaService;
        this.promptEngineeringService = promptEngineeringService;
    }

    @GetMapping("/models")
    public Map<String, Object> getModels() {
        return ollamaService.getModels();
    }

    @GetMapping("/strategies")
    public Map<String, Object> getStrategies() {
        return promptEngineeringService.getStrategies();
    }

    
}
