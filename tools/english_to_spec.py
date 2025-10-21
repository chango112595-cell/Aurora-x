#!/usr/bin/env python3
"""
English-to-Spec Converter for Aurora-X v3
Converts plain English requests into V3 spec markdown files
"""

import hashlib
import re
import sys
from datetime import datetime
from pathlib import Path


def sanitize_name(text: str) -> str:
    """Convert text to a safe filename"""
    # Remove special characters and convert to lowercase
    safe = re.sub(r'[^a-zA-Z0-9_\s-]', '', text.lower())
    # Replace spaces with underscores
    safe = re.sub(r'\s+', '_', safe.strip())
    # Limit length
    safe = safe[:50]
    # Add a short hash for uniqueness
    hash_suffix = hashlib.md5(text.encode()).hexdigest()[:6]
    return f"{safe}_{hash_suffix}" if safe else f"request_{hash_suffix}"

def infer_function_details(text: str) -> dict:
    """Try to infer function details from English text"""
    text_lower = text.lower()

    # Common patterns
    patterns = {
        'function_with_list': r'(list|array|numbers|items|collection)',
        'function_with_string': r'(string|text|word|sentence|phrase)',
        'function_with_number': r'(number|integer|float|digit|count)',
        'function_returns_bool': r'(check|is|can|should|verify|validate)',
        'function_returns_list': r'(sort|filter|collect|gather|find all)',
    }

    # Determine input/output types
    input_type = 'Any'
    output_type = 'Any'

    if re.search(patterns['function_with_list'], text_lower):
        input_type = 'list[Any]'
    elif re.search(patterns['function_with_string'], text_lower):
        input_type = 'str'
    elif re.search(patterns['function_with_number'], text_lower):
        input_type = 'int'

    if re.search(patterns['function_returns_bool'], text_lower):
        output_type = 'bool'
    elif re.search(patterns['function_returns_list'], text_lower):
        output_type = 'list[Any]'
    elif 'count' in text_lower or 'sum' in text_lower or 'total' in text_lower:
        output_type = 'int'
    elif 'reverse' in text_lower or 'convert' in text_lower:
        output_type = input_type

    # Generate a function name
    name = sanitize_name(text)
    if not name.replace('_', '').replace('-', '').isidentifier():
        name = f"func_{name}"

    # Create parameter name based on input type
    param_name = 'input_value'
    if 'list' in input_type:
        param_name = 'items'
    elif input_type == 'str':
        param_name = 'text'
    elif input_type == 'int':
        param_name = 'n'

    return {
        'name': name,
        'input_type': input_type,
        'output_type': output_type,
        'param_name': param_name,
        'description': text
    }

def generate_v3_spec(text: str) -> str:
    """Generate a V3 spec markdown from English text"""
    details = infer_function_details(text)

    spec = f"""# SpecV3: {text}

## Metadata
- Generated: {datetime.now().isoformat()}
- Source: English prompt
- Template: generic

## Function Definition

```python
def {details['name']}({details['param_name']}: {details['input_type']}) -> {details['output_type']}:
    \"\"\"
    {details['description']}

    This is a generic template placeholder function.
    \"\"\"
    pass
```

## Examples

```python
# Example 1
{details['param_name']} = # TODO: Add example input
expected_output = # TODO: Add expected output
assert {details['name']}({details['param_name']}) == expected_output

# Example 2
{details['param_name']} = # TODO: Add another example input
expected_output = # TODO: Add expected output
assert {details['name']}({details['param_name']}) == expected_output
```

## Description

{details['description']}

This specification was auto-generated from an English prompt.
The function signature and examples may need refinement.

## Tags
- auto-generated
- english-mode
- generic-template
"""
    return spec

def main():
    if len(sys.argv) < 2:
        print("Usage: python english_to_spec.py 'your English request'")
        print("       python english_to_spec.py --stdin < request.txt")
        sys.exit(1)

    # Get input text
    if sys.argv[1] == '--stdin':
        text = sys.stdin.read().strip()
    else:
        text = ' '.join(sys.argv[1:])

    if not text:
        print("Error: Empty input text")
        sys.exit(1)

    # Generate spec
    spec_content = generate_v3_spec(text)

    # Ensure requests directory exists
    requests_dir = Path("specs/requests")
    requests_dir.mkdir(parents=True, exist_ok=True)

    # Save spec to file
    filename = f"{sanitize_name(text)}.md"
    spec_path = requests_dir / filename

    with open(spec_path, 'w') as f:
        f.write(spec_content)

    print(f"✅ Spec generated: {spec_path}")
    print(f"📝 Function name: {infer_function_details(text)['name']}")

    # Also output the path for scripting
    print(f"SPEC_PATH={spec_path}")

    return spec_path

if __name__ == "__main__":
    main()
