package org.refactoraptor.backend.filtering;

public interface IFilteringService {
    void registerKey(String key, Boolean value);
    void unregisterKey(String key);

    Boolean filter(String key);
}
