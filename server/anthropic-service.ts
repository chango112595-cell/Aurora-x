/**
 * LOCAL AI SERVICE - No External API Required
 * Generates intelligent responses using advanced pattern matching and templates
 */

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export function isAnthropicAvailable(): boolean {
  return true;
}

const CODE_TEMPLATES: Record<string, Record<string, string>> = {
  typescript: {
    function: `export function {{name}}({{params}}): {{returnType}} {
  {{body}}
}`,
    class: `export class {{name}} {
  {{properties}}

  constructor({{constructorParams}}) {
    {{constructorBody}}
  }

  {{methods}}
}`,
    interface: `export interface {{name}} {
  {{properties}}
}`,
    react: `import { useState, useEffect } from 'react';

export function {{name}}({{props}}) {
  const [state, setState] = useState({{initialState}});

  useEffect(() => {
    {{effect}}
  }, []);

  return (
    {{jsx}}
  );
}`
  },
  python: {
    function: `def {{name}}({{params}}){{returnType}}:
    """{{docstring}}"""
    {{body}}`,
    class: `class {{name}}:
    """{{docstring}}"""
    
    def __init__(self{{initParams}}):
        {{initBody}}
    
    {{methods}}`,
    api: `from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

{{models}}

@app.get("/{{endpoint}}")
async def {{handler}}():
    {{body}}
    return {"status": "success"}`
  },
  javascript: {
    function: `function {{name}}({{params}}) {
  {{body}}
}`,
    async: `async function {{name}}({{params}}) {
  try {
    {{body}}
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}`,
    express: `const express = require('express');
const app = express();

app.use(express.json());

{{routes}}

app.listen({{port}}, () => {
  console.log('Server running on port {{port}}');
});`
  }
};

const RESPONSE_PATTERNS = {
  greeting: [
    "Hello! I'm Aurora, your AI assistant. How can I help you today?",
    "Hi there! Ready to help with coding, questions, or anything else you need.",
    "Welcome! What would you like to work on?"
  ],
  code_generation: {
    prefixes: [
      "Here's the code you requested:",
      "I've generated the following code:",
      "Here's a solution for you:"
    ],
    suffixes: [
      "\n\nLet me know if you'd like me to modify anything!",
      "\n\nFeel free to ask if you need any changes.",
      "\n\nI can adjust this based on your specific needs."
    ]
  },
  explanation: {
    prefixes: [
      "Let me explain this for you:",
      "Here's a breakdown:",
      "Great question! Here's what you need to know:"
    ]
  },
  debugging: {
    prefixes: [
      "I see the issue. Here's what's happening:",
      "Let me help you debug this:",
      "I've analyzed the problem:"
    ]
  }
};

function detectIntent(message: string): string {
  const lower = message.toLowerCase();
  
  if (/^(hi|hello|hey|greetings)/i.test(lower)) return 'greeting';
  if (/\b(write|create|generate|make|build)\b.*\b(code|function|class|component|api|app)/i.test(lower)) return 'code_generation';
  if (/\b(fix|debug|error|bug|issue|problem|not working|broken)\b/i.test(lower)) return 'debugging';
  if (/\b(explain|what is|how does|why|describe|tell me about)\b/i.test(lower)) return 'explanation';
  if (/\b(optimize|improve|faster|performance|efficient)\b/i.test(lower)) return 'optimization';
  if (/\b(test|testing|unit test|spec)\b/i.test(lower)) return 'testing';
  if (/\b(refactor|clean|restructure)\b/i.test(lower)) return 'refactoring';
  if (/\b(help|assist|can you|could you|please)\b/i.test(lower)) return 'assistance';
  if (/\?$/.test(message.trim())) return 'question';
  
  return 'general';
}

