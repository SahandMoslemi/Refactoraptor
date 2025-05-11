package org.refactoraptor.backend.filtering;

import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class FilteringService implements IFilteringService {
    private final Map<String, Boolean> filteringKeys;

    public FilteringService() {
        filteringKeys = new HashMap<>();
    }

    public void registerKey(String key, Boolean value) {
        filteringKeys.put(key, value);
    }

    public void unregisterKey(String key) {
        filteringKeys.remove(key);
    }

    public Boolean filter(String key) {
        if (filteringKeys.containsKey(key)) {
            return filteringKeys.get(key);
        }
        else {
            return Boolean.FALSE;
        }
    }

}
