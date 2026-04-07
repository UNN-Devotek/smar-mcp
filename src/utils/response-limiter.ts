/**
 * Utility to limit response sizes and prevent "Tool result is too large" errors
 */

const MAX_RESPONSE_LENGTH = 100000; // ~100KB of text

export interface LimitedResponse {
  [x: string]: unknown;
  content: Array<{
    [x: string]: unknown;
    type: "text";
    text: string;
  }>;
  isError?: boolean;
}

/**
 * Limits the size of a response by truncating if necessary
 * @param data The data to return
 * @param truncateArrays If true, truncates arrays to a reasonable size
 * @returns Limited response object
 */
export function limitResponseSize(data: any, truncateArrays: boolean = true): LimitedResponse {
  let jsonString = JSON.stringify(data, null, 2);

  // If the response is within limits, return as-is
  if (jsonString.length <= MAX_RESPONSE_LENGTH) {
    return {
      content: [
        {
          type: "text" as const,
          text: jsonString
        }
      ]
    };
  }

  // Response is too large, need to truncate
  console.error(`Response size ${jsonString.length} exceeds limit ${MAX_RESPONSE_LENGTH}, truncating...`);

  // Try to intelligently truncate arrays first
  if (truncateArrays) {
    const truncated = truncateArraysInObject(data);
    jsonString = JSON.stringify(truncated, null, 2);

    if (jsonString.length <= MAX_RESPONSE_LENGTH) {
      return {
        content: [
          {
            type: "text" as const,
            text: `⚠️ Response was truncated to fit size limits.\n\n${jsonString}`
          }
        ]
      };
    }
  }

  // Still too large, do hard truncation
  const truncatedText = jsonString.substring(0, MAX_RESPONSE_LENGTH);
  const truncatedInfo = `\n\n... [Response truncated: ${jsonString.length - MAX_RESPONSE_LENGTH} characters omitted]`;

  return {
    content: [
      {
        type: "text" as const,
        text: `⚠️ Response exceeded maximum size and was truncated.\n\n${truncatedText}${truncatedInfo}`
      }
    ]
  };
}

/**
 * Truncates arrays in an object to reduce size
 */
function truncateArraysInObject(obj: any, maxArrayLength: number = 10): any {
  if (Array.isArray(obj)) {
    if (obj.length > maxArrayLength) {
      const truncated = obj.slice(0, maxArrayLength);
      return [
        ...truncated,
        {
          _truncated: true,
          _message: `Array truncated: showing ${maxArrayLength} of ${obj.length} items`,
          _totalItems: obj.length
        }
      ];
    }
    return obj.map(item => truncateArraysInObject(item, maxArrayLength));
  }

  if (obj !== null && typeof obj === 'object') {
    const result: any = {};
    for (const [key, value] of Object.entries(obj)) {
      result[key] = truncateArraysInObject(value, maxArrayLength);
    }
    return result;
  }

  return obj;
}

/**
 * Creates a summary of large data instead of returning all details
 */
export function createSummaryResponse(data: any, summaryFields: string[] = []): LimitedResponse {
  const summary: any = {
    _summary: true,
    _message: "Full data was too large. Showing summary only."
  };

  // Extract summary fields
  summaryFields.forEach(field => {
    if (data[field] !== undefined) {
      summary[field] = data[field];
    }
  });

  // Add counts for arrays
  for (const [key, value] of Object.entries(data)) {
    if (Array.isArray(value)) {
      summary[`${key}_count`] = value.length;
    }
  }

  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify(summary, null, 2)
      }
    ]
  };
}
