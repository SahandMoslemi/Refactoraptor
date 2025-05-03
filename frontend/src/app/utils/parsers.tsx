/**
 * Parses and normalizes potentially malformed refactoring result JSON
 * @param jsonString - The JSON string to parse
 * @returns A normalized RefactoredData object
 */
export function parseRefactoringResult(jsonString: string): RefactoredData {
  try {
    // Try to parse the JSON directly first
    const parsedData = JSON.parse(jsonString);
    return normalizeRefactoredData(parsedData);
  } catch (error) {
    // If direct parsing fails, try to fix common issues
    console.warn("Initial JSON parsing failed, attempting recovery:", error);

    // Try to fix the malformed JSON
    const fixedJsonString = fixMalformedJson(jsonString);

    try {
      const parsedData = JSON.parse(fixedJsonString);
      return normalizeRefactoredData(parsedData);
    } catch (secondError) {
      console.error("JSON recovery failed:", secondError);

      // Fall back to a basic extraction approach
      return extractDataFromMalformedJson(jsonString);
    }
  }
}

/**
 * Attempts to fix common JSON formatting issues
 */
function fixMalformedJson(jsonString: string): string {
  let result = jsonString;

  // Fix truncated strings by adding missing quotes and braces
  if (result.indexOf('":{') > -1 && !result.endsWith("}")) {
    result += '"}';
  }

  if (!result.endsWith("}")) {
    result += "}";
  }

  // Fix escaped quotes within strings
  result = result.replace(/\\"/g, '"');

  // Fix missing commas between properties
  result = result.replace(/"\s+"/g, '", "');

  return result;
}

/**
 * Extracts data from malformed JSON using regex patterns
 */
function extractDataFromMalformedJson(jsonString: string): RefactoredData {
  // Default values
  const defaultData: RefactoredData = {
    originalCode: "",
    refactoredCode: "",
    codeChanges: [],
    explanation: "",
    executionTime: "0s",
    modelUsed: "Unknown model",
    originalFileName: "code.txt",
    language: "text",
  };

  // Extract explanation
  const explanationMatch = jsonString.match(/"explanation":"([^"]+)"/);
  if (explanationMatch && explanationMatch[1]) {
    defaultData.explanation = cleanupString(explanationMatch[1]);
  }

  // Extract refactored code
  const codeMatch = jsonString.match(/"refactored_code":"([^"]+)"/);
  if (codeMatch && codeMatch[1]) {
    defaultData.refactoredCode = cleanupString(codeMatch[1]);
  }

  // Try to extract language type
  const typeMatch = jsonString.match(/"type":"([^"]+)"/);
  if (typeMatch && typeMatch[1]) {
    defaultData.language = cleanupString(typeMatch[1]);
  }

  // Generate code changes from explanation if possible
  defaultData.codeChanges = generateCodeChangesFromExplanation(
    defaultData.explanation
  );

  return defaultData;
}

/**
 * Cleans up a string by unescaping newlines and other common escape sequences
 */
function cleanupString(str: string): string {
  return str
    .replace(/\\n/g, "\n")
    .replace(/\\t/g, "\t")
    .replace(/\\r/g, "\r")
    .replace(/\\\\/g, "\\")
    .replace(/\\"/g, '"');
}

/**
 * Generates code changes based on the explanation text
 */
function generateCodeChangesFromExplanation(
  explanation: string
): Array<{ lineNumber: number; explanation: string }> {
  const changes: Array<{ lineNumber: number; explanation: string }> = [];
  const lines = explanation.split("\n");

  // Look for numbered items or things that look like line references
  let currentLineNumber = 1;

  lines.forEach((line) => {
    // Try to extract line numbers
    const lineNumberMatch = line.match(/(\d+)\.\s+\*\*([^:]+)\*\*:\s+(.*)/);
    if (lineNumberMatch) {
      changes.push({
        lineNumber: currentLineNumber++,
        explanation: `${lineNumberMatch[2]}: ${lineNumberMatch[3]}`,
      });
      return;
    }

    // Look for bullet points
    if (line.trim().startsWith("- ") || line.trim().startsWith("* ")) {
      const explanationText = line.trim().substring(2);
      if (explanationText.length > 10) {
        // Only add substantial explanations
        changes.push({
          lineNumber: currentLineNumber++,
          explanation: explanationText,
        });
      }
    }
  });

  // If we couldn't find any changes, make a generic one
  if (changes.length === 0 && explanation.length > 0) {
    changes.push({
      lineNumber: 1,
      explanation:
        "Code was refactored to follow better practices. See the explanation for details.",
    });
  }

  return changes;
}

/**
 * Normalizes the parsed data to ensure it conforms to the expected structure
 */
function normalizeRefactoredData(data: any): RefactoredData {
  // Create a base object with defaults
  const normalized: RefactoredData = {
    originalCode: data.originalCode || data.original_code || "",
    refactoredCode: data.refactoredCode || data.refactored_code || "",
    codeChanges: data.codeChanges || data.code_changes || [],
    explanation: data.explanation || "",
    executionTime: data.executionTime || data.execution_time || "0s",
    modelUsed: data.modelUsed || data.model_used || "Unknown model",
    originalFileName:
      data.originalFileName || data.original_file_name || "code.txt",
    language: data.language || data.type || "text",
  };

  // Convert codeChanges to proper format if necessary
  if (
    !Array.isArray(normalized.codeChanges) ||
    normalized.codeChanges.length === 0
  ) {
    normalized.codeChanges = generateCodeChangesFromExplanation(
      normalized.explanation
    );
  }

  // Ensure each code change has the required properties
  normalized.codeChanges = normalized.codeChanges.map((change, index) => {
    return {
      lineNumber: change.lineNumber || change.lineNumber || index + 1,
      explanation: change.explanation || "Code improvement",
    };
  });

  return normalized;
}

// Type definition for RefactoredData
export interface RefactoredData {
  originalCode: string;
  refactoredCode: string;
  codeChanges: Array<{ lineNumber: number; explanation: string }>;
  explanation: string;
  executionTime: string;
  modelUsed: string;
  originalFileName: string;
  language: string;
}
