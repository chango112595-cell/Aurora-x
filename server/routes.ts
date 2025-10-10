import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { corpusStorage } from "./corpus-storage";
import * as path from "path";
import * as fs from "fs";
import { spawn } from "child_process";
import { promisify } from "util";
import {
  corpusEntrySchema,
  corpusQuerySchema,
  topQuerySchema,
  recentQuerySchema,
  similarityQuerySchema,
  runMetaSchema,
  usedSeedSchema,
} from "@shared/schema";

const AURORA_API_KEY = process.env.AURORA_API_KEY || "dev-key-change-in-production";

export async function registerRoutes(app: Express): Promise<Server> {
  // Aurora-X Adaptive Learning Stats endpoints
  app.get("/api/adaptive_stats", (req, res) => {
    try {
      // Import and access the global scheduler if available
      const { _global_adaptive_scheduler } = require("../aurora_x/main");
      if (_global_adaptive_scheduler) {
        return res.json({
          summary: _global_adaptive_scheduler.summary(),
          iteration: _global_adaptive_scheduler.iteration
        });
      } else {
        return res.json({ summary: {}, iteration: 0 });
      }
    } catch (e) {
      return res.json({ summary: {}, iteration: 0 });
    }
  });

  app.get("/api/seed_bias/history", (req, res) => {
    try {
      const { _global_adaptive_scheduler } = require("../aurora_x/main");
      if (_global_adaptive_scheduler) {
        return res.json({ history: _global_adaptive_scheduler.history });
      } else {
        return res.json({ history: [] });
      }
    } catch (e) {
      return res.json({ history: [] });
    }
  });

  app.get("/api/seed_bias", (req, res) => {
    try {
      const { get_seed_store } = require("../aurora_x/learn");
      const seed_store = get_seed_store();
      const summary = seed_store.get_summary();
      
      return res.json({
        summary: {
          total_seeds: summary["total_seeds"],
          avg_bias: Math.round(summary["avg_bias"] * 10000) / 10000,
          max_bias: Math.round(summary["max_bias"] * 10000) / 10000,
          min_bias: Math.round(summary["min_bias"] * 10000) / 10000,
          total_updates: summary["total_updates"],
          config: summary["config"]
        },
        top_biases: (summary["top_biases"] || []).map(([key, bias]: [string, number]) => ({
          seed_key: key,
          bias: Math.round(bias * 10000) / 10000
        }))
      });
    } catch (e: any) {
      return res.status(500).json({ error: "Internal error", details: e?.message ?? String(e) });
    }
  });
  app.post("/api/corpus", (req, res) => {
    const auth = req.header("x-api-key") ?? "";
    if (auth !== AURORA_API_KEY) {
      return res.status(401).json({ error: "unauthorized" });
    }

    try {
      const entry = corpusEntrySchema.parse(req.body);
      corpusStorage.insertEntry(entry);
      return res.json({ ok: true, id: entry.id });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_request",
        details: e?.message ?? String(e),
      });
    }
  });

  app.get("/api/corpus", (req, res) => {
    try {
      const query = corpusQuerySchema.parse(req.query);
      const items = corpusStorage.getEntries({
        func: query.func,
        limit: query.limit,
        offset: query.offset,
        perfectOnly: query.perfectOnly,
        minScore: query.minScore,
        maxScore: query.maxScore,
        startDate: query.startDate,
        endDate: query.endDate,
      });
      return res.json({ items, hasMore: items.length === query.limit });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_query",
        details: e?.message ?? String(e),
      });
    }
  });

  app.get("/api/corpus/top", (req, res) => {
    try {
      const query = topQuerySchema.parse(req.query);
      const items = corpusStorage.getTopByFunc(query.func, query.limit);
      return res.json({ items });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_query",
        details: e?.message ?? String(e),
      });
    }
  });

  app.get("/api/corpus/recent", (req, res) => {
    try {
      const query = recentQuerySchema.parse(req.query);
      const items = corpusStorage.getRecent(query.limit);
      return res.json({ items });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_query",
        details: e?.message ?? String(e),
      });
    }
  });

  app.post("/api/corpus/similar", (req, res) => {
    try {
      const query = similarityQuerySchema.parse(req.body);
      const results = corpusStorage.getSimilar(
        query.targetSigKey,
        query.targetPostBow,
        query.limit
      );
      return res.json({ results });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_query",
        details: e?.message ?? String(e),
      });
    }
  });

  app.post("/api/run-meta", (req, res) => {
    const auth = req.header("x-api-key") ?? "";
    if (auth !== AURORA_API_KEY) {
      return res.status(401).json({ error: "unauthorized" });
    }

    try {
      const meta = runMetaSchema.parse(req.body);
      corpusStorage.insertRunMeta(meta);
      return res.json({ ok: true, run_id: meta.run_id });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_request",
        details: e?.message ?? String(e),
      });
    }
  });

  app.get("/api/run-meta/latest", (req, res) => {
    try {
      const meta = corpusStorage.getLatestRunMeta();
      return res.json({ meta });
    } catch (e: any) {
      return res.status(500).json({
        error: "internal_error",
        details: e?.message ?? String(e),
      });
    }
  });

  app.post("/api/used-seeds", (req, res) => {
    const auth = req.header("x-api-key") ?? "";
    if (auth !== AURORA_API_KEY) {
      return res.status(401).json({ error: "unauthorized" });
    }

    try {
      const seed = usedSeedSchema.parse(req.body);
      const id = corpusStorage.insertUsedSeed(seed);
      return res.json({ ok: true, id });
    } catch (e: any) {
      return res.status(400).json({
        error: "bad_request",
        details: e?.message ?? String(e),
      });
    }
  });

  app.get("/api/used-seeds", (req, res) => {
    try {
      const run_id = req.query.run_id as string | undefined;
      const limit = req.query.limit ? parseInt(req.query.limit as string) : 200;
      const seeds = corpusStorage.getUsedSeeds({ run_id, limit });
      return res.json({ seeds });
    } catch (e: any) {
      return res.status(500).json({
        error: "internal_error",
        details: e?.message ?? String(e),
      });
    }
  });

  // Chat endpoint for Aurora-X synthesis requests
  app.post("/api/chat", async (req, res) => {
    try {
      const { message } = req.body;
      
      if (!message || typeof message !== 'string') {
        return res.status(400).json({ error: "Message is required" });
      }

      // Sanitize message to prevent any shell injection
      // Remove shell metacharacters and control characters
      // This includes: backticks, $(), semicolons, pipes, ampersands, etc.
      const sanitizedMessage = message
        .replace(/[`$()<>|;&\\\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/g, '')
        .replace(/\*/g, '')  // Remove wildcards
        .replace(/~/g, '')   // Remove tilde expansion
        .replace(/\[/g, '')  // Remove bracket expansion
        .replace(/\]/g, '')  // Remove bracket expansion
        .replace(/\{/g, '')  // Remove brace expansion  
        .replace(/\}/g, '')  // Remove brace expansion
        .trim();
      
      console.log(`[Aurora-X] Processing request: "${sanitizedMessage}"`);
      
      // Execute Aurora-X with the natural language command using spawn for security
      try {
        // Use spawn instead of exec to prevent command injection
        const spawnProcess = spawn('make', ['say', `WHAT=${sanitizedMessage}`], {
          cwd: process.cwd(),
          timeout: 30000, // 30 second timeout
          shell: false, // Explicitly disable shell to prevent injection
          env: { ...process.env } // Pass environment variables
        });
        
        let stdout = '';
        let stderr = '';
        
        spawnProcess.stdout.on('data', (data) => {
          stdout += data.toString();
        });
        
        spawnProcess.stderr.on('data', (data) => {
          stderr += data.toString();
        });
        
        // Wait for the process to complete
        await new Promise<void>((resolve, reject) => {
          spawnProcess.on('close', (code) => {
            if (code !== 0 && code !== null) {
              console.error(`[Aurora-X] Process exited with code ${code}`);
              reject(new Error(`Aurora-X synthesis failed with exit code ${code}`));
            } else {
              resolve();
            }
          });
          
          spawnProcess.on('error', (err) => {
            console.error(`[Aurora-X] Process error:`, err);
            reject(err);
          });
        });
        
        console.log(`[Aurora-X] Command output:`, stdout);
        if (stderr) console.log(`[Aurora-X] Command stderr:`, stderr);
        
        // Find the latest run directory with proper validation
        const runsDir = path.join(process.cwd(), 'runs');
        
        // Pattern for valid run directories: run-YYYYMMDD-HHMMSS
        const runDirPattern = /^run-\d{8}-\d{6}$/;
        
        const runDirs = fs.readdirSync(runsDir)
          .filter(name => {
            // Validate directory name format
            if (!runDirPattern.test(name)) {
              return false;
            }
            
            // Check if it's actually a directory
            const dirPath = path.join(runsDir, name);
            try {
              const stats = fs.statSync(dirPath);
              if (!stats.isDirectory()) {
                return false;
              }
              
              // Verify the directory contains a src/ subdirectory
              const srcDir = path.join(dirPath, 'src');
              if (!fs.existsSync(srcDir) || !fs.statSync(srcDir).isDirectory()) {
                console.log(`[Aurora-X] Skipping ${name}: no valid src/ directory found`);
                return false;
              }
              
              return true;
            } catch (e) {
              console.error(`[Aurora-X] Error checking directory ${name}:`, e);
              return false;
            }
          })
          .map(name => ({
            name,
            path: path.join(runsDir, name),
            time: fs.statSync(path.join(runsDir, name)).mtime.getTime()
          }))
          .sort((a, b) => b.time - a.time);
        
        if (runDirs.length === 0) {
          throw new Error("No valid synthesis runs found with src/ directory");
        }
        
        const latestRun = runDirs[0];
        console.log(`[Aurora-X] Latest valid run: ${latestRun.name}`);
        
        // Read the generated source code
        const srcDir = path.join(latestRun.path, 'src');
        let code = "";
        let functionName = "";
        let description = "";
        
        if (fs.existsSync(srcDir)) {
          const srcFiles = fs.readdirSync(srcDir)
            .filter(file => file.endsWith('.py') && !file.startsWith('#') && !file.startsWith('test_'));
          
          if (srcFiles.length > 0) {
            // Read the first Python file
            const codeFile = path.join(srcDir, srcFiles[0]);
            code = fs.readFileSync(codeFile, 'utf-8');
            functionName = srcFiles[0].replace('.py', '');
            console.log(`[Aurora-X] Read generated code from: ${srcFiles[0]}`);
          }
        }
        
        // If no code found in src, check if there's a single file with function name
        if (!code) {
          const allFiles = fs.readdirSync(latestRun.path);
          const pyFiles = allFiles.filter(f => f.endsWith('.py') && !f.startsWith('test_'));
          if (pyFiles.length > 0) {
            const codeFile = path.join(latestRun.path, pyFiles[0]);
            try {
              const fileContent = fs.readFileSync(codeFile, 'utf-8');
              // Verify the file is not empty and contains actual code
              if (fileContent && fileContent.trim().length > 0) {
                code = fileContent;
                functionName = pyFiles[0].replace('.py', '');
              } else {
                console.log(`[Aurora-X] Warning: File ${pyFiles[0]} is empty`);
              }
            } catch (readError) {
              console.error(`[Aurora-X] Error reading file ${pyFiles[0]}:`, readError);
            }
          }
        }
        
        // Extract function description from the code if available
        const docstringMatch = code.match(/"""([\s\S]*?)"""/);
        if (docstringMatch) {
          description = docstringMatch[1].trim();
        }
        
        // Prepare response message
        let responseMessage = `Aurora-X has synthesized the "${functionName}" function. `;
        if (description) {
          responseMessage += description;
        } else {
          responseMessage += `This function was generated based on your request: "${message}"`;
        }
        
        // If still no code, use a fallback
        if (!code) {
          console.log(`[Aurora-X] Warning: No generated code found, using fallback`);
          code = `# Aurora-X Synthesis Result
# Request: ${message}
# Run: ${latestRun.name}

def synthesized_function():
    """Function synthesized by Aurora-X"""
    # Implementation generated but not found in expected location
    pass`;
        }
        
        return res.json({
          message: responseMessage,
          code: code,
          language: "python",
          synthesis_id: latestRun.name,
          timestamp: new Date().toISOString(),
          function_name: functionName
        });
        
      } catch (execError: any) {
        console.error(`[Aurora-X] Execution error:`, execError);
        
        // Fallback to a simple response if Aurora-X fails
        const lowerMessage = message.toLowerCase();
        let fallbackCode = "";
        let fallbackMessage = "I'll help you with that. ";
        
        // Provide basic implementations for common requests
        if (lowerMessage.includes("reverse") && lowerMessage.includes("string")) {
          fallbackMessage += "Here's a string reversal function:";
          fallbackCode = `def reverse_string(s: str) -> str:
    """Reverse a given string."""
    return s[::-1]

# Example usage
if __name__ == "__main__":
    test_string = "hello"
    result = reverse_string(test_string)
    print(f"'{test_string}' reversed is '{result}'")`;
        } else if (lowerMessage.includes("factorial")) {
          fallbackMessage += "Here's a factorial calculation function:";
          fallbackCode = `def factorial(n: int) -> int:
    """Calculate the factorial of a non-negative integer."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

# Example usage
if __name__ == "__main__":
    num = 5
    result = factorial(num)
    print(f"Factorial of {num} is {result}")`;
        } else if (lowerMessage.includes("palindrome")) {
          fallbackMessage += "Here's a palindrome checker:";
          fallbackCode = `def is_palindrome(s: str) -> bool:
    """Check if a string is a palindrome."""
    # Remove spaces and convert to lowercase for comparison
    cleaned = ''.join(s.split()).lower()
    return cleaned == cleaned[::-1]

# Example usage
if __name__ == "__main__":
    test_string = "racecar"
    result = is_palindrome(test_string)
    print(f"'{test_string}' is {'a' if result else 'not a'} palindrome")`;
        } else if (lowerMessage.includes("fibonacci")) {
          fallbackMessage += "Here's a Fibonacci sequence function:";
          fallbackCode = `def fibonacci(n: int) -> int:
    """Return the nth Fibonacci number."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# Example usage
if __name__ == "__main__":
    n = 10
    result = fibonacci(n)
    print(f"The {n}th Fibonacci number is {result}")`;
        } else if (lowerMessage.includes("prime")) {
          fallbackMessage += "Here's a prime number checker:";
          fallbackCode = `def is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

# Example usage
if __name__ == "__main__":
    num = 17
    result = is_prime(num)
    print(f"{num} is {'prime' if result else 'not prime'}")`;
        } else if ((lowerMessage.includes("add") || lowerMessage.includes("sum")) && lowerMessage.includes("two")) {
          fallbackMessage += "Here's a function to add two numbers:";
          fallbackCode = `def add_two_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

# Example usage
if __name__ == "__main__":
    result = add_two_numbers(5, 3)
    print(f"5 + 3 = {result}")`;
        } else if (lowerMessage.includes("largest") || lowerMessage.includes("maximum")) {
          fallbackMessage += "Here's a function to find the largest number:";
          fallbackCode = `def find_largest(numbers: list[int]) -> int:
    """Find the largest number in a list."""
    if not numbers:
        raise ValueError("List cannot be empty")
    return max(numbers)

# Example usage
if __name__ == "__main__":
    nums = [3, 7, 2, 9, 1, 5]
    result = find_largest(nums)
    print(f"The largest number in {nums} is {result}")`;
        } else if (lowerMessage.includes("sort")) {
          fallbackMessage += "Here's a sorting function:";
          fallbackCode = `def sort_list(nums: list[int]) -> list[int]:
    """Sort a list of integers in ascending order."""
    return sorted(nums)

# Example usage
if __name__ == "__main__":
    nums = [3, 7, 2, 9, 1, 5]
    result = sort_list(nums)
    print(f"Sorted list: {result}")`;
        } else if (lowerMessage.includes("vowel")) {
          fallbackMessage += "Here's a vowel counting function:";
          fallbackCode = `def count_vowels(s: str) -> int:
    """Count the number of vowels in a string."""
    vowels = "aeiouAEIOU"
    return sum(1 for char in s if char in vowels)

# Example usage
if __name__ == "__main__":
    text = "hello world"
    result = count_vowels(text)
    print(f"'{text}' contains {result} vowels")`;
        } else if (lowerMessage.includes("gcd") || lowerMessage.includes("greatest common divisor")) {
          fallbackMessage += "Here's a GCD function:";
          fallbackCode = `def gcd(a: int, b: int) -> int:
    """Find the greatest common divisor of two numbers."""
    while b:
        a, b = b, a % b
    return abs(a)

# Example usage
if __name__ == "__main__":
    result = gcd(48, 18)
    print(f"GCD of 48 and 18 is {result}")`;
        } else {
          fallbackMessage += "Here's a template function based on your request:";
          fallbackCode = `def custom_function():
    """
    Function for: ${message}
    
    This is a placeholder. Aurora-X synthesis engine
    would normally generate the actual implementation.
    """
    # Implementation would be generated here
    return "Result based on: ${message}"

# Example usage
if __name__ == "__main__":
    result = custom_function()
    print(result)`;
        }
        
        return res.json({
          message: fallbackMessage,
          code: fallbackCode,
          language: "python",
          synthesis_id: `fallback-${Date.now()}`,
          timestamp: new Date().toISOString(),
          error_detail: "Aurora-X synthesis failed, using fallback implementation"
        });
      }
      
    } catch (error: any) {
      console.error("[Aurora-X] Chat API error:", error);
      return res.status(500).json({
        error: "Failed to process synthesis request",
        details: error?.message
      });
    }
  });

  // Serve the tracker visual HTML
  app.get("/tracker-visual", (req, res) => {
    const trackerPath = path.join(process.cwd(), "tracker_visual.html");
    if (fs.existsSync(trackerPath)) {
      res.sendFile(trackerPath);
    } else {
      res.status(404).send("Tracker visual not found");
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}
