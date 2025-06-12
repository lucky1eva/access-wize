## API Interface Draft

### 1. Generate Search Strategy Prompt

**Endpoint:** `/api/generate_prompt`
**Method:** `POST`
**Description:** Generates the prompt for the AI model based on the user's keyword.

**Request Body:**
```json
{
  "keyword": "string"  // User-provided keyword, e.g., "insomnia"
}
```

**Response Body (Success - 200 OK):**
```json
{
  "prompt": "string" // The generated prompt for the AI model
}
```

### 2. Get AI Generated Search Strategy

**Endpoint:** `/api/get_ai_strategy`
**Method:** `POST`
**Description:** Sends the generated prompt to the AI model and retrieves the search strategy in JSON format.

**Request Body:**
```json
{
  "prompt": "string" // The prompt generated from the previous step
}
```

**Response Body (Success - 200 OK):**
```json
{
  "ai_response": { // AI generated JSON response
    "search_strategy": "string",
    "explanation": "string",
    "keywords_analysis": {
      "disease": "string",
      "intervention": "string",
      "population": "string",
      "study_type": "string"
    },
    "estimated_results": "string",
    "mesh_terms": ["string"],
    "search_tips": "string"
  }
}
```

### 3. Execute PubMed Search and Get Results

**Endpoint:** `/api/execute_pubmed_search`
**Method:** `POST`
**Description:** Executes the PubMed search using the AI-generated search strategy and returns the results.

**Request Body:**
```json
{
  "search_strategy": "string" // The search strategy from AI response
}
```

**Response Body (Success - 200 OK):**
```json
{
  "pubmed_results_csv": "string" // Base64 encoded CSV content of PubMed results
}
```

