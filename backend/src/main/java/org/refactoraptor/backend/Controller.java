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

    @GetMapping("/models")
    public Map<String, Object> getModels() {
        return ollamaService.getModels();
    }

    @GetMapping("/strategies")
    public Map<String, Object> getStrategies() {
        return promptEngineeringService.getStrategies();
    }

    @PostMapping("/source/{session_id}/{strategy}")
    public ResponseEntity postSource(
            @RequestBody SourceModel sourceModel,
            @PathVariable("session_id") Long sessionId,
            @PathVariable("strategy") String strategy) {
        sourceModel.getFiles().forEach(file ->
                System.out.println("Received file: " + file.getFileName())
        );
        return ResponseEntity.ok("Received " + sourceModel.getFiles().size() + " files for user " + sessionId);
    }
}
