package org.refactoraptor.backend;

import java.util.List;

public class SourceModel {
    private List<SourceFile> files;

    // Getters and setters
    public List<SourceFile> getFiles() {
        return files;
    }

    public void setFiles(List<SourceFile> files) {
        this.files = files;
    }
}
