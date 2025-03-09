package org.refactoraptor.backend;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

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
}
