# Aurora-X English Mode Documentation

## Overview

Aurora-X English Mode enables natural language code synthesis, allowing users to describe what they want in plain English rather than writing formal specifications. The system automatically converts English requests into V3 specs and synthesizes working code, using a generic fallback template when no specific pattern matches.

## Key Features

### 1. **Plain English Input**
- Accept natural language descriptions
- No need for formal specification syntax
- Automatic inference of function signatures and types

### 2. **Zero Dead-Ends**
- Always generates something useful
- Generic fallback for unrecognized patterns
- Returns working placeholder functions instead of errors

### 3. **API Integration**
- RESTful endpoints for programmatic access
- Optional approval workflow for synthesis runs
- Real-time synthesis feedback

## Components

### English-to-Spec Converter (`tools/english_to_spec.py`)

Converts plain English text into V3 specification files:

```bash
python tools/english_to_spec.py "reverse a string"
```

Features:
- Automatic function name generation
- Type inference from context
- Sanitized file naming
- Template markers for classification

### Generic Fallback Template (`aurora_x/synthesis/fallback.py`)

Provides working placeholder functions when no template matches:

```python
from aurora_x.synthesis.fallback import generate_fallback_function

code = generate_fallback_function(
    "def unknown_func(x: int) -> str",
    "Some unrecognized function"
)
```

Features:
- Automatic return type detection
- Sensible default values
- Self-documenting placeholders
- Type-appropriate returns

### API Endpoints (`aurora_x/serve_addons.py`)

#### POST `/api/chat`
Generate spec from English prompt:

```bash
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "find the largest number in a list", "auto_synthesize": true}'
```

Response:
```json
{
  "ok": true,
  "spec": "specs/requests/find_the_largest_number_in_a_list_a3f2d1.md",
  "function_name": "find_the_largest_number_in_a_list_a3f2d1",
  "message": "Spec generated successfully",
  "synthesis_started": true
}
```

#### GET `/api/approve`
List pending synthesis runs:

```bash
curl http://localhost:5001/api/approve
```

#### POST `/api/approve`
Approve or reject a synthesis run:

```bash
curl -X POST http://localhost:5001/api/approve \
  -H "Content-Type: application/json" \
  -d '{"token": "abc123", "approved": true}'
```

#### GET `/api/english/status`
Check English mode status:

```bash
curl http://localhost:5001/api/english/status
```

## Usage

### Command Line Interface

#### Interactive Chat Mode
```bash
make chat
# Enter: find all prime numbers in a list
```

#### Direct Command
```bash
make chat PROMPT="reverse a string"
```

#### API-Based Chat (requires server)
```bash
make serve-v3  # In one terminal
make chat-api  # In another terminal
```

### Python API

```python
from tools.english_to_spec import generate_v3_spec, sanitize_name

# Generate spec from English
spec_content = generate_v3_spec("reverse a string")

# Save to file
filename = f"specs/requests/{sanitize_name('reverse a string')}.md"
with open(filename, 'w') as f:
    f.write(spec_content)
```

### Programmatic Usage

```python
import requests

# Send English prompt
response = requests.post(
    "http://localhost:5001/api/chat",
    json={
        "prompt": "calculate factorial of a number",
        "auto_synthesize": True
    }
)

result = response.json()
print(f"Generated spec: {result['spec']}")
print(f"Function name: {result['function_name']}")
```

## Examples

### Example 1: Recognized Pattern
```bash
$ python tools/english_to_spec.py "reverse a string"
✅ Spec generated: specs/requests/reverse_a_string_f4a2c1.md
📝 Function name: reverse_a_string_f4a2c1
```

The system recognizes "reverse" and "string", generating appropriate code.

### Example 2: Unrecognized Pattern (Uses Fallback)
```bash
$ python tools/english_to_spec.py "perform quantum calculations"
✅ Spec generated: specs/requests/perform_quantum_calculations_d3e5a7.md
📝 Function name: perform_quantum_calculations_d3e5a7
```

The system doesn't recognize the pattern, so it generates a generic placeholder function that returns appropriate default values.

### Example 3: Complex Request
```bash
$ make chat
🗣️ Aurora-X Interactive English Mode
Enter your request in plain English:
> find all palindromes in a list and return their count
📝 Generating spec from: find all palindromes in a list and return their count
✅ Spec created: specs/requests/find_all_palindromes_in_a_list_9b3c2f.md
🔧 Compiling to code...
📊 Code generated in: runs/run-20251011-120000
```

## Testing

### Test All Components
```bash
make english-test
```

This runs:
1. English-to-spec converter test
2. Fallback template test
3. Flow_ops integration test
4. API endpoint availability check

### Run Demo
```bash
make english-demo
```

Shows examples of:
- Simple function requests
- Complex function requests
- Unrecognized patterns using fallback

### Check Status
```bash
make english-status
```

Displays:
- Component availability
- Directory structure
- Recent specs generated
- Server endpoint status

## Configuration

### Environment Variables

- `AURORA_PORT`: Server port (default: 5001)
- `PROMPT`: Default prompt for chat commands

### File Locations

- Specs: `specs/requests/`
- Tools: `tools/english_to_spec.py`
- Fallback: `aurora_x/synthesis/fallback.py`
- API: `aurora_x/serve_addons.py`

## Makefile Commands

Include the English mode targets in your Makefile:

```makefile
include Makefile.english.add
```

Or add individual targets:

```makefile
chat:
	@echo "Interactive English Mode"
	@read -r prompt; \
	python tools/english_to_spec.py "$$prompt"

approve:
	@curl -s http://localhost:5001/api/approve | python -m json.tool
```

## Architecture

```
User Input (English)
        ↓
english_to_spec.py
        ↓
Generate V3 Spec
        ↓
Save to specs/requests/
        ↓
flow_ops.py (synthesis)
        ↓
Template Match?
    ├─ Yes → Use specific template
    └─ No → Use generic fallback
        ↓
Generated Code
```

## Troubleshooting

### "Template not recognized" Error
This should no longer occur with English mode enabled. The fallback template ensures all requests generate working code.

### Empty Specs Directory
The `specs/requests/` directory is created automatically when needed.

### Server Not Running
Start the server before using API endpoints:
```bash
make serve-v3
```

### Import Errors
Ensure Aurora-X is installed:
```bash
pip install -e .
```

## Best Practices

1. **Be Specific**: More detailed descriptions generate better function signatures
2. **Use Examples**: Include example inputs/outputs in your description
3. **Review Generated Code**: Always review and test generated placeholders
4. **Iterate**: Refine your English prompt if the first result isn't ideal
5. **Combine with Templates**: Use existing templates when available for better results

## Future Enhancements

Planned improvements:
- Machine learning for better pattern recognition
- Context-aware type inference
- Multi-function synthesis from complex descriptions
- Interactive refinement workflow
- Integration with popular IDEs
- Natural language test generation

## Support

For issues or questions about English mode:
1. Check this documentation
2. Run `make english-test` to verify installation
3. Review generated specs in `specs/requests/`
4. Check server logs for API issues

## Conclusion

Aurora-X English Mode eliminates the barrier between natural language and code synthesis. By accepting plain English and always generating useful output, it makes code generation accessible to everyone while maintaining the power of the Aurora-X synthesis engine.