import { Router, Request, Response } from 'express';
import AuroraCore from './aurora-core';
import { getAuroraAI } from './aurora';

const aurora = AuroraCore.getInstance();
const auroraAI = getAuroraAI();

export const mcpRouter = Router();

// MCP Server Info endpoint
mcpRouter.get('/info', (_req: Request, res: Response) => {
  res.json({
    name: "Aurora-X Ultra MCP Server",
    version: "1.0.0",
    description: "MCP server for Aurora-X Ultra AI-powered code synthesis platform",
    capabilities: [
      "chat",
      "code_synthesis", 
      "code_analysis",
      "code_fix",
      "aurora_status"
    ],
    tools: [
      {
        name: "aurora_chat",
        description: "Chat with Aurora AI - ask questions, request code, get explanations",
        inputSchema: {
          type: "object",
          properties: {
            message: { type: "string", description: "Your message to Aurora" }
          },
          required: ["message"]
        }
      },
      {
        name: "aurora_synthesize",
        description: "Generate code based on a specification",
        inputSchema: {
          type: "object",
          properties: {
            spec: { type: "string", description: "Code specification or requirements" },
            language: { type: "string", description: "Target programming language" }
          },
          required: ["spec"]
        }
      },
      {
        name: "aurora_analyze",
        description: "Analyze code or text input",
        inputSchema: {
          type: "object",
          properties: {
            input: { type: "string", description: "Code or text to analyze" },
            context: { type: "string", description: "Additional context" }
          },
          required: ["input"]
        }
      },
      {
        name: "aurora_fix",
        description: "Fix code issues",
        inputSchema: {
          type: "object",
          properties: {
            code: { type: "string", description: "Code to fix" },
            issue: { type: "string", description: "Description of the issue" }
          },
          required: ["code", "issue"]
        }
      },
      {
        name: "aurora_status",
        description: "Get Aurora system status including tiers, workers, and capabilities",
        inputSchema: {
          type: "object",
          properties: {}
        }
      }
    ]
  });
});

// MCP Tools List endpoint
mcpRouter.get('/tools', (_req: Request, res: Response) => {
  res.json({
    tools: [
      {
        name: "aurora_chat",
        description: "Chat with Aurora AI - 188 intelligence tiers, 66 execution methods",
        inputSchema: {
          type: "object",
          properties: {
            message: { type: "string", description: "Your message to Aurora" }
          },
          required: ["message"]
        }
      },
      {
        name: "aurora_synthesize",
        description: "Generate code using Aurora's hyperspeed synthesis engine",
        inputSchema: {
          type: "object",
          properties: {
            spec: { type: "string", description: "What code to generate" },
            language: { type: "string", description: "Programming language", default: "typescript" }
          },
          required: ["spec"]
        }
      },
      {
        name: "aurora_analyze",
        description: "Analyze code with Aurora's 188 grandmaster tiers",
        inputSchema: {
          type: "object",
          properties: {
            input: { type: "string", description: "Code or text to analyze" },
            context: { type: "string", description: "Additional context" }
          },
          required: ["input"]
        }
      },
      {
        name: "aurora_fix",
        description: "Fix code using Aurora's 300 autonomous workers",
        inputSchema: {
          type: "object",
          properties: {
            code: { type: "string", description: "Code with issues" },
            issue: { type: "string", description: "What's wrong" }
          },
          required: ["code", "issue"]
        }
      },
      {
        name: "aurora_status",
        description: "Get full Aurora system status",
        inputSchema: { type: "object", properties: {} }
      }
    ]
  });
});

// MCP Tool Execution endpoint
mcpRouter.post('/execute', async (req: Request, res: Response) => {
  try {
    const { tool, arguments: args } = req.body;

    if (!tool) {
      return res.status(400).json({ error: "Missing 'tool' field" });
    }

    let result: any;

    switch (tool) {
      case 'aurora_chat':
        if (!args?.message) {
          return res.status(400).json({ error: "Missing 'message' argument" });
        }
        result = await auroraAI.handleChat(args.message);
        break;

      case 'aurora_synthesize':
        if (!args?.spec) {
          return res.status(400).json({ error: "Missing 'spec' argument" });
        }
        result = await auroraAI.synthesize(args.spec);
        break;

      case 'aurora_analyze':
        if (!args?.input) {
          return res.status(400).json({ error: "Missing 'input' argument" });
        }
        result = await aurora.analyze(args.input, args.context);
        break;

      case 'aurora_fix':
        if (!args?.code || !args?.issue) {
          return res.status(400).json({ error: "Missing 'code' or 'issue' argument" });
        }
        result = await aurora.fix(args.code, args.issue);
        break;

      case 'aurora_status':
        result = aurora.getStatus();
        break;

      default:
        return res.status(400).json({ error: `Unknown tool: ${tool}` });
    }

    res.json({
      success: true,
      tool,
      result,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('[MCP] Execution error:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Execution failed'
    });
  }
});

// Health check
mcpRouter.get('/health', (_req: Request, res: Response) => {
  res.json({ status: 'ok', server: 'Aurora MCP Server' });
});

export default mcpRouter;