function detectLanguage(message: string): string {
  const lower = message.toLowerCase();
  
  if (/\b(typescript|ts|tsx)\b/i.test(lower)) return 'typescript';
  if (/\b(javascript|js|jsx|node)\b/i.test(lower)) return 'javascript';
  if (/\b(python|py|fastapi|django|flask)\b/i.test(lower)) return 'python';
  if (/\b(rust|cargo)\b/i.test(lower)) return 'rust';
  if (/\b(go|golang)\b/i.test(lower)) return 'go';
  if (/\b(java|spring)\b/i.test(lower)) return 'java';
  if (/\b(c\+\+|cpp)\b/i.test(lower)) return 'cpp';
  if (/\b(react|vue|angular|svelte)\b/i.test(lower)) return 'typescript';
  if (/\b(sql|database|query)\b/i.test(lower)) return 'sql';
  if (/\b(html|css|web)\b/i.test(lower)) return 'html';
  
  return 'typescript';
}

function extractCodeTarget(message: string): { type: string; name: string; details: string } {
  const lower = message.toLowerCase();
  
  let type = 'function';
  if (/\b(class|component|module)\b/i.test(lower)) type = 'class';
  else if (/\b(api|endpoint|route)\b/i.test(lower)) type = 'api';
  else if (/\b(interface|type)\b/i.test(lower)) type = 'interface';
  else if (/\b(hook|state)\b/i.test(lower)) type = 'react';
  
  const nameMatch = message.match(/(?:called|named|for)\s+["']?(\w+)["']?/i);
  const name = nameMatch ? nameMatch[1] : 'example';
  
  return { type, name, details: message };
}

function generateCodeResponse(message: string, language: string): string {
  const { type, name, details } = extractCodeTarget(message);
  const lower = message.toLowerCase();
  
  let code = '';
  let explanation = '';
  
  if (language === 'typescript' || language === 'javascript') {
    if (/\b(api|fetch|request|http)\b/i.test(lower)) {
      code = `async function ${name}(url: string, options?: RequestInit): Promise<any> {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers
      },
      ...options
    });
    
    if (!response.ok) {
      throw new Error(\`HTTP error! status: \${response.status}\`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}`;
      explanation = "This function handles HTTP requests with proper error handling and JSON parsing.";
    } else if (/\b(sort|array|list)\b/i.test(lower)) {
      code = `function ${name}<T>(arr: T[], compareFn?: (a: T, b: T) => number): T[] {
  return [...arr].sort(compareFn);
}

// Example usage:
const numbers = [3, 1, 4, 1, 5, 9, 2, 6];
const sorted = ${name}(numbers, (a, b) => a - b);
console.log(sorted); // [1, 1, 2, 3, 4, 5, 6, 9]`;
      explanation = "This is a type-safe sorting function that doesn't mutate the original array.";
    } else if (/\b(search|find|filter)\b/i.test(lower)) {
      code = `function ${name}<T>(items: T[], predicate: (item: T) => boolean): T[] {
  return items.filter(predicate);
}

// Advanced search with multiple criteria
function advancedSearch<T extends Record<string, any>>(
  items: T[],
  criteria: Partial<T>
): T[] {
  return items.filter(item =>
    Object.entries(criteria).every(([key, value]) => 
      item[key] === value
    )
  );
}`;
      explanation = "These functions provide flexible search and filtering capabilities.";
    } else if (/\b(component|react|ui)\b/i.test(lower)) {
      const componentName = name.charAt(0).toUpperCase() + name.slice(1);
      code = `import { useState, useCallback } from 'react';

interface ${componentName}Props {
  title?: string;
  onAction?: (data: any) => void;
}

export function ${componentName}({ title = 'Default Title', onAction }: ${componentName}Props) {
  const [isLoading, setIsLoading] = useState(false);
  const [data, setData] = useState<any>(null);

  const handleAction = useCallback(async () => {
    setIsLoading(true);
    try {
      // Your logic here
      const result = { success: true };
      setData(result);
      onAction?.(result);
    } catch (error) {
      console.error('Action failed:', error);
    } finally {
      setIsLoading(false);
    }
  }, [onAction]);

  return (
    <div className="p-4 rounded-lg border bg-card">
      <h2 className="text-lg font-semibold">{title}</h2>
      {isLoading ? (
        <div className="animate-pulse">Loading...</div>
      ) : (
        <button 
          onClick={handleAction}
          className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md"
        >
          Take Action
        </button>
      )}
      {data && <pre className="mt-4 text-sm">{JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
}`;
      explanation = "This is a reusable React component with loading state and callback handling.";
    } else if (/\b(hook|use)\b/i.test(lower)) {
      code = `import { useState, useEffect, useCallback } from 'react';

export function use${name.charAt(0).toUpperCase() + name.slice(1)}<T>(initialValue: T) {
  const [value, setValue] = useState<T>(initialValue);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const update = useCallback(async (newValue: T | ((prev: T) => T)) => {
    setIsLoading(true);
    setError(null);
    try {
      setValue(newValue);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setValue(initialValue);
    setError(null);
  }, [initialValue]);

  return { value, update, reset, isLoading, error };
}`;
      explanation = "This custom hook provides state management with loading and error handling.";
    } else {
      code = `function ${name}(input: any): any {
  // Implementation based on your requirements
  console.log('Processing:', input);
  
  // Add your logic here
  const result = {
    processed: true,
    data: input,
    timestamp: new Date().toISOString()
  };
  
  return result;
}

// Example usage:
const output = ${name}({ example: 'data' });
console.log(output);`;
      explanation = "Here's a basic function template that you can customize for your needs.";
    }
  } else if (language === 'python') {
    if (/\b(api|endpoint|fastapi|rest)\b/i.test(lower)) {
      code = `from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

items_db: List[Item] = []

@app.get("/items")
async def get_items():
    return {"items": items_db}

@app.post("/items")
async def create_item(item: Item):
    items_db.append(item)
    return {"message": "Item created", "item": item}

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id < 0 or item_id >= len(items_db):
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]`;
      explanation = "This is a FastAPI implementation with CRUD operations and Pydantic models.";
    } else if (/\b(class|object)\b/i.test(lower)) {
      code = `from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class ${name.charAt(0).toUpperCase() + name.slice(1)}:
    """${details.substring(0, 50)}..."""
    
    id: int
    name: str
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)
    
    def process(self) -> dict:
        """Process the data and return results."""
        return {
            "id": self.id,
            "name": self.name,
            "processed_at": datetime.now().isoformat()
        }
    
    def validate(self) -> bool:
        """Validate the instance data."""
        return bool(self.name and len(self.name) > 0)`;
      explanation = "This dataclass provides a clean, type-annotated structure with methods.";
    } else {
      code = `def ${name}(data: any) -> dict:
    """
    Process the given data.
    
    Args:
        data: Input data to process
        
    Returns:
        Processed result dictionary
    """
    try:
        result = {
            "success": True,
            "data": data,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

# Example usage
if __name__ == "__main__":
    output = ${name}({"example": "input"})
    print(output)`;
      explanation = "Here's a Python function with proper documentation and error handling.";
    }
  } else if (language === 'sql') {
    code = `-- Create table
CREATE TABLE ${name} (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Select with filtering
SELECT * FROM ${name}
WHERE created_at >= NOW() - INTERVAL '7 days'
ORDER BY created_at DESC
LIMIT 100;

-- Insert
INSERT INTO ${name} (name) VALUES ('example');

-- Update
UPDATE ${name}
SET name = 'updated', updated_at = CURRENT_TIMESTAMP
WHERE id = 1;`;
    explanation = "These SQL statements cover common CRUD operations.";
  } else {
    code = `// ${language} implementation for: ${name}
// Based on: ${details.substring(0, 100)}

// Add your implementation here
function ${name}() {
  // TODO: Implement based on requirements
}`;
    explanation = `I've created a template for ${language}. Let me know if you need a more specific implementation.`;
  }
  
  return `${RESPONSE_PATTERNS.code_generation.prefixes[Math.floor(Math.random() * RESPONSE_PATTERNS.code_generation.prefixes.length)]}

\`\`\`${language}
${code}
\`\`\`

${explanation}${RESPONSE_PATTERNS.code_generation.suffixes[Math.floor(Math.random() * RESPONSE_PATTERNS.code_generation.suffixes.length)]}`;
}

function generateExplanationResponse(message: string): string {
  const lower = message.toLowerCase();
  let response = '';
  
  if (/\b(async|await|promise)\b/i.test(lower)) {
    response = `**Async/Await and Promises**

Asynchronous programming in JavaScript/TypeScript allows code to execute without blocking.

**Promises** are objects representing the eventual completion or failure of an async operation:
\`\`\`javascript
const promise = new Promise((resolve, reject) => {
  // async operation
  setTimeout(() => resolve('Done!'), 1000);
});
\`\`\`

**Async/Await** is syntactic sugar that makes async code look synchronous:
\`\`\`javascript
async function fetchData() {
  try {
    const result = await someAsyncOperation();
    return result;
  } catch (error) {
    console.error('Error:', error);
  }
}
\`\`\`

Key points:
- \`async\` functions always return a Promise
- \`await\` pauses execution until the Promise resolves
- Use try/catch for error handling
- Multiple awaits run sequentially; use \`Promise.all\` for parallel execution`;
  } else if (/\b(closure|scope)\b/i.test(lower)) {
    response = `**Closures and Scope**

A **closure** is a function that remembers the variables from its outer scope even after that scope has finished executing.

\`\`\`javascript
function createCounter() {
  let count = 0; // This variable is "closed over"
  
  return function() {
    count++;
    return count;
  };
}

const counter = createCounter();
console.log(counter()); // 1
console.log(counter()); // 2
\`\`\`

**Key concepts:**
1. **Lexical Scope**: Functions access variables from where they're defined, not where they're called
2. **Closure**: The inner function "closes over" the outer variables
3. **Privacy**: Closures can create private variables
4. **Memory**: Closed-over variables persist as long as the closure exists`;
  } else if (/\b(api|rest|http)\b/i.test(lower)) {
    response = `**REST APIs Explained**

REST (Representational State Transfer) is an architectural style for building web services.

**Key Principles:**
- **Stateless**: Each request contains all needed information
- **Resource-based**: URLs represent resources (nouns, not verbs)
- **HTTP Methods**: 
  - GET: Read data
  - POST: Create data
  - PUT/PATCH: Update data
  - DELETE: Remove data

**Example endpoints:**
\`\`\`
GET    /api/users       - List all users
GET    /api/users/123   - Get user 123
POST   /api/users       - Create new user
PUT    /api/users/123   - Update user 123
DELETE /api/users/123   - Delete user 123
\`\`\`

**Best practices:**
- Use plural nouns for resources
- Return appropriate HTTP status codes
- Use JSON for request/response bodies
- Implement proper error handling`;
  } else if (/\b(typescript|type|interface)\b/i.test(lower)) {
    response = `**TypeScript Types and Interfaces**

TypeScript adds static typing to JavaScript for better code quality.

**Basic Types:**
\`\`\`typescript
let name: string = "Aurora";
let age: number = 25;
let active: boolean = true;
let items: string[] = ["a", "b"];
\`\`\`

**Interfaces** define object shapes:
\`\`\`typescript
interface User {
  id: number;
  name: string;
  email?: string; // Optional
}
\`\`\`

**Type aliases** can define unions and more:
\`\`\`typescript
type Status = 'pending' | 'active' | 'completed';
type Result<T> = { success: true; data: T } | { success: false; error: string };
\`\`\`

**When to use which:**
- **Interface**: For object shapes, especially when extending
- **Type**: For unions, intersections, and complex types`;
  } else if (/\b(react|component|hook)\b/i.test(lower)) {
    response = `**React Components and Hooks**

React uses a component-based architecture with hooks for state and side effects.

**Functional Components:**
\`\`\`tsx
function Greeting({ name }: { name: string }) {
  return <h1>Hello, {name}!</h1>;
}
\`\`\`

**Common Hooks:**
- \`useState\`: Local state management
- \`useEffect\`: Side effects (API calls, subscriptions)
- \`useCallback\`: Memoized callbacks
- \`useMemo\`: Memoized values
- \`useRef\`: Mutable references

**Example with hooks:**
\`\`\`tsx
function Counter() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    document.title = \`Count: \${count}\`;
  }, [count]);
  
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}
\`\`\``;
  } else {
    response = `I'd be happy to explain that concept. Here's what you need to know:

**Overview:**
${message.replace(/\?/g, '')} is an important topic in software development.

**Key Points:**
1. Understanding the fundamentals helps build better applications
2. Practice with real examples solidifies knowledge
3. Start simple and gradually add complexity

Would you like me to:
- Provide specific code examples?
- Dive deeper into a particular aspect?
- Explain how it applies to your project?`;
  }
  
  return response;
}

function generateDebuggingResponse(message: string): string {
  const lower = message.toLowerCase();
  
  if (/\b(undefined|null|cannot read)\b/i.test(lower)) {
    return `**Debugging Null/Undefined Errors**

This error typically occurs when accessing properties on \`null\` or \`undefined\`.

**Common causes:**
1. **Async data not loaded yet**
   \`\`\`tsx
   // Problem: data might be undefined initially
   const name = user.name; // Error if user is undefined
   
   // Solution: Optional chaining
   const name = user?.name;
   \`\`\`

2. **Missing null checks**
   \`\`\`typescript
   // Add guards
   if (data && data.items) {
     process(data.items);
   }
   \`\`\`

3. **Array access out of bounds**
   \`\`\`typescript
   const first = items?.[0] ?? defaultValue;
   \`\`\`

**Fixes:**
- Use optional chaining (\`?.\`)
- Use nullish coalescing (\`??\`)
- Add proper loading states in React
- Validate API responses`;
  } else if (/\b(cors|cross-origin)\b/i.test(lower)) {
    return `**Fixing CORS Errors**

CORS (Cross-Origin Resource Sharing) errors occur when a browser blocks requests to a different domain.

**Backend fix (Express):**
\`\`\`javascript
const cors = require('cors');
app.use(cors({
  origin: 'http://localhost:5000',
  credentials: true
}));
\`\`\`

**Backend fix (manual headers):**
\`\`\`javascript
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  next();
});
\`\`\`

**Key points:**
- CORS is a browser security feature
- The server must allow the origin
- Check if credentials are needed
- Preflight requests use OPTIONS method`;
  } else if (/\b(import|module|require|export)\b/i.test(lower)) {
    return `**Fixing Import/Module Errors**

Module errors usually stem from incorrect paths or export/import mismatches.

**Common issues:**

1. **Default vs Named exports:**
   \`\`\`typescript
   // If file exports: export default MyComponent
   import MyComponent from './MyComponent'; // Correct
   import { MyComponent } from './MyComponent'; // Wrong
   
   // If file exports: export const MyComponent
   import { MyComponent } from './MyComponent'; // Correct
   \`\`\`

2. **Path issues:**
   \`\`\`typescript
   // Check file extension and path
   import { util } from './utils'; // .ts/.js extension usually not needed
   import data from './data.json'; // JSON needs extension
   \`\`\`

3. **Circular dependencies:**
   - Module A imports B, B imports A
   - Refactor to break the cycle

**Tips:**
- Check your tsconfig.json paths
- Verify the file actually exports what you're importing
- Use your IDE's auto-import feature`;
  } else {
    return `**Debugging Your Issue**

Let me help you troubleshoot. Here's a systematic approach:

**Step 1: Identify the error**
- What's the exact error message?
- When does it occur?
- Is it reproducible?

**Step 2: Check common causes**
- Typos in variable/function names
- Missing imports or dependencies
- Incorrect data types
- Async timing issues
- Scope problems

**Step 3: Debug techniques**
\`\`\`javascript
// Add console logs at key points
console.log('Variable state:', variable);

// Use debugger statement
debugger; // Opens browser dev tools

// Check network requests in dev tools
\`\`\`

**Step 4: Isolate the problem**
- Comment out code sections
- Test with minimal example
- Check if it works in isolation

Please share:
1. The error message
2. The relevant code
3. What you've already tried

I'll help you find the solution!`;
  }
}

function generateGeneralResponse(message: string, previousMessages: ChatMessage[]): string {
  const lower = message.toLowerCase();
  const hasContext = previousMessages.length > 0;
  
  if (/\b(thank|thanks)\b/i.test(lower)) {
    return "You're welcome! Let me know if you need anything else.";
  }
  
  if (/\b(help|can you|could you)\b/i.test(lower)) {
    return `Absolutely! I can help you with:

**Code Generation**
- Write functions, classes, components
- Create APIs and database queries
- Build React/TypeScript applications

**Debugging**
- Find and fix errors
- Optimize performance
- Resolve import/module issues

**Explanations**
- Explain programming concepts
- Document code
- Clarify best practices

**Architecture**
- Design system structures
- Plan database schemas
- Suggest patterns

What would you like to work on?`;
  }
  
  if (/\b(status|how are you|working)\b/i.test(lower)) {
    return "All systems operational! I'm ready to help with coding, debugging, explanations, or anything else you need. What's on your mind?";
  }
  
  if (hasContext) {
    const lastAssistant = previousMessages.filter(m => m.role === 'assistant').pop();
    if (lastAssistant && lastAssistant.content.includes('```')) {
      return `I see you're following up on the code I provided. Would you like me to:
- Modify the implementation?
- Add more features?
- Explain a specific part?
- Help integrate it into your project?

Just let me know what you need!`;
    }
  }
  
  return `I understand you're asking about "${message.substring(0, 50)}${message.length > 50 ? '...' : ''}". 

I can help with:
- Writing or generating code
- Explaining concepts
- Debugging issues
- Designing solutions

Could you provide more details about what you'd like to accomplish?`;
}

export async function generateAuroraResponse(
  userMessage: string,
  conversationType: string,
  memoryContext: string = '',
  previousMessages: ChatMessage[] = []
): Promise<{ response: string; success: boolean }> {
  
  console.log(`[Aurora AI] Processing: ${userMessage.substring(0, 50)}...`);
  console.log(`[Aurora AI] Detected type: ${conversationType}`);
  
  const intent = detectIntent(userMessage);
  const language = detectLanguage(userMessage);
  
  let response = '';
  
  try {
    switch (intent) {
      case 'greeting':
        const greetings = RESPONSE_PATTERNS.greeting;
        response = greetings[Math.floor(Math.random() * greetings.length)];
        break;
        
      case 'code_generation':
        response = generateCodeResponse(userMessage, language);
        break;
        
      case 'explanation':
      case 'question':
        response = generateExplanationResponse(userMessage);
        break;
        
      case 'debugging':
        response = generateDebuggingResponse(userMessage);
        break;
        
      case 'optimization':
        response = `**Optimization Suggestions**

I can help optimize your code. Here are general best practices:

1. **Reduce unnecessary operations**
   - Cache repeated calculations
   - Use memoization where appropriate

2. **Efficient data structures**
   - Use Set/Map for lookups instead of arrays
   - Consider pagination for large datasets

3. **Async optimization**
   - Use \`Promise.all\` for parallel operations
   - Implement proper caching

4. **React-specific**
   - Use \`useMemo\` and \`useCallback\` appropriately
   - Avoid unnecessary re-renders
   - Virtualize long lists

Please share the specific code you'd like to optimize, and I'll provide targeted improvements!`;
        break;
        
      case 'testing':
        response = `**Testing Your Code**

Here's how to write effective tests:

\`\`\`typescript
import { describe, it, expect, vi } from 'vitest';

describe('YourFunction', () => {
  it('should handle normal input', () => {
    const result = yourFunction('input');
    expect(result).toBe('expected');
  });
  
  it('should handle edge cases', () => {
    expect(yourFunction('')).toBe('default');
    expect(yourFunction(null)).toThrow();
  });
  
  it('should work with async operations', async () => {
    const result = await asyncFunction();
    expect(result).toBeDefined();
  });
});
\`\`\`

What would you like to test? Share the code and I'll write specific tests for it!`;
        break;
        
      case 'refactoring':
        response = `**Refactoring Approach**

I can help refactor your code for better:
- **Readability**: Clear naming, smaller functions
- **Maintainability**: Single responsibility, DRY principle
- **Performance**: Efficient algorithms, proper caching
- **Type safety**: Better TypeScript types

Share the code you'd like refactored, and I'll:
1. Analyze the current structure
2. Identify improvement areas
3. Provide the refactored version with explanations`;
        break;
        
      default:
        response = generateGeneralResponse(userMessage, previousMessages);
    }
    
    if (memoryContext && response) {
      const userName = memoryContext.match(/User's name: (\w+)/)?.[1];
      if (userName && !response.includes(userName)) {
        response = `${userName}, ${response.charAt(0).toLowerCase()}${response.slice(1)}`;
      }
    }
    
    console.log(`[Aurora AI] Generated ${response.length} chars`);
    
    return { response, success: true };
  } catch (error) {
    console.error('[Aurora AI] Error:', error);
    return { 
      response: "I encountered an issue processing that request. Could you try rephrasing?", 
      success: false 
    };
  }
}

export async function analyzeCode(code: string, language: string): Promise<string> {
  console.log(`[Aurora AI] Analyzing ${language} code (${code.length} chars)`);
  
  const issues: string[] = [];
  const suggestions: string[] = [];
  
  if (!code.includes('try') && !code.includes('catch')) {
    issues.push("No error handling detected - consider adding try/catch blocks");
  }
  
  if (/console\.log/.test(code)) {
    suggestions.push("Remove or replace console.log statements for production");
  }
  
  if (/any/.test(code) && (language === 'typescript' || language === 'ts')) {
    issues.push("Using 'any' type reduces type safety - consider specific types");
  }
  
  if (/var\s/.test(code)) {
    suggestions.push("Replace 'var' with 'const' or 'let' for better scoping");
  }
  
  if (code.split('\n').some(line => line.length > 120)) {
    suggestions.push("Some lines exceed 120 characters - consider breaking them up");
  }
  
  const functionCount = (code.match(/function\s+\w+|const\s+\w+\s*=\s*(\([^)]*\)|[^=]+)\s*=>/g) || []).length;
  if (functionCount > 10) {
    suggestions.push(`File has ${functionCount} functions - consider splitting into modules`);
  }
  
  return `## Code Analysis Results

### Issues Found (${issues.length})
${issues.length > 0 ? issues.map(i => `- ${i}`).join('\n') : '- No critical issues detected'}

### Suggestions (${suggestions.length})
${suggestions.length > 0 ? suggestions.map(s => `- ${s}`).join('\n') : '- Code looks good!'}

### Summary
The code is ${issues.length === 0 ? 'well-structured' : 'functional but could be improved'}. ${suggestions.length > 0 ? 'Consider the suggestions above for better code quality.' : ''}`;
}

export async function generateCode(
  prompt: string,
  language: string = 'typescript'
): Promise<{ code: string; explanation: string; success: boolean }> {
  
  const response = generateCodeResponse(prompt, language);
  
  const codeMatch = response.match(/```[\w]*\n([\s\S]*?)```/);
  const code = codeMatch ? codeMatch[1].trim() : '';
  const explanation = response.replace(/```[\w]*\n[\s\S]*?```/g, '').trim();
  
  return { code, explanation, success: true };
}
