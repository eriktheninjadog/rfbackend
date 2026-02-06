# LLM Query API Endpoint

The `/llm_query` endpoint provides a generic interface for making LLM API calls through the existing OpenRouter infrastructure.

## Endpoint

```
POST /llm_query
```

## Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model` | string | Yes | - | LLM model identifier (e.g., "claude-3.5-sonnet", "gpt-4", etc.) |
| `prompt` | string | Yes | - | The actual prompt/question to send to the LLM |
| `system_message` | string | No | "" | Optional system message to guide the LLM's behavior |
| `temperature` | number | No | 0.7 | Creativity level (0.0-1.0) |
| `max_tokens` | number | No | 1000 | Maximum response length limit |
| `session_id` | string | No | null | Optional session ID for conversation continuity |
| `clear_history` | boolean | No | false | Whether to start a fresh conversation |
| `response_format` | string | No | "text" | Response format: "text", "json", "structured" |
| `metadata` | object | No | {} | Additional context information |

## Example Requests

### Basic Usage

```bash
curl -X POST http://localhost:5000/llm_query \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3.5-sonnet",
    "prompt": "Explain quantum computing in simple terms"
  }'
```

### With System Message

```bash
curl -X POST http://localhost:5000/llm_query \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3.5-sonnet",
    "prompt": "Translate this to Cantonese: Hello, how are you?",
    "system_message": "You are a helpful assistant that specializes in Traditional Chinese and Cantonese translations",
    "temperature": 0.3,
    "max_tokens": 500
  }'
```

### JSON Response Format

```bash
curl -X POST http://localhost:5000/llm_query \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3.5-sonnet",
    "prompt": "Create a study plan for learning Cantonese. Return as JSON with daily tasks.",
    "response_format": "json",
    "metadata": {
      "use_case": "study_planning",
      "language": "traditional_chinese",
      "user_level": "beginner"
    }
  }'
```

### Session Management

```bash
curl -X POST http://localhost:5000/llm_query \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3.5-sonnet",
    "prompt": "Continue our conversation about Cantonese grammar",
    "session_id": "user-session-123",
    "clear_history": false
  }'
```

## Response Format

```json
{
  "content": "The LLM response content",
  "model": "claude-3.5-sonnet",
  "session_id": "user-session-123",
  "metadata": {
    "use_case": "study_planning",
    "language": "traditional_chinese"
  },
  "usage": {
    "prompt_tokens": 45,
    "completion_tokens": 123,
    "total_tokens": 168
  },
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 1000,
    "response_format": "text"
  }
}
```

## Error Responses

### Missing Required Parameters

```json
{
  "error": "model and prompt are required"
}
```

### API Error

```json
{
  "error": "LLM API request failed: Model not found",
  "model": "invalid-model",
  "session_id": "user-session-123"
}
```

## Available Models

The endpoint supports all models available through OpenRouter. Common models include:

- `anthropic/claude-3.5-sonnet`
- `anthropic/claude-3-opus`
- `openai/gpt-4`
- `openai/gpt-3.5-turbo`
- `meta-llama/llama-3.1-70b-instruct`
- `google/gemini-pro`
- And many more...

## Session Management (Placeholder)

Session management is partially implemented but needs additional storage backend:

- Sessions are identified by `session_id`
- Use `clear_history: true` to start fresh conversations
- Conversation history storage is currently a placeholder and needs implementation

## Integration Notes

- Uses the existing OpenRouter API infrastructure
- Leverages existing logging and error handling
- Maintains compatibility with the current authentication system
- All requests are logged for monitoring and debugging