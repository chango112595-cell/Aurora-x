import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { corpusStorage } from "./corpus-storage";
import { progressStore } from "./progress-store";
import { createWebSocketServer, type SynthesisWebSocketServer } from "./websocket-server";
import * as path from "path";
import * as fs from "fs";
import { spawn, execFile } from "child_process";
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
const AURORA_HEALTH_TOKEN = process.env.AURORA_HEALTH_TOKEN || "ok";
const BRIDGE_URL = process.env.AURORA_BRIDGE_URL || "http://0.0.0.0:5001";
const AURORA_REPO = process.env.AURORA_REPO || "chango112595-cell/Aurora-x";
const TARGET_BRANCH = process.env.AURORA_TARGET_BRANCH || "main";
const AURORA_GH_TOKEN = process.env.AURORA_GH_TOKEN;
const GH_API = "https://api.github.com";
let wsServer: SynthesisWebSocketServer | null = null;
let serverStartTime: number = Date.now();

// GitHub API helper function
function getGitHubHeaders() {
  if (!AURORA_GH_TOKEN) {
    throw new Error("Missing AURORA_GH_TOKEN environment variable");
  }
  return {
    "Authorization": `token ${AURORA_GH_TOKEN}`,
    "Accept": "application/vnd.github+json"
  };
}

/**
 * Helper function to refresh README badges after progress updates
 * Runs asynchronously to avoid blocking the API response
 * 
 * This function:
 * 1. Runs the Python script at tools/patch_readme_progress.py to update README badges
 * 2. Optionally commits and pushes changes to git if AURORA_AUTO_GIT is set
 */
async function refreshReadmeBadges(): Promise<void> {
  try {
    // Check if the Python script exists
    const scriptPath = path.join(process.cwd(), 'tools', 'patch_readme_progress.py');
    if (!fs.existsSync(scriptPath)) {
      // Script doesn't exist, log but don't fail
      console.log('[Badge Refresh] Python script not found at tools/patch_readme_progress.py - skipping badge refresh');
      return;
    }

    // Run the Python script to update badges
    await new Promise<void>((resolve, reject) => {
      execFile('python3', [scriptPath], {
        cwd: process.cwd(),
        timeout: 10000, // 10 second timeout
        maxBuffer: 1024 * 1024, // 1MB buffer
      }, (error, stdout, stderr) => {
        if (error) {
          console.error('[Badge Refresh] Error running patch_readme_progress.py:', error.message);
          // Don't reject, just log and continue
          resolve();
          return;
        }

        if (stderr && !stderr.includes('[OK]')) {
          console.error('[Badge Refresh] Script stderr:', stderr);
        }

        if (stdout && stdout.includes('[OK]')) {
          console.log('[Badge Refresh] README badges updated successfully');
        }

        resolve();
      });
    });

    // Check if auto-git is enabled
    const autoGit = process.env.AURORA_AUTO_GIT;
    const shouldAutoCommit = autoGit && ['1', 'true', 'yes', 'on'].includes(autoGit.toLowerCase());

    if (shouldAutoCommit) {
      // Run git operations
      console.log('[Badge Refresh] Auto-git enabled, committing and pushing changes...');

      // Add specific files
      const filesToAdd = [
        'progress.json',
        'MASTER_TASK_LIST.md',
        'progress_export.csv',
        'README.md'
      ];

      // Check which files exist and add them
      const existingFiles = filesToAdd.filter(file => 
        fs.existsSync(path.join(process.cwd(), file))
      );

      if (existingFiles.length === 0) {
        console.log('[Badge Refresh] No files to commit');
        return;
      }

      // Add files to git
      await new Promise<void>((resolve) => {
        execFile('git', ['add', ...existingFiles], {
          cwd: process.cwd(),
          timeout: 5000,
        }, (error, stdout, stderr) => {
          if (error) {
            console.error('[Badge Refresh] Error adding files to git:', error.message);
            resolve();
            return;
          }
          console.log('[Badge Refresh] Added files to git:', existingFiles.join(', '));
          resolve();
        });
      });

      // Create commit
      await new Promise<void>((resolve) => {
        execFile('git', ['commit', '-m', 'chore(progress): bump via /api and refresh badges'], {
          cwd: process.cwd(),
          timeout: 5000,
        }, (error, stdout, stderr) => {
          if (error) {
            // Check if it's just "nothing to commit" which is not really an error
            if (error.message.includes('nothing to commit')) {
              console.log('[Badge Refresh] Nothing to commit, working tree clean');
            } else {
              console.error('[Badge Refresh] Error creating commit:', error.message);
            }
            resolve();
            return;
          }
          console.log('[Badge Refresh] Created commit successfully');
          resolve();
        });
      });

      // Push to remote
      await new Promise<void>((resolve) => {
        execFile('git', ['push'], {
          cwd: process.cwd(),
          timeout: 15000, // Give push more time
        }, (error, stdout, stderr) => {
          if (error) {
            console.error('[Badge Refresh] Error pushing to remote:', error.message);
            resolve();
            return;
          }
          console.log('[Badge Refresh] Pushed changes to remote repository');
          resolve();
        });
      });
    }
  } catch (error: any) {
    // Log error but don't throw - this is a non-critical operation
    console.error('[Badge Refresh] Unexpected error:', error.message || error);
  }
}

export async function registerRoutes(app: Express): Promise<Server> {
  // Simple health check endpoint for container health checks
  app.get("/api/health", (req, res) => {
    res.status(200).json({ 
      status: "ok",
      service: "chango",
      uptime: Math.floor((Date.now() - serverStartTime) / 1000)
    });
  });

  // PWA endpoints
  app.get("/manifest.webmanifest", (req, res) => {
    const manifestPath = path.join(process.cwd(), 'frontend', 'pwa', 'manifest.webmanifest');

    // Check if the file exists
    if (!fs.existsSync(manifestPath)) {
      console.error('[PWA] Manifest file not found at:', manifestPath);
      return res.status(404).json({
        ok: false,
        err: "manifest missing"
      });
    }

    // Set the correct MIME type for PWA manifest
    res.setHeader('Content-Type', 'application/manifest+json');
    res.setHeader('Cache-Control', 'public, max-age=3600'); // Cache for 1 hour

    // Send the manifest file
    res.sendFile(manifestPath);
  });

  app.get("/service-worker.js", (req, res) => {
    const swPath = path.join(process.cwd(), 'frontend', 'pwa', 'service-worker.js');

    // Check if the file exists
    if (!fs.existsSync(swPath)) {
      console.error('[PWA] Service worker file not found at:', swPath);
      return res.status(404).json({
        ok: false,
        err: "sw missing"
      });
    }

    // Set the correct MIME type for JavaScript
    res.setHeader('Content-Type', 'application/javascript');
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate'); // Don't cache service worker
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');

    // Send the service worker file
    res.sendFile(swPath);
  });

  // Aurora-X Universal Code Synthesis endpoints
  app.post("/api/nl/compile_full", (req, res) => {
    try {
      const { prompt } = req.body;

      // Validate input
      if (!prompt || typeof prompt !== 'string' || prompt.trim().length === 0) {
        return res.status(400).json({
          status: "error",
          error: "Invalid request",
          message: "prompt is required and must be a non-empty string"
        });
      }

      // Limit prompt length for safety
      if (prompt.length > 5000) {
        return res.status(400).json({
          status: "error",
          error: "Prompt too long",
          message: "Prompt must be less than 5000 characters"
        });
      }

      // Generate run ID
      const runId = `run-${new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)}`;

      console.log(`[Synthesis] Starting synthesis for run ${runId}: "${prompt.substring(0, 100)}..."`);

      // Execute Python synthesis engine
      const pythonScript = `
import json
import sys
import os
from aurora_x.synthesis.universal_engine import synthesize_universal_sync

# Redirect print output to stderr to keep stdout clean for JSON
class StderrRedirect:
    def write(self, text):
        sys.stderr.write(text)
    def flush(self):
        sys.stderr.flush()

try:
    prompt = ${JSON.stringify(prompt)}
    run_id = ${JSON.stringify(runId)}

    # Temporarily redirect stdout to stderr for status messages
    old_stdout = sys.stdout
    sys.stdout = StderrRedirect()

    # Call the synthesis engine
    result = synthesize_universal_sync(prompt, run_id=run_id)

    # Restore stdout and output JSON result
    sys.stdout = old_stdout

    # Output only the JSON to stdout
    print(json.dumps(result))
    sys.exit(0)
except Exception as e:
    # Restore stdout in case of error
    sys.stdout = sys.__stdout__
    error_result = {
        "status": "error",
        "error": str(e),
        "run_id": run_id,
        "files": [],
        "project_type": "unknown"
    }
    print(json.dumps(error_result))
    sys.exit(1)
`;

      // Execute the Python script
      execFile('python3', ['-c', pythonScript], {
        cwd: process.cwd(),
        timeout: 60000, // 60 second timeout for synthesis
        maxBuffer: 10 * 1024 * 1024, // 10MB buffer
      }, (error, stdout, stderr) => {
        if (error && !stdout) {
          console.error(`[Synthesis] Error executing synthesis: ${error.message}`);
          console.error(`[Synthesis] stderr: ${stderr}`);
          return res.status(500).json({
            status: "error",
            error: "Synthesis failed",
            message: error.message,
            details: stderr,
            run_id: runId
          });
        }

        // Log status messages from stderr (if any)
        if (stderr) {
          console.log(`[Synthesis] Status messages: ${stderr}`);
        }

        try {
          // Parse the JSON result from stdout - try to extract JSON if mixed with other text
          let jsonStr = stdout.trim();

          // If stdout contains multiple lines, try to find the JSON line
          const lines = jsonStr.split('\n');
          for (let i = lines.length - 1; i >= 0; i--) {
            const line = lines[i].trim();
            if (line.startsWith('{') && line.endsWith('}')) {
              jsonStr = line;
              break;
            }
          }

          const result = JSON.parse(jsonStr);

          // Log successful synthesis
          console.log(`[Synthesis] Successfully completed synthesis for run ${runId}`);
          console.log(`[Synthesis] Project type: ${result.project_type}, Files: ${result.files?.length || 0}`);

          // Add download URL to the result
          if (result.status === "success" && result.run_id) {
            result.download_url = `/api/projects/${result.run_id}/download`;
          }

          return res.json(result);
        } catch (parseError: any) {
          console.error(`[Synthesis] Error parsing synthesis result: ${parseError.message}`);
          console.error(`[Synthesis] stdout: ${stdout}`);
          console.error(`[Synthesis] stderr: ${stderr}`);

          return res.status(500).json({
            status: "error",
            error: "Failed to parse synthesis result",
            message: parseError.message,
            run_id: runId,
            stdout: stdout.substring(0, 1000), // Include first 1000 chars for debugging
            stderr: stderr.substring(0, 1000)
          });
        }
      });
    } catch (error: any) {
      console.error(`[Synthesis] Unexpected error: ${error.message}`);
      return res.status(500).json({
        status: "error",
        error: "Internal server error",
        message: error.message
      });
    }
  });

  // Endpoint to download project ZIP files
  app.get("/api/projects/:runId/download", (req, res) => {
    try {
      const { runId } = req.params;

      // Validate run ID format (should be like run-2025-10-12T15-20-07)
      // Also support older format run-20241012-143539
      if (!runId || !runId.match(/^run-(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}|\d{8}-\d{6})$/)) {
        return res.status(400).json({
          error: "Invalid run ID",
          message: "Run ID must be in format run-YYYY-MM-DDTHH-MM-SS or run-YYYYMMDD-HHMMSS"
        });
      }

      // Construct path to the project.zip file
      const zipPath = path.join(process.cwd(), 'runs', runId, 'project.zip');

      // Check if the file exists
      if (!fs.existsSync(zipPath)) {
        console.error(`[Download] ZIP file not found at: ${zipPath}`);
        return res.status(404).json({
          error: "Project not found",
          message: `No project found for run ID: ${runId}`
        });
      }

      // Get file stats for size
      const stats = fs.statSync(zipPath);

      console.log(`[Download] Serving ZIP file for run ${runId}, size: ${stats.size} bytes`);

      // Set appropriate headers for file download
      res.setHeader('Content-Type', 'application/zip');
      res.setHeader('Content-Disposition', `attachment; filename="${runId}.zip"`);
      res.setHeader('Content-Length', stats.size.toString());
      res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
      res.setHeader('Pragma', 'no-cache');
      res.setHeader('Expires', '0');

      // Stream the file to the response
      const fileStream = fs.createReadStream(zipPath);

      fileStream.on('error', (streamError) => {
        console.error(`[Download] Error streaming file: ${streamError.message}`);
        if (!res.headersSent) {
          res.status(500).json({
            error: "Download failed",
            message: "Failed to stream the project file"
          });
        }
      });

      fileStream.pipe(res);

      fileStream.on('end', () => {
        console.log(`[Download] Successfully sent ZIP file for run ${runId}`);
      });

    } catch (error: any) {
      console.error(`[Download] Unexpected error: ${error.message}`);
      return res.status(500).json({
        error: "Internal server error",
        message: error.message
      });
    }
  });

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

  // Progress endpoint to serve progress.json data
  app.get("/api/progress", (req, res) => {
    try {
      // Read the progress.json file from the root directory
      const progressPath = path.join(process.cwd(), 'progress.json');

      // Check if the file exists
      if (!fs.existsSync(progressPath)) {
        return res.status(404).json({
          error: "Progress data not found",
          message: "The progress.json file does not exist"
        });
      }

      // Read the file content
      const progressData = fs.readFileSync(progressPath, 'utf-8');

      // Parse the JSON data
      const progressJson = JSON.parse(progressData);

      // Calculate overall percentage
      const tasks = progressJson.tasks || [];
      let totalPercent = 0;
      tasks.forEach((task: any) => {
        let percent = task.percent || 0;
        if (typeof percent === 'string') {
          percent = parseFloat(percent.replace('%', ''));
        }
        totalPercent += percent;
      });
      const overall_percent = Math.round((totalPercent / Math.max(tasks.length, 1)) * 100) / 100;

      // Add calculated fields
      progressJson.overall_percent = overall_percent;
      progressJson.ok = true;

      // Ensure ui_thresholds exist with defaults
      const th = progressJson.ui_thresholds || {};
      progressJson.ui_thresholds = {
        ok: typeof th.ok === 'number' ? th.ok : 90,
        warn: typeof th.warn === 'number' ? th.warn : 60
      };

      // Set CORS headers for cross-origin access
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
      res.setHeader('Access-Control-Max-Age', '86400'); // 24 hours

      // Return the progress data with aggressive caching
      res.setHeader('Content-Type', 'application/json');
      res.setHeader('Cache-Control', 'public, max-age=5, stale-while-revalidate=10'); // Cache for 5s, allow stale for 10s
      res.setHeader('ETag', `"${Date.now()}"`); // Add ETag for conditional requests
      return res.json(progressJson);

    } catch (error: any) {
      // Handle JSON parsing errors or other read errors
      console.error('[Progress API] Error reading or parsing progress.json:', error);

      // Return appropriate error response
      if (error.code === 'ENOENT') {
        return res.status(404).json({
          error: "Progress data not found",
          message: "The progress.json file does not exist"
        });
      } else if (error instanceof SyntaxError) {
        return res.status(500).json({
          error: "Invalid progress data",
          message: "The progress.json file contains invalid JSON"
        });
      } else {
        return res.status(500).json({
          error: "Internal server error",
          message: "Failed to read progress data",
          details: error?.message ?? String(error)
        });
      }
    }
  });

  // Handle OPTIONS preflight requests for CORS
  app.options("/api/progress", (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Access-Control-Max-Age', '86400');
    res.sendStatus(204); // No content for OPTIONS
  });

  // POST endpoint to update task percentage
  app.post("/api/progress/task_percent", (req, res) => {
    try {
      const { task_id, percentage } = req.body;

      // Validate inputs
      if (!task_id || typeof task_id !== 'string') {
        return res.status(400).json({
          error: "Invalid request",
          message: "task_id is required and must be a string"
        });
      }

      if (percentage === undefined || percentage === null || typeof percentage !== 'number') {
        return res.status(400).json({
          error: "Invalid request", 
          message: "percentage is required and must be a number"
        });
      }

      if (percentage < 0 || percentage > 100) {
        return res.status(400).json({
          error: "Invalid percentage",
          message: "Percentage must be between 0 and 100"
        });
      }

      // Read the progress.json file
      const progressPath = path.join(process.cwd(), 'progress.json');

      if (!fs.existsSync(progressPath)) {
        return res.status(404).json({
          error: "Progress data not found",
          message: "The progress.json file does not exist"
        });
      }

      // Parse the current data
      const progressData = fs.readFileSync(progressPath, 'utf-8');
      const progressJson = JSON.parse(progressData);

      // Find the task to update
      const tasks = progressJson.tasks || [];
      const taskIndex = tasks.findIndex((t: any) => t.id === task_id);

      if (taskIndex === -1) {
        return res.status(404).json({
          error: "Task not found",
          message: `No task found with ID: ${task_id}`
        });
      }

      // Update the task
      const task = tasks[taskIndex];
      const oldPercent = task.percent;
      const oldStatus = task.status;

      task.percent = percentage;

      // Auto-update status based on percentage
      if (percentage === 100) {
        task.status = "complete";
      } else if (percentage > 0) {
        if (oldStatus === "not-started" || oldStatus === "pending") {
          task.status = "in-progress";
        }
        // Keep existing in-progress or in-development status
      } else {
        // 0% means not started
        task.status = "not-started";
      }

      // Update the updated_utc timestamp
      progressJson.updated_utc = new Date().toISOString();

      // Write back to file
      fs.writeFileSync(progressPath, JSON.stringify(progressJson, null, 2));

      console.log(`[Progress Update] Task ${task_id}: ${oldPercent}% → ${percentage}% (status: ${oldStatus} → ${task.status})`);

      // Asynchronously refresh README badges after successful update
      // This runs in the background and doesn't block the API response
      refreshReadmeBadges().catch((error) => {
        console.error('[Progress Update] Badge refresh failed:', error);
        // Don't throw - let the API response succeed even if badge refresh fails
      });

      // Calculate new overall percentage
      let totalPercent = 0;
      tasks.forEach((t: any) => {
        let percent = t.percent || 0;
        if (typeof percent === 'string') {
          percent = parseFloat(percent.replace('%', ''));
        }
        totalPercent += percent;
      });
      const overall_percent = Math.round((totalPercent / Math.max(tasks.length, 1)) * 100) / 100;

      // Set CORS headers for cross-origin access
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

      // Return success response with updated data
      return res.json({
        success: true,
        task_id: task_id,
        old_percentage: oldPercent,
        new_percentage: percentage,
        old_status: oldStatus,
        new_status: task.status,
        overall_percent: overall_percent,
        updated_utc: progressJson.updated_utc,
        message: `Successfully updated task ${task_id} to ${percentage}%`
      });

    } catch (error: any) {
      console.error('[Progress Update API] Error updating task percentage:', error);

      if (error instanceof SyntaxError) {
        return res.status(500).json({
          error: "Invalid progress data",
          message: "The progress.json file contains invalid JSON"
        });
      } else {
        return res.status(500).json({
          error: "Internal server error",
          message: "Failed to update task percentage",
          details: error?.message ?? String(error)
        });
      }
    }
  });

  // Handle OPTIONS preflight requests for task_percent endpoint
  app.options("/api/progress/task_percent", (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Access-Control-Max-Age', '86400');
    res.sendStatus(204); // No content for OPTIONS
  });

  // POST endpoint to recompute progress data, regenerate task lists and badges
  app.post("/api/progress/recompute", async (req, res) => {
    // Track operation results
    let timestampUpdated = false;
    let taskListRegenerated = false;
    let badgesRefreshed = false;
    let gitOperations = false;
    let updatedTimestamp: string | undefined;
    let errors: string[] = [];
    let hasAnySuccess = false;

    try {
      console.log('[Progress Recompute] Starting progress recomputation...');

      // Step 1: Update the timestamp in progress.json (CRITICAL - fail fast if this fails)
      const progressPath = path.join(process.cwd(), 'progress.json');

      if (!fs.existsSync(progressPath)) {
        // Set CORS headers
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

        return res.status(404).json({
          error: "Progress data not found",
          message: "The progress.json file does not exist",
          operations_performed: {
            timestamp_updated: false,
            task_list_regenerated: false,
            badges_refreshed: false,
            git_operations: false
          }
        });
      }

      try {
        // Read and update the progress.json file
        const progressData = fs.readFileSync(progressPath, 'utf-8');
        const progressJson = JSON.parse(progressData);
        updatedTimestamp = new Date().toISOString();
        progressJson.updated_utc = updatedTimestamp;

        // Write the updated timestamp back to file
        fs.writeFileSync(progressPath, JSON.stringify(progressJson, null, 2));
        timestampUpdated = true;
        hasAnySuccess = true;
        console.log('[Progress Recompute] Updated timestamp in progress.json to:', updatedTimestamp);
      } catch (timestampError: any) {
        console.error('[Progress Recompute] Failed to update timestamp:', timestampError);
        errors.push(`Timestamp update failed: ${timestampError.message}`);

        // This is a critical error - fail fast
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

        return res.status(500).json({
          error: "Critical operation failed",
          message: "Failed to update progress.json timestamp",
          details: timestampError.message,
          operations_performed: {
            timestamp_updated: false,
            task_list_regenerated: false,
            badges_refreshed: false,
            git_operations: false
          }
        });
      }

      // Step 2: Run update_progress.py to regenerate MASTER_TASK_LIST.md and progress_export.csv
      const updateProgressScriptPath = path.join(process.cwd(), 'tools', 'update_progress.py');

      if (fs.existsSync(updateProgressScriptPath)) {
        console.log('[Progress Recompute] Running update_progress.py...');

        try {
          await new Promise<void>((resolve, reject) => {
            execFile('python3', [updateProgressScriptPath], {
              cwd: process.cwd(),
              timeout: 30000, // 30 second timeout
              maxBuffer: 1024 * 1024 * 5, // 5MB buffer
            }, (error, stdout, stderr) => {
              if (error) {
                // Check exit code - non-zero means failure
                if (error.code && error.code !== 0) {
                  console.error('[Progress Recompute] update_progress.py failed with exit code:', error.code);
                  console.error('[Progress Recompute] Error:', error.message);
                  if (stderr) console.error('[Progress Recompute] stderr:', stderr);
                  reject(new Error(`update_progress.py failed with exit code ${error.code}: ${error.message}`));
                  return;
                }
                // If error but no exit code, still treat as failure
                console.error('[Progress Recompute] Error running update_progress.py:', error.message);
                reject(error);
                return;
              }

              // Check for error indicators in stderr (excluding [OK])
              if (stderr && !stderr.includes('[OK]') && stderr.trim() !== '') {
                console.error('[Progress Recompute] update_progress.py stderr:', stderr);
                // Don't fail on stderr warnings, only if there was an actual error
              }

              if (stdout) {
                console.log('[Progress Recompute] update_progress.py output:', stdout);
              }

              console.log('[Progress Recompute] Successfully ran update_progress.py');
              resolve();
            });
          });
          taskListRegenerated = true;
          hasAnySuccess = true;
        } catch (scriptError: any) {
          console.error('[Progress Recompute] Failed to regenerate task list:', scriptError);
          errors.push(`Task list regeneration failed: ${scriptError.message}`);
          // Continue with other operations
        }
      } else {
        console.log('[Progress Recompute] update_progress.py not found - skipping task list generation');
        // File doesn't exist, so we didn't run it, don't mark as success
      }

      // Step 3: Run patch_readme_progress.py to refresh README badges
      const patchReadmeScriptPath = path.join(process.cwd(), 'tools', 'patch_readme_progress.py');

      if (fs.existsSync(patchReadmeScriptPath)) {
        console.log('[Progress Recompute] Running patch_readme_progress.py...');

        try {
          await new Promise<void>((resolve, reject) => {
            execFile('python3', [patchReadmeScriptPath], {
              cwd: process.cwd(),
              timeout: 10000, // 10 second timeout
              maxBuffer: 1024 * 1024, // 1MB buffer
            }, (error, stdout, stderr) => {
              if (error) {
                // Check exit code - non-zero means failure
                if (error.code && error.code !== 0) {
                  console.error('[Progress Recompute] patch_readme_progress.py failed with exit code:', error.code);
                  console.error('[Progress Recompute] Error:', error.message);
                  if (stderr) console.error('[Progress Recompute] stderr:', stderr);
                  reject(new Error(`patch_readme_progress.py failed with exit code ${error.code}: ${error.message}`));
                  return;
                }
                // If error but no exit code, still treat as failure
                console.error('[Progress Recompute] Error running patch_readme_progress.py:', error.message);
                reject(error);
                return;
              }

              // Check for error indicators in stderr (excluding [OK])
              if (stderr && !stderr.includes('[OK]') && stderr.trim() !== '') {
                console.error('[Progress Recompute] patch_readme_progress.py stderr:', stderr);
                // Don't fail on stderr warnings
              }

              if (stdout && stdout.includes('[OK]')) {
                console.log('[Progress Recompute] README badges updated successfully');
              }

              resolve();
            });
          });
          badgesRefreshed = true;
          hasAnySuccess = true;
        } catch (badgeError: any) {
          console.error('[Progress Recompute] Failed to refresh badges:', badgeError);
          errors.push(`Badge refresh failed: ${badgeError.message}`);
          // Continue with other operations
        }
      } else {
        console.log('[Progress Recompute] patch_readme_progress.py not found - skipping badge refresh');
        // File doesn't exist, so we didn't run it, don't mark as success
      }

      // Step 4: Optionally commit and push changes if AURORA_AUTO_GIT is enabled
      const autoGit = process.env.AURORA_AUTO_GIT;
      const shouldAutoCommit = autoGit && ['1', 'true', 'yes', 'on'].includes(autoGit.toLowerCase());

      if (shouldAutoCommit) {
        console.log('[Progress Recompute] Auto-git enabled, committing and pushing changes...');

        // Add specific files
        const filesToAdd = [
          'progress.json',
          'MASTER_TASK_LIST.md', 
          'progress_export.csv',
          'README.md'
        ];

        // Check which files exist and add them
        const existingFiles = filesToAdd.filter(file => 
          fs.existsSync(path.join(process.cwd(), file))
        );

        if (existingFiles.length > 0) {
          let gitAddSuccess = false;
          let gitCommitSuccess = false;
          let gitPushSuccess = false;

          // Add files to git
          try {
            await new Promise<void>((resolve, reject) => {
              execFile('git', ['add', ...existingFiles], {
                cwd: process.cwd(),
                timeout: 5000,
              }, (error, stdout, stderr) => {
                if (error) {
                  console.error('[Progress Recompute] Error adding files to git:', error.message);
                  reject(new Error(`Git add failed: ${error.message}`));
                  return;
                }
                console.log('[Progress Recompute] Added files to git:', existingFiles.join(', '));
                resolve();
              });
            });
            gitAddSuccess = true;
          } catch (gitError: any) {
            console.error('[Progress Recompute] Git add operation failed:', gitError);
            errors.push(`Git add failed: ${gitError.message}`);
          }

          // Create commit (only if add succeeded)
          if (gitAddSuccess) {
            try {
              await new Promise<void>((resolve, reject) => {
                execFile('git', ['commit', '-m', 'chore(progress): recompute via API'], {
                  cwd: process.cwd(),
                  timeout: 5000,
                }, (error, stdout, stderr) => {
                  if (error) {
                    // Check if it's just "nothing to commit" which is not really an error
                    if (error.message.includes('nothing to commit')) {
                      console.log('[Progress Recompute] Nothing to commit, working tree clean');
                      resolve();  // This is OK, not an error
                    } else {
                      console.error('[Progress Recompute] Error creating commit:', error.message);
                      reject(new Error(`Git commit failed: ${error.message}`));
                    }
                    return;
                  }
                  console.log('[Progress Recompute] Created commit successfully');
                  resolve();
                });
              });
              gitCommitSuccess = true;
            } catch (gitError: any) {
              console.error('[Progress Recompute] Git commit operation failed:', gitError);
              errors.push(`Git commit failed: ${gitError.message}`);
            }
          }

          // Push to remote (only if commit succeeded)
          if (gitCommitSuccess) {
            try {
              await new Promise<void>((resolve, reject) => {
                execFile('git', ['push'], {
                  cwd: process.cwd(),
                  timeout: 15000, // Give push more time
                }, (error, stdout, stderr) => {
                  if (error) {
                    console.error('[Progress Recompute] Error pushing to remote:', error.message);
                    reject(new Error(`Git push failed: ${error.message}`));
                    return;
                  }
                  console.log('[Progress Recompute] Pushed changes to remote repository');
                  resolve();
                });
              });
              gitPushSuccess = true;
            } catch (gitError: any) {
              console.error('[Progress Recompute] Git push operation failed:', gitError);
              errors.push(`Git push failed: ${gitError.message}`);
            }
          }

          // Git operations succeeded if all attempted operations succeeded
          gitOperations = gitAddSuccess && gitCommitSuccess && gitPushSuccess;
          if (gitOperations) {
            hasAnySuccess = true;
          }
        } else {
          console.log('[Progress Recompute] No files to commit');
          // No files to commit, not a failure
        }
      } else {
        console.log('[Progress Recompute] Auto-git disabled, skipping commit and push');
        // Git was disabled, not a failure
      }

      // Set CORS headers for cross-origin access
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

      // Determine response status based on results
      const allCriticalSucceeded = timestampUpdated;
      const anyOperationFailed = errors.length > 0;

      // If we have any errors but also some successes, it's a partial success
      if (anyOperationFailed && hasAnySuccess) {
        // Partial success - some operations succeeded, some failed
        return res.status(207).json({  // 207 Multi-Status for partial success
          success: false,
          partial_success: true,
          message: "Progress data partially recomputed - some operations failed",
          updated_utc: updatedTimestamp,
          operations_performed: {
            timestamp_updated: timestampUpdated,
            task_list_regenerated: taskListRegenerated,
            badges_refreshed: badgesRefreshed,
            git_operations: gitOperations
          },
          errors: errors
        });
      } else if (anyOperationFailed) {
        // Complete failure
        return res.status(500).json({
          success: false,
          error: "Operation failed",
          message: "Failed to recompute progress data",
          operations_performed: {
            timestamp_updated: timestampUpdated,
            task_list_regenerated: taskListRegenerated,
            badges_refreshed: badgesRefreshed,
            git_operations: gitOperations
          },
          errors: errors
        });
      } else {
        // Complete success
        return res.json({
          success: true,
          message: "Progress data recomputed successfully",
          updated_utc: updatedTimestamp,
          operations_performed: {
            timestamp_updated: timestampUpdated,
            task_list_regenerated: taskListRegenerated,
            badges_refreshed: badgesRefreshed,
            git_operations: shouldAutoCommit ? gitOperations : false
          }
        });
      }

    } catch (error: any) {
      console.error('[Progress Recompute] Unexpected error:', error);

      // Set CORS headers even on error
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

      // Return error response with operation status
      if (error instanceof SyntaxError) {
        return res.status(500).json({
          error: "Invalid progress data",
          message: "The progress.json file contains invalid JSON",
          operations_performed: {
            timestamp_updated: timestampUpdated,
            task_list_regenerated: taskListRegenerated,
            badges_refreshed: badgesRefreshed,
            git_operations: gitOperations
          },
          errors: [...errors, error.message]
        });
      } else {
        return res.status(500).json({
          error: "Internal server error",
          message: "Failed to recompute progress data",
          operations_performed: {
            timestamp_updated: timestampUpdated,
            task_list_regenerated: taskListRegenerated,
            badges_refreshed: badgesRefreshed,
            git_operations: gitOperations
          },
          errors: [...errors, error?.message ?? String(error)]
        });
      }
    }
  });

  // Handle OPTIONS preflight requests for recompute endpoint
  app.options("/api/progress/recompute", (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Access-Control-Max-Age', '86400');
    res.sendStatus(204); // No content for OPTIONS
  });

  // Simple health check endpoint
  app.get("/api/health", async (_req, res) => {
    res.json({ status: "ok", timestamp: new Date().toISOString() });
  });

  // System diagnostics endpoint
  app.get("/api/diagnostics", async (_req, res) => {
    try {
      const diagnostics: any = {
        status: "ok",
        timestamp: new Date().toISOString(),
        services: {}
      };

      // Check database
      try {
        const recentItems = await corpusStorage.getRecent(1);
        diagnostics.services.database = "connected";
        diagnostics.corpus_count = recentItems.length;
      } catch (e) {
        diagnostics.services.database = "error";
        diagnostics.status = "degraded";
      }

      // Check WebSocket
      diagnostics.services.websocket = wsServer ? "active" : "inactive";

      // Check Bridge
      try {
        const bridgeRes = await fetch("http://0.0.0.0:5001/healthz", { signal: AbortSignal.timeout(2000) });
        diagnostics.services.bridge = bridgeRes.ok ? "connected" : "error";
      } catch (e) {
        diagnostics.services.bridge = "unreachable";
      }

      // Check progress system
      try {
        const progressPath = path.join(process.cwd(), 'progress.json');
        if (fs.existsSync(progressPath)) {
          const progressData = JSON.parse(fs.readFileSync(progressPath, 'utf-8'));
          diagnostics.services.progress = "ok";
          diagnostics.progress_tasks = progressData.tasks?.length || 0;
        } else {
          diagnostics.services.progress = "missing";
        }
      } catch (e) {
        diagnostics.services.progress = "error";
      }

      res.json(diagnostics);
    } catch (error: any) {
      res.status(500).json({
        status: "error",
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
  });

  // Health check endpoint for auto-updater monitoring
  app.get("/healthz", async (req, res) => {
    const providedToken = req.query.token as string | undefined;

    // Check token authentication if token is provided
    if (providedToken !== undefined && providedToken !== AURORA_HEALTH_TOKEN) {
      return res.status(401).json({
        error: "Unauthorized",
        message: "Invalid health check token"
      });
    }

    // Calculate uptime in seconds
    const uptimeSeconds = Math.floor((Date.now() - serverStartTime) / 1000);

    // Check database connection status
    let databaseStatus = "disconnected";
    let databaseError: string | undefined;
    try {
      // Attempt to query database to check if it's connected
      // Properly await the async operation
      const testQuery = await corpusStorage.getRecent(1);
      databaseStatus = "connected";
    } catch (e: any) {
      databaseStatus = "disconnected";
      databaseError = e?.message ?? String(e);
      console.error("[Health Check] Database connection failed:", databaseError);
    }

    // Check WebSocket server status more thoroughly
    let websocketStatus = "inactive";
    let websocketDetails: any = {};
    if (wsServer) {
      try {
        // Check if the WebSocket server is properly initialized and listening
        const wsServerInternal = wsServer as any;
        if (wsServerInternal.wss) {
          // Check if WebSocket server has clients property (indicates it's listening)
          websocketStatus = "active";
          // Add more detailed status if available
          if (wsServerInternal.wss.clients) {
            websocketDetails.clientCount = wsServerInternal.wss.clients.size;
          }
          // Check if server is in listening state
          if (wsServerInternal.wss.listening !== false) {
            websocketDetails.listening = true;
          }
        }
      } catch (e) {
        console.error("[Health Check] WebSocket status check failed:", e);
        websocketStatus = "error";
      }
    }

    // Get version from package.json
    let version = "1.0.0";
    try {
      const packageJson = JSON.parse(fs.readFileSync(path.join(process.cwd(), 'package.json'), 'utf-8'));
      version = packageJson.version || "1.0.0";
    } catch (e) {
      console.error("[Health Check] Failed to read package.json:", e);
    }

    // Determine overall health status
    const isHealthy = databaseStatus === "connected" && 
                     (websocketStatus === "active" || websocketStatus === "inactive"); // inactive is ok if not initialized

    const overallStatus = isHealthy ? "ok" : "unhealthy";
    const statusCode = isHealthy ? 200 : 503;

    // Build response object
    const response: any = {
      status: overallStatus,
      service: "Aurora-X",
      version: version,
      timestamp: new Date().toISOString(),
      uptime: uptimeSeconds,
      components: {
        database: databaseStatus,
        websocket: websocketStatus
      }
    };

    // Add error details if unhealthy
    if (!isHealthy) {
      response.errors = [];
      if (databaseStatus === "disconnected") {
        response.errors.push({
          component: "database",
          message: databaseError || "Database connection failed"
        });
      }
      if (websocketStatus === "error") {
        response.errors.push({
          component: "websocket",
          message: "WebSocket server error"
        });
      }
    }

    // Add WebSocket details if available
    if (Object.keys(websocketDetails).length > 0) {
      response.components.websocketDetails = websocketDetails;
    }

    // Return health check response with appropriate status code
    return res.status(statusCode).json(response);
  });

  // Self-learning daemon state
  let selfLearningProcess: any = null;
  let selfLearningStats = {
    started_at: null as string | null,
    last_activity: null as string | null,
    run_count: 0,
  };

  // Self-learning status endpoint
  app.get("/api/self-learning/status", (req, res) => {
    // Check if process is actually running
    const pidPath = path.join(process.cwd(), '.self_learning.pid');
    let running = false;
    
    if (fs.existsSync(pidPath)) {
      const pidStr = fs.readFileSync(pidPath, 'utf-8').trim();
      const pid = parseInt(pidStr);
      
      if (pid) {
        try {
          // Check if process exists (signal 0 doesn't kill, just checks)
          process.kill(pid, 0);
          running = true;
        } catch (e: any) {
          // Process doesn't exist
          if (e.code === 'ESRCH') {
            fs.unlinkSync(pidPath);
            running = false;
          }
        }
      }
    }
    
    return res.json({
      running,
      message: running ? "Self-learning daemon is active" : "Self-learning daemon is stopped",
      stats: running ? selfLearningStats : null
    });
  });

  // Start self-learning daemon
  app.post("/api/self-learning/start", (req, res) => {
    if (selfLearningProcess) {
      return res.status(400).json({
        error: "Already running",
        message: "Self-learning daemon is already active"
      });
    }

    try {
      const { sleepInterval = 15 } = req.body;
      const interval = Math.max(5, Math.min(3600, sleepInterval)); // Clamp between 5s and 1h
      
      console.log(`[Self-Learning] Starting daemon with ${interval}s interval...`);
      
      // Start as detached background process
      selfLearningProcess = spawn('python3', [
        '-m', 'aurora_x.self_learn',
        '--sleep', interval.toString(),
        '--max-iters', '50',
        '--beam', '20'
      ], {
        cwd: process.cwd(),
        detached: true,  // Run independently
        stdio: ['ignore', 'ignore', 'ignore']  // Fully detached
      });
      
      // Unref so it can run independently
      selfLearningProcess.unref();

      // Store PID for later management
      const pidPath = path.join(process.cwd(), '.self_learning.pid');
      fs.writeFileSync(pidPath, selfLearningProcess.pid?.toString() || '');

      selfLearningStats.started_at = new Date().toISOString();
      selfLearningStats.last_activity = new Date().toISOString();
      selfLearningStats.run_count = 0;

      console.log(`[Self-Learning] Daemon started successfully with PID ${selfLearningProcess.pid}`);

      return res.json({
        status: "started",
        message: `Self-learning daemon started successfully (runs every ${interval} seconds)`,
        stats: selfLearningStats,
        interval: interval
      });
    } catch (error: any) {
      console.error('[Self-Learning] Failed to start:', error);
      return res.status(500).json({
        error: "Failed to start",
        message: error.message
      });
    }
  });

  // Stop self-learning daemon
  app.post("/api/self-learning/stop", (req, res) => {
    try {
      console.log('[Self-Learning] Stopping daemon...');
      
      const pidPath = path.join(process.cwd(), '.self_learning.pid');
      
      // Try to read PID from file
      let pid: number | null = null;
      if (fs.existsSync(pidPath)) {
        const pidStr = fs.readFileSync(pidPath, 'utf-8').trim();
        pid = parseInt(pidStr);
      } else if (selfLearningProcess?.pid) {
        pid = selfLearningProcess.pid;
      }
      
      if (!pid) {
        return res.status(400).json({
          error: "Not running",
          message: "Self-learning daemon is not active"
        });
      }
      
      // Kill the process
      try {
        process.kill(pid, 'SIGTERM');
      } catch (e: any) {
        if (e.code !== 'ESRCH') {
          throw e;
        }
      }
      
      // Clean up
      if (fs.existsSync(pidPath)) {
        fs.unlinkSync(pidPath);
      }
      selfLearningProcess = null;
      
      const finalStats = { ...selfLearningStats };
      selfLearningStats = {
        started_at: null,
        last_activity: null,
        run_count: 0,
      };

      console.log('[Self-Learning] Daemon stopped successfully');

      return res.json({
        status: "stopped",
        message: "Self-learning daemon stopped successfully",
        final_stats: finalStats
      });
    } catch (error: any) {
      console.error('[Self-Learning] Failed to stop:', error);
      return res.status(500).json({
        error: "Failed to stop",
        message: error.message
      });
    }
  });

  // T08 Natural Language Synthesis activation endpoints
  // State storage for T08 (in production, this should be in a database or persistent storage)
  let t08Enabled = true;

  // GET endpoint to fetch current T08 status
  app.get("/api/t08/activate", (req, res) => {
    try {
      return res.json({
        t08_enabled: t08Enabled
      });
    } catch (e: any) {
      console.error("[T08] Error fetching T08 status:", e);
      return res.status(500).json({
        error: "Failed to fetch T08 status",
        details: e?.message ?? String(e)
      });
    }
  });

  // POST endpoint to toggle T08 activation
  app.post("/api/t08/activate", (req, res) => {
    try {
      const { on } = req.body;

      // Validate input
      if (typeof on !== 'boolean') {
        return res.status(400).json({
          error: "Invalid request",
          message: "The 'on' parameter must be a boolean value"
        });
      }

      // Update T08 state
      t08Enabled = on;

      // Log the change
      console.log(`[T08] Natural language synthesis ${on ? 'activated' : 'deactivated'}`);

      // Return success response
      return res.json({
        status: on ? "activated" : "deactivated",
        t08_enabled: t08Enabled
      });
    } catch (e: any) {
      console.error("[T08] Error updating T08 status:", e);
      return res.status(500).json({
        error: "Failed to update T08 status",
        details: e?.message ?? String(e)
      });
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

  // Corpus API endpoint - Function Library
  app.get("/api/corpus", (req, res) => {
    try {
      // Provide defaults for query parameters
      const queryDefaults = {
        func: undefined,
        limit: 50,
        offset: 0,
        perfectOnly: false,
        minScore: undefined,
        maxScore: undefined,
        startDate: undefined,
        endDate: undefined,
        ...req.query
      };

      const query = corpusQuerySchema.parse(queryDefaults);
      
      // Debug logging
      console.log("[Corpus API] Query params:", query);
      
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
      
      console.log("[Corpus API] Found items:", items.length);
      if (items.length > 0) {
        console.log("[Corpus API] First item:", items[0]);
      }
      
      return res.json({ items, hasMore: items.length === query.limit });
    } catch (e: any) {
      console.error("[Corpus API] Error fetching corpus entries:", e);
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

  // Progress tracking endpoints
  app.get("/api/synthesis/progress/:id", (req, res) => {
    try {
      const { id } = req.params;
      const progress = progressStore.getProgress(id);

      if (!progress) {
        return res.status(404).json({ error: "Synthesis not found" });
      }

      return res.json(progress);
    } catch (e: any) {
      return res.status(500).json({
        error: "Failed to retrieve progress",
        details: e?.message ?? String(e)
      });
    }
  });

  // Get synthesis result endpoint
  app.get("/api/synthesis/result/:id", (req, res) => {
    try {
      const { id } = req.params;
      const progress = progressStore.getProgress(id);

      if (!progress) {
        return res.status(404).json({ error: "Synthesis not found" });
      }

      if (progress.stage !== "COMPLETE" && progress.stage !== "ERROR") {
        return res.status(202).json({
          message: "Synthesis is still in progress",
          stage: progress.stage,
          percentage: progress.percentage,
          estimatedTimeRemaining: progress.estimatedTimeRemaining
        });
      }

      if (progress.stage === "ERROR") {
        return res.status(500).json({
          error: "Synthesis failed",
          details: progress.error,
          message: progress.message
        });
      }

      // Return the completed synthesis result
      if (!progress.result) {
        return res.status(500).json({ 
          error: "Synthesis completed but no result found",
          message: "This may be a legacy synthesis. Please try again." 
        });
      }

      return res.json({
        synthesis_id: id,
        message: progress.message,
        code: progress.result.code,
        language: progress.result.language,
        function_name: progress.result.functionName,
        description: progress.result.description,
        timestamp: progress.result.timestamp,
        actualDuration: progress.actualDuration,
        complexity: progress.complexity
      });
    } catch (e: any) {
      return res.status(500).json({
        error: "Failed to retrieve synthesis result",
        details: e?.message ?? String(e)
      });
    }
  });

  app.post("/api/synthesis/estimate", (req, res) => {
    try {
      const { message } = req.body;

      if (!message || typeof message !== 'string') {
        return res.status(400).json({ error: "Message is required" });
      }

      const complexity = progressStore.estimateComplexity(message);
      let estimatedTime: number;

      switch (complexity) {
        case "simple":
          estimatedTime = 7; // 5-10 seconds
          break;
        case "medium":
          estimatedTime = 20; // 15-30 seconds
          break;
        case "complex":
          estimatedTime = 45; // 30-60 seconds
          break;
        default:
          estimatedTime = 15;
      }

      return res.json({
        complexity,
        estimatedTime,
        message: `Estimated time: ${estimatedTime} seconds for ${complexity} synthesis`
      });
    } catch (e: any) {
      return res.status(500).json({
        error: "Failed to estimate synthesis time",
        details: e?.message ?? String(e)
      });
    }
  });

  // Natural Language Compilation endpoint - proxy to Aurora-X backend
  app.post("/api/nl/compile", async (req, res) => {
    try {
      const { prompt } = req.body;

      if (!prompt || typeof prompt !== 'string') {
        return res.status(400).json({ 
          status: "error",
          run_id: "",
          files_generated: [],
          message: "Prompt is required and must be a string"
        });
      }

      // Sanitize prompt to prevent shell injection
      const sanitizedPrompt = prompt
        .replace(/[`$()<>|;&\\\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/g, '')
        .replace(/\*/g, '')  // Remove wildcards
        .replace(/~/g, '')   // Remove tilde expansion
        .replace(/\[/g, '')  // Remove bracket expansion
        .replace(/\]/g, '')  // Remove bracket expansion
        .replace(/\{/g, '')  // Remove brace expansion  
        .replace(/\}/g, '')  // Remove brace expansion
        .trim();

      console.log(`[NL Compile] Processing prompt: "${sanitizedPrompt}"`);

      // Execute Aurora-X natural language compilation command
      const pythonProcess = spawn('python3', ['-m', 'aurora_x.main', '--nl', sanitizedPrompt], {
        cwd: process.cwd(),
        timeout: 60000, // 60 second timeout
        shell: false, // Disable shell to prevent injection
        env: { ...process.env }
      });

      let stdout = '';
      let stderr = '';

      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      // Wait for process completion
      const exitCode = await new Promise<number>((resolve, reject) => {
        pythonProcess.on('close', (code) => {
          resolve(code || 0);
        });

        pythonProcess.on('error', (err) => {
          console.error(`[NL Compile] Process error:`, err);
          reject(err);
        });
      });

      console.log(`[NL Compile] Exit code:`, exitCode);
      console.log(`[NL Compile] Output:`, stdout);
      if (stderr) console.log(`[NL Compile] Stderr:`, stderr);

      // Parse output to extract information
      let status = "error";
      let run_id = "";
      let files_generated: string[] = [];
      let message = "Compilation failed";

      // Check if output contains [OK] for success
      if (stdout.includes("[OK]")) {
        status = "success";

        // Extract run ID from patterns like "run-20251012-084111"
        const runIdMatch = stdout.match(/run-\d{8}-\d{6}/);
        if (runIdMatch) {
          run_id = runIdMatch[0];
        }

        // Extract file paths for Flask apps
        const flaskMatch = stdout.match(/Flask app generated at: (runs\/[^\s]+)/);
        if (flaskMatch) {
          files_generated.push(flaskMatch[1]);
          message = "Flask application generated successfully";
        }

        // Extract file paths for v3 functions
        const v3Match = stdout.match(/v3 generated: (runs\/[^\s]+)/);
        if (v3Match) {
          const runPath = v3Match[1];
          // Check for generated files in the run directory
          try {
            const srcDir = path.join(process.cwd(), runPath, 'src');
            if (fs.existsSync(srcDir)) {
              const files = fs.readdirSync(srcDir)
                .filter(file => file.endsWith('.py'))
                .map(file => path.join(runPath, 'src', file));
              files_generated.push(...files);
            }
          } catch (e) {
            console.error(`[NL Compile] Error checking generated files:`, e);
          }
          message = "Function generated successfully";
        }

        // Generic extraction for any "generated at:" pattern
        const genericMatches = Array.from(stdout.matchAll(/generated at: (runs\/[^\s]+)/g));
        for (const match of genericMatches) {
          if (!files_generated.includes(match[1])) {
            files_generated.push(match[1]);
          }
        }

        // If no specific files found but we have a run_id, check the run directory
        if (files_generated.length === 0 && run_id) {
          try {
            const runDir = path.join(process.cwd(), 'runs', run_id);
            if (fs.existsSync(runDir)) {
              const srcDir = path.join(runDir, 'src');
              if (fs.existsSync(srcDir)) {
                const files = fs.readdirSync(srcDir)
                  .filter(file => file.endsWith('.py'))
                  .map(file => path.join('runs', run_id, 'src', file));
                files_generated.push(...files);
              }
            }
          } catch (e) {
            console.error(`[NL Compile] Error scanning run directory:`, e);
          }
        }

        if (files_generated.length === 0 && status === "success") {
          message = "Code generated successfully (check runs directory)";
        }

      } else if (exitCode === 0) {
        // Process completed but no [OK] marker
        status = "warning";
        message = "Compilation completed with warnings";

        // Still try to extract run ID
        const runIdMatch = stdout.match(/run-\d{8}-\d{6}/);
        if (runIdMatch) {
          run_id = runIdMatch[0];
        }
      } else {
        // Process failed
        status = "error";
        message = stderr || stdout || "Compilation failed with no output";
      }

      // Return the response
      return res.json({
        run_id,
        status,
        files_generated,
        message
      });

    } catch (e: any) {
      console.error(`[NL Compile] Error:`, e);
      return res.status(500).json({
        status: "error",
        run_id: "",
        files_generated: [],
        message: e?.message ?? "Internal server error during compilation"
      });
    }
  });

  // Chat endpoint for natural language synthesis
  app.post("/api/chat", async (req, res) => {
    const { prompt } = req.body;
    if (!prompt) {
      return res.status(400).json({ error: "Missing prompt" });
    }

    try {
      // Call Python Aurora-X with natural language
      const { exec } = await import("child_process");
      const { promisify } = await import("util");
      const execAsync = promisify(exec);

      const command = `python3 -m aurora_x.main --nl "${prompt.replace(/"/g, '\\"')}"`;
      console.log(`[Aurora] Executing: ${command}`);

      const { stdout, stderr } = await execAsync(command, {
        cwd: process.cwd(),
        timeout: 60000, // 60 second timeout
      });

      // Extract run directory from output
      const runMatch = stdout.match(/Latest valid run: (run-[\d-]+)/);
      const runDir = runMatch ? runMatch[1] : null;

      res.json({
        message: "Synthesis completed",
        prompt,
        status: "success",
        output: stdout,
        runDir: runDir,
        error: stderr || null
      });
    } catch (error: any) {
      console.error("Chat error:", error);
      res.status(500).json({ 
        error: "Synthesis failed",
        details: error.message,
        output: error.stdout || "",
        stderr: error.stderr || ""
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

  // T09 Domain Router endpoints with unit normalization
  app.post("/api/units", async (req, res) => {
    try {
      const units = await import("./units");
      const { value } = req.body;

      if (!value || typeof value !== "string") {
        return res.status(400).json({ error: "missing 'value'" });
      }

      const [numeric_value, unit] = units.parse_value_with_unit(value);

      if (numeric_value === null) {
        return res.status(422).json({ error: `Could not parse value from: ${value}` });
      }

      const result = units.normalize_to_si(numeric_value, unit);

      return res.json({
        si_value: result.si_value,
        si_unit: result.si_unit,
        original: value,
        original_value: result.original_value,
        original_unit: result.original_unit,
        conversion_factor: result.conversion_factor,
        unit_type: result.unit_type
      });
    } catch (error: any) {
      console.error("[Aurora-X] Units API error:", error);
      return res.status(500).json({
        error: "Failed to process unit conversion",
        details: error?.message
      });
    }
  });

  // Note: The original /api/solve and /api/explain endpoints have been replaced
  // with new versions that directly use aurora_x/generators/solver.py

  // Task graph visualization endpoint
  app.get("/dashboard/graph", (req, res) => {
    const graphHTML = `<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Aurora-X · Master Task Graph</title>
  <style>
    html, body {
      margin: 0;
      height: 100%;
      background: #03060e;
      color: #e5e9ff;
      font-family: system-ui, -apple-system, sans-serif;
    }
    svg {
      width: 100%;
      height: 100%;
      background: radial-gradient(circle at 50% 50%, #101526, #03060e);
    }
    text {
      fill: #fff;
      font-size: 13px;
      text-anchor: middle;
      pointer-events: none;
      user-select: none;
    }
    .node circle {
      stroke: #fff;
      stroke-width: 1.2;
      cursor: pointer;
      transition: all 0.2s;
    }
    .node:hover circle {
      r: 35;
      stroke-width: 2;
      filter: brightness(1.2);
    }
    .node.completed circle {
      fill: #29cc5f;
    }
    .node.inprogress circle {
      fill: #1e90ff;
    }
    .node.pending circle {
      fill: #d93f3f;
    }
    .node.development circle {
      fill: #ffa600;
    }
    .link {
      stroke: #bbb;
      stroke-opacity: .4;
      stroke-width: 1.5;
    }
    .legend {
      position: absolute;
      top: 10px;
      left: 10px;
      color: #fff;
      font-size: 14px;
      background: rgba(0, 0, 0, 0.5);
      padding: 10px;
      border-radius: 8px;
    }
    .legend small {
      display: block;
      margin-top: 5px;
      opacity: 0.8;
    }
    .btn {
      position: absolute;
      top: 10px;
      right: 10px;
      padding: 8px 14px;
      background: #1e90ff;
      color: #fff;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 500;
      transition: background 0.2s;
    }
    .btn:hover {
      background: #1a7fd8;
    }
  </style>
</head>
<body>
  <div class="legend">
    Aurora-X Ultra — Master Dependency Graph<br>
    <small>Green=Complete • Blue=In Progress • Yellow=Development • Red=Pending</small>
    <small style="display:block;margin-top:3px;color:#1e90ff">✏️ Click any node to edit its percentage</small>
  </div>
  <a href="/dashboard" class="btn">← Dashboard</a>
  <svg id="graph"></svg>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <script>
    async function render() {
      try {
        const res = await fetch('/api/progress');
        const data = await res.json();
        const tasks = data.tasks || [];

        // Create nodes from tasks data
        const nodes = tasks.map(t => ({
          id: t.id || 'Unknown',
          name: t.name || 'Unknown Task',
          percent: typeof t.percent === 'number' ? t.percent : parseFloat(t.percent) || 0,
          status: t.status,
          group: determineGroup(t)
        }));

        // Function to determine node group/color
        function determineGroup(task) {
          const percent = typeof task.percent === 'number' ? task.percent : parseFloat(task.percent) || 0;

          if (percent >= 100) {
            return 'completed';
          } else if (task.status === 'in-development') {
            return 'development';
          } else if (percent > 0) {
            return 'inprogress';
          } else {
            return 'pending';
          }
        }

        // Create links between consecutive tasks (T01->T02->T03...)
        const links = [];
        for (let i = 1; i < nodes.length; i++) {
          links.push({
            source: nodes[i - 1].id,
            target: nodes[i].id
          });
        }

        // Setup D3 visualization
        const svg = d3.select("#graph");
        const width = window.innerWidth;
        const height = window.innerHeight;

        // Clear previous graph if any
        svg.selectAll("*").remove();

        // Create force simulation
        const simulation = d3.forceSimulation(nodes)
          .force("link", d3.forceLink(links).id(d => d.id).distance(160))
          .force("charge", d3.forceManyBody().strength(-450))
          .force("center", d3.forceCenter(width / 2, height / 2))
          .force("collision", d3.forceCollide().radius(35));

        // Create links
        const link = svg.append("g")
          .selectAll("line")
          .data(links)
          .enter()
          .append("line")
          .attr("class", "link");

        // Create nodes
        const node = svg.append("g")
          .selectAll("g")
          .data(nodes)
          .enter()
          .append("g")
          .attr("class", d => "node " + d.group);

        // Add circles to nodes
        node.append("circle")
          .attr("r", 30);

        // Add text labels to nodes
        node.append("text")
          .attr("dy", 5)
          .text(d => d.id);

        // Add click handler to update task percentage
        node.on("click", async (event, d) => {
          const currentPercent = typeof d.percent === 'number' ? d.percent : 0;
          const status = d.group === 'completed' ? 'Completed' :
                        d.group === 'inprogress' ? 'In Progress' :
                        d.group === 'development' ? 'In Development' :
                        'Pending';

          // Show prompt to update percentage
          const newPercentStr = prompt(
            \`Task: \${d.id}\\nName: \${d.name}\\nCurrent Progress: \${currentPercent}%\\nStatus: \${status}\\n\\nEnter new percentage (0-100):\`,
            currentPercent.toString()
          );

          // If user cancelled or entered nothing, do nothing
          if (newPercentStr === null || newPercentStr.trim() === '') {
            return;
          }

          const newPercent = parseFloat(newPercentStr);

          // Validate the input
          if (isNaN(newPercent) || newPercent < 0 || newPercent > 100) {
            alert('Invalid percentage. Please enter a number between 0 and 100.');
            return;
          }

          try {
            // Send update to the API
            const response = await fetch('/api/progress/task_percent', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                task_id: d.id,
                percentage: newPercent
              })
            });

            if (!response.ok) {
              const error = await response.json();
              alert(\`Failed to update task: \${error.message || 'Unknown error'}\`);
              return;
            }

            const result = await response.json();

            // Show success message
            alert(\`✅ Successfully updated task \${d.id} from \${result.old_percentage}% to \${result.new_percentage}%\\n\\nStatus: \${result.old_status} → \${result.new_status}\\nOverall Progress: \${result.overall_percent}%\`);

            // Re-render the graph to show the updated data
            render();

          } catch (error) {
            console.error('Error updating task percentage:', error);
            alert(\`Failed to update task percentage. Please check the console for details.\`);
          }
        });

        // Add drag behavior
        node.call(d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended));

        // Update positions on tick
        simulation.on("tick", () => {
          link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

          node
            .attr("transform", d => \`translate(\${d.x}, \${d.y})\`);
        });

        // Drag functions
        function dragstarted(event) {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          event.subject.fx = event.subject.x;
          event.subject.fy = event.subject.y;
        }

        function dragged(event) {
          event.subject.fx = event.x;
          event.subject.fy = event.y;
        }

        function dragended(event) {
          if (!event.active) simulation.alphaTarget(0);
          event.subject.fx = null;
          event.subject.fy = null;
        }

      } catch (error) {
        console.error('Error loading task data:', error);
        alert('Failed to load task data. Please check the console for details.');
      }
    }

    // Render the graph
    render();

    // Auto-refresh every 30 seconds
    setInterval(render, 30000);
  </script>
</body>
</html>`;

    res.setHeader('Content-Type', 'text/html');
    res.send(graphHTML);
  });

  // ========== Natural Language Code Synthesis Endpoints ==========

  // POST endpoint to compile/generate a project from natural language
  app.post("/api/nl/compile_full", async (req, res) => {
    try {
      const { prompt } = req.body;

      // Validate input
      if (!prompt || typeof prompt !== 'string' || prompt.trim().length === 0) {
        console.log('[Synthesis] Invalid prompt received');
        return res.status(400).json({
          status: "error",
          error: "Invalid request",
          details: "prompt is required and must be a non-empty string"
        });
      }

      console.log('[Synthesis] Starting project generation for prompt:', prompt.substring(0, 100) + '...');

      // For now, create a mock response to test the integration
      // We'll replace this with the actual Python call once we verify the endpoint works
      const mockResult = {
        status: "success",
        run_id: `run-${new Date().toISOString().replace(/[:.]/g, '-').replace('T', '-').substring(0, 17)}`,
        files: ["src/main.py", "requirements.txt", "README.md"],
        project_type: "python_script",
        framework: "python",
        language: "python",
        features: ["simple"],
        message: "Mock project generated successfully for testing"
      };

      console.log('[Synthesis] Mock response created:', mockResult);

      // Set CORS headers
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
      res.setHeader('Content-Type', 'application/json');

      // Return the mock result
      return res.json(mockResult);

      /* TODO: Replace with actual Python call once verified
      // Call Python synthesis engine
      const result = await new Promise<any>((resolve, reject) => {
        const pythonProcess = spawn('python3', [
          '-c',
          `
import sys
import json
import asyncio
sys.path.insert(0, '.')
from aurora_x.synthesis.universal_engine import synthesize_universal

async def main():
    try:
        result = await synthesize_universal("""${prompt.replace(/"/g, '\\"').replace(/\n/g, '\\n')}""")
        print(json.dumps(result))
    except Exception as e:
        import traceback
        print(json.dumps({"status": "error", "error": str(e), "traceback": traceback.format_exc()}))

asyncio.run(main())
`
        ], {
          cwd: process.cwd(),
          env: { ...process.env, PYTHONPATH: process.cwd() }
        });

        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
          stdout += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
          stderr += data.toString();
        });

        pythonProcess.on('close', (code) => {
          if (code !== 0) {
            console.error('[Synthesis] Python process failed:', stderr);
            reject(new Error(`Synthesis failed with code ${code}: ${stderr}`));
            return;
          }

          try {
            // Parse the JSON output from Python
            const result = JSON.parse(stdout);
            resolve(result);
          } catch (parseError: any) {
            console.error('[Synthesis] Failed to parse Python output:', stdout);
            reject(new Error(`Failed to parse synthesis result: ${parseError.message}`));
          }
        });

        pythonProcess.on('error', (error) => {
          console.error('[Synthesis] Failed to spawn Python process:', error);
          reject(error);
        });
      });

      // Check if synthesis was successful
      if (result.status === 'error') {
        console.error('[Synthesis] Generation failed:', result.error);
        return res.status(500).json({
          status: "error",
          error: "Synthesis failed",
          details: result.error || "Unknown error during synthesis"
        });
      }

      console.log('[Synthesis] Successfully generated project:', {
        run_id: result.run_id,
        project_type: result.project_type,
        files_count: result.files?.length || 0
      });

      // Set CORS headers
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

      // Return the synthesis result
      return res.json({
        status: "success",
        run_id: result.run_id,
        files: result.files || [],
        project_type: result.project_type || "unknown",
        zip_path: result.zip_path || null,
        framework: result.framework || null,
        language: result.language || null,
        features: result.features || [],
        message: `Successfully generated ${result.project_type || 'project'} with ${(result.files || []).length} files`
      });
      */

    } catch (error: any) {
      console.error('[Synthesis] Unexpected error:', error);
      return res.status(500).json({
        status: "error",
        error: "Internal server error",
        details: error?.message || String(error)
      });
    }
  });

  // Handle OPTIONS preflight requests for synthesis endpoint
  app.options("/api/nl/compile_full", (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Access-Control-Max-Age', '86400');
    res.sendStatus(204);
  });

  // GET endpoint to download generated project ZIP file
  app.get("/api/projects/:run_id/download", (req, res) => {
    try {
      const { run_id } = req.params;

      // Validate run_id format (e.g., run-20251012-123456)
      if (!run_id || !run_id.match(/^run-\d{8}-\d{6}$/)) {
        return res.status(400).json({
          error: "Invalid run ID",
          details: "Run ID must be in format: run-YYYYMMDD-HHMMSS"
        });
      }

      // Build the path to the ZIP file
      const zipPath = path.join(process.cwd(), 'runs', run_id, 'project.zip');

      // Check if the ZIP file exists
      if (!fs.existsSync(zipPath)) {
        console.error(`[Download] ZIP file not found: ${zipPath}`);
        return res.status(404).json({
          error: "Project not found",
          details: `No project found with run ID: ${run_id}`
        });
      }

      // Get file stats for size
      const stats = fs.statSync(zipPath);

      console.log(`[Download] Serving ZIP file: ${zipPath} (${stats.size} bytes)`);

      // Set headers for file download
      res.setHeader('Content-Type', 'application/zip');
      res.setHeader('Content-Disposition', `attachment; filename="${run_id}-project.zip"`);
      res.setHeader('Content-Length', stats.size.toString());
      res.setHeader('Access-Control-Allow-Origin', '*');

      // Stream the file to the response
      const fileStream = fs.createReadStream(zipPath);
      fileStream.pipe(res);

      fileStream.on('error', (error) => {
        console.error('[Download] Error streaming file:', error);
        if (!res.headersSent) {
          res.status(500).json({
            error: "Download failed",
            details: "Failed to stream the project file"
          });
        }
      });

    } catch (error: any) {
      console.error('[Download] Unexpected error:', error);
      return res.status(500).json({
        error: "Internal server error",
        details: error?.message || String(error)
      });
    }
  });

  // Handle OPTIONS preflight requests for download endpoint
  app.options("/api/projects/:run_id/download", (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Access-Control-Max-Age', '86400');
    res.sendStatus(204);
  });

  // POST endpoint for raw solver results
  app.post("/api/solve", (req, res) => {
    try {
      const { q } = req.body;

      // Validate input
      if (!q || typeof q !== 'string') {
        return res.status(400).json({
          ok: false,
          error: "Invalid request",
          message: "q is required and must be a string"
        });
      }

      // Limit query length for safety
      if (q.length > 1000) {
        return res.status(400).json({
          ok: false,
          error: "Query too long",
          message: "Query must be less than 1000 characters"
        });
      }

      console.log(`[Solver] Processing query: "${q.substring(0, 100)}..."`);

      // Python command to execute the solver
      const pythonCommand = `from aurora_x.generators.solver import solve_text; import json; import sys; q = sys.stdin.read(); print(json.dumps(solve_text(q)))`;

      // Spawn Python process with the query as stdin
      const python = spawn('python3', ['-c', pythonCommand], {
        cwd: process.cwd(),
        timeout: 5000, // 5 second timeout
      });

      let stdout = '';
      let stderr = '';

      // Collect output
      python.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      python.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      // Send the query to stdin
      python.stdin.write(q);
      python.stdin.end();

      // Handle process completion
      python.on('close', (code) => {
        if (code !== 0) {
          console.error(`[Solver] Python process exited with code ${code}`);
          console.error(`[Solver] stderr: ${stderr}`);
          return res.status(500).json({
            ok: false,
            error: "Solver execution failed",
            message: `Python process exited with code ${code}`,
            details: stderr
          });
        }

        try {
          // Parse the JSON result
          const result = JSON.parse(stdout.trim());
          console.log(`[Solver] Successfully solved query, task: ${result.task || 'unknown'}`);
          return res.json(result);
        } catch (parseError: any) {
          console.error(`[Solver] Error parsing solver result: ${parseError.message}`);
          console.error(`[Solver] stdout: ${stdout}`);
          return res.status(500).json({
            ok: false,
            error: "Failed to parse solver result",
            message: parseError.message,
            stdout: stdout.substring(0, 500)
          });
        }
      });

      // Handle errors
      python.on('error', (error) => {
        console.error(`[Solver] Failed to spawn Python process: ${error.message}`);
        return res.status(500).json({
          ok: false,
          error: "Failed to execute solver",
          message: error.message
        });
      });

    } catch (error: any) {
      console.error(`[Solver] Unexpected error: ${error.message}`);
      return res.status(500).json({
        ok: false,
        error: "Internal server error",
        message: error.message
      });
    }
  });

  // POST endpoint for formatted solver results
  app.post("/api/solve/pretty", (req, res) => {
    try {
      const { q } = req.body;

      // Validate input
      if (!q || typeof q !== 'string') {
        return res.status(400).json({
          ok: false,
          error: "Invalid request",
          message: "q is required and must be a string"
        });
      }

      // Limit query length for safety
      if (q.length > 1000) {
        return res.status(400).json({
          ok: false,
          error: "Query too long",
          message: "Query must be less than 1000 characters"
        });
      }

      console.log(`[Solver Pretty] Processing query: "${q.substring(0, 100)}..."`);

      // Python command to execute the solver
      const pythonCommand = `from aurora_x.generators.solver import solve_text; import json; import sys; q = sys.stdin.read(); print(json.dumps(solve_text(q)))`;

      // Spawn Python process with the query as stdin
      const python = spawn('python3', ['-c', pythonCommand], {
        cwd: process.cwd(),
        timeout: 5000, // 5 second timeout
      });

      let stdout = '';
      let stderr = '';

      // Collect output
      python.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      python.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      // Send the query to stdin
      python.stdin.write(q);
      python.stdin.end();

      // Handle process completion
      python.on('close', (code) => {
        if (code !== 0) {
          console.error(`[Solver Pretty] Python process exited with code ${code}`);
          console.error(`[Solver Pretty] stderr: ${stderr}`);
          return res.status(500).json({
            ok: false,
            error: "Solver execution failed",
            message: `Python process exited with code ${code}`,
            details: stderr
          });
        }

        try {
          // Parse the JSON result
          const result = JSON.parse(stdout.trim());

          if (!result.ok) {
            // Return error as-is for failed results
            return res.json({
              ok: false,
              formatted: result.error || "Unknown error",
              raw: result
            });
          }

          // Format the result based on task type
          let formatted = "";

          if (result.task === "arithmetic") {
            // Format: "2 + 3 * 4 = 14"
            formatted = `${result.input} = ${result.result}`;
          } else if (result.task === "differentiate") {
            // Format: "d/dx(x^3 - 2x^2 + x) = 3x^2 - 4x + 1"
            formatted = `d/dx(${result.input}) = ${result.result}`;
          } else if (result.task === "orbital_period") {
            // Format: "T ≈ 1.51 h (5436 s)"
            const seconds = result.result.period_seconds;
            const hours = seconds / 3600;
            const days = seconds / 86400;

            if (hours < 24) {
              formatted = `T ≈ ${hours.toFixed(2)} h (${Math.round(seconds)} s)`;
            } else if (days < 365) {
              formatted = `T ≈ ${days.toFixed(2)} days (${Math.round(seconds)} s)`;
            } else {
              const years = days / 365.25;
              formatted = `T ≈ ${years.toFixed(2)} years (${days.toFixed(1)} days)`;
            }
          } else {
            // Default formatting
            formatted = result.explanation || JSON.stringify(result.result);
          }

          console.log(`[Solver Pretty] Successfully formatted result: ${formatted}`);

          return res.json({
            ok: true,
            formatted: formatted,
            task: result.task,
            domain: result.domain,
            raw: result
          });

        } catch (parseError: any) {
          console.error(`[Solver Pretty] Error parsing solver result: ${parseError.message}`);
          console.error(`[Solver Pretty] stdout: ${stdout}`);
          return res.status(500).json({
            ok: false,
            error: "Failed to parse solver result",
            message: parseError.message,
            stdout: stdout.substring(0, 500)
          });
        }
      });

      // Handle errors
      python.on('error', (error) => {
        console.error(`[Solver Pretty] Failed to spawn Python process: ${error.message}`);
        return res.status(500).json({
          ok: false,
          error: "Failed to execute solver",
          message: error.message
        });
      });

    } catch (error: any) {
      console.error(`[Solver Pretty] Unexpected error: ${error.message}`);
      return res.status(500).json({
        ok: false,
        error: "Internal server error",
        message: error.message
      });
    }
  });

  // Factory Bridge endpoint - proxy to FastAPI backend
  app.post("/api/bridge/nl", async (req, res) => {
    try {
      const { prompt } = req.body;

      // Validate input
      if (!prompt || typeof prompt !== 'string') {
        return res.status(400).json({
          status: "error",
          error: "Invalid request",
          message: "prompt is required and must be a string"
        });
      }

      console.log(`[Bridge] Processing prompt: "${prompt.substring(0, 100)}..."`);

      // Proxy to FastAPI server
      try {
        const response = await fetch('http://localhost:5001/api/bridge/nl', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ prompt })
        });

        const data = await response.json();

        console.log(`[Bridge] Response from FastAPI: ${JSON.stringify(data).substring(0, 200)}`);

        return res.json(data);
      } catch (fetchError: any) {
        console.error(`[Bridge] Error calling FastAPI: ${fetchError.message}`);
        return res.status(502).json({
          status: "error",
          error: "Bridge service unavailable",
          message: "Could not connect to the Factory Bridge service. Please ensure it's running on port 5001."
        });
      }

    } catch (error: any) {
      console.error(`[Bridge] Unexpected error: ${error.message}`);
      return res.status(500).json({
        status: "error",
        error: "Internal server error",
        message: error.message
      });
    }
  });

  // UI Generate endpoint - relay to Bridge with PR mode support
  app.post("/api/ui/generate", async (req, res) => {
    try {
      const { prompt, repo, branch, mode } = req.body;

      // Validate input
      if (!prompt || typeof prompt !== 'string' || prompt.trim().length === 0) {
        return res.status(400).json({
          error: "invalid_request",
          message: "prompt is required and must be a non-empty string"
        });
      }

      // Limit prompt length for safety
      if (prompt.length > 5000) {
        return res.status(400).json({
          error: "prompt_too_long",
          message: "Prompt must be less than 5000 characters"
        });
      }

      // Build payload for Bridge
      const payload = {
        prompt,
        repo: repo || AURORA_REPO,
        branch: branch || TARGET_BRANCH,
        mode: mode || "api"
      };

      console.log(`[UI Generate] Processing request: "${prompt.substring(0, 100)}..."`);
      console.log(`[UI Generate] Target repo: ${payload.repo}, branch: ${payload.branch}`);

      // Forward to Bridge service
      try {
        const response = await fetch(`${BRIDGE_URL}/api/bridge/nl`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload)
        });

        if (response.status >= 300) {
          const errorText = await response.text();
          console.error(`[UI Generate] Bridge returned error status ${response.status}: ${errorText}`);
          return res.status(502).json({
            error: "bridge_failed",
            status: response.status,
            body: errorText.substring(0, 500)
          });
        }

        const data = await response.json();
        console.log(`[UI Generate] Success - PR/code generated`);
        return res.json(data);

      } catch (fetchError: any) {
        console.error(`[UI Generate] Failed to reach Bridge: ${fetchError.message}`);
        return res.status(502).json({
          error: "bridge_unreachable",
          message: `Could not connect to Bridge service at ${BRIDGE_URL}. Ensure it's running.`
        });
      }

    } catch (error: any) {
      console.error(`[UI Generate] Unexpected error: ${error.message}`);
      return res.status(500).json({
        error: "internal_error",
        message: error.message
      });
    }
  });

  // Rollback Open PR endpoint
  app.post("/api/bridge/rollback/open", async (req, res) => {
    try {
      // Check for GitHub token
      if (!AURORA_GH_TOKEN) {
        return res.status(500).json({
          status: "error",
          error: "Missing AURORA_GH_TOKEN",
          message: "GitHub token is not configured"
        });
      }

      const [owner, repo] = AURORA_REPO.split("/", 2);
      const searchQuery = `repo:${AURORA_REPO} is:pr is:open label:aurora`;

      console.log(`[Rollback Open] Searching for open Aurora PRs: ${searchQuery}`);

      // Search for open PRs with 'aurora' label
      const searchResponse = await fetch(`${GH_API}/search/issues?q=${encodeURIComponent(searchQuery)}`, {
        headers: getGitHubHeaders()
      });

      if (!searchResponse.ok) {
        const error = await searchResponse.text();
        console.error(`[Rollback Open] GitHub search failed: ${error}`);
        return res.status(502).json({
          status: "error",
          error: "GitHub API error",
          message: "Failed to search for open PRs"
        });
      }

      const searchData = await searchResponse.json();
      const items = searchData.items || [];

      if (items.length === 0) {
        return res.status(404).json({
          status: "error",
          error: "Not found",
          message: "No open Aurora PR found"
        });
      }

      const prNumber = items[0].number;
      console.log(`[Rollback Open] Found PR #${prNumber}, fetching details...`);

      // Get PR details to find the branch
      const prResponse = await fetch(`${GH_API}/repos/${owner}/${repo}/pulls/${prNumber}`, {
        headers: getGitHubHeaders()
      });

      if (!prResponse.ok) {
        const error = await prResponse.text();
        console.error(`[Rollback Open] Failed to get PR details: ${error}`);
        return res.status(502).json({
          status: "error",
          error: "GitHub API error",
          message: "Failed to get PR details"
        });
      }

      const prData = await prResponse.json();
      const headRef = prData.head.ref;

      console.log(`[Rollback Open] Closing PR #${prNumber} and deleting branch ${headRef}`);

      // Close the PR
      const closeResponse = await fetch(`${GH_API}/repos/${owner}/${repo}/pulls/${prNumber}`, {
        method: 'PATCH',
        headers: {
          ...getGitHubHeaders(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ state: "closed" })
      });

      if (!closeResponse.ok) {
        const error = await closeResponse.text();
        console.error(`[Rollback Open] Failed to close PR: ${error}`);
        return res.status(502).json({
          status: "error",
          error: "GitHub API error",
          message: "Failed to close PR"
        });
      }

      // Delete the branch
      const deleteResponse = await fetch(`${GH_API}/repos/${owner}/${repo}/git/refs/heads/${headRef}`, {
        method: 'DELETE',
        headers: getGitHubHeaders()
      });

      if (!deleteResponse.ok) {
        const error = await deleteResponse.text();
        console.error(`[Rollback Open] Failed to delete branch: ${error}`);
        // Don't fail the whole operation if branch deletion fails
      }

      console.log(`[Rollback Open] Successfully closed PR #${prNumber} and deleted branch ${headRef}`);

      return res.json({
        status: "ok",
        closed: prNumber,
        deleted_branch: headRef
      });

    } catch (error: any) {
      console.error(`[Rollback Open] Unexpected error: ${error.message}`);
      return res.status(500).json({
        status: "error",
        error: "Internal error",
        message: error.message
      });
    }
  });

  // Rollback Merged PR endpoint
  app.post("/api/bridge/rollback/merged", async (req, res) => {
    try {
      // Check for GitHub token
      if (!AURORA_GH_TOKEN) {
        return res.status(500).json({
          status: "error",
          error: "Missing AURORA_GH_TOKEN",
          message: "GitHub token is not configured"
        });
      }

      const [owner, repo] = AURORA_REPO.split("/", 2);
      const base = req.body.base || TARGET_BRANCH;
      const searchQuery = `repo:${AURORA_REPO} is:pr is:closed is:merged label:aurora sort:updated-desc`;

      console.log(`[Rollback Merged] Searching for merged Aurora PRs: ${searchQuery}`);

      // Search for merged PRs with 'aurora' label
      const searchResponse = await fetch(`${GH_API}/search/issues?q=${encodeURIComponent(searchQuery)}`, {
        headers: getGitHubHeaders()
      });

      if (!searchResponse.ok) {
        const error = await searchResponse.text();
        console.error(`[Rollback Merged] GitHub search failed: ${error}`);
        return res.status(502).json({
          status: "error",
          error: "GitHub API error",
          message: "Failed to search for merged PRs"
        });
      }

      const searchData = await searchResponse.json();
      const items = searchData.items || [];

      if (items.length === 0) {
        return res.status(404).json({
          status: "error",
          error: "Not found",
          message: "No merged Aurora PR found"
        });
      }

      const prNumber = items[0].number;
      console.log(`[Rollback Merged] Found PR #${prNumber}, fetching details...`);

      // Get PR details to find merge commit
      const prResponse = await fetch(`${GH_API}/repos/${owner}/${repo}/pulls/${prNumber}`, {
        headers: getGitHubHeaders()
      });

      if (!prResponse.ok) {
        const error = await prResponse.text();
        console.error(`[Rollback Merged] Failed to get PR details: ${error}`);
        return res.status(502).json({
          status: "error",
          error: "GitHub API error",
          message: "Failed to get PR details"
        });
      }

      const prData = await prResponse.json();

      if (!prData.merged) {
        return res.status(400).json({
          status: "error",
          error: "Invalid state",
          message: "Selected PR is not merged"
        });
      }

      const mergeSha = prData.merge_commit_sha;
      const targetBase = base || prData.base.ref;

      console.log(`[Rollback Merged] Attempting to revert PR #${prNumber} with merge SHA ${mergeSha}`);

      // Try GitHub's native revert endpoint first (if available)
      try {
        const revertResponse = await fetch(`${GH_API}/repos/${owner}/${repo}/pulls/${prNumber}/reverts`, {
          method: 'POST',
          headers: {
            ...getGitHubHeaders(),
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            commit_title: `Revert PR #${prNumber}`,
            body: "Automated revert via Aurora dashboard",
            revert: { branch: targetBase }
          })
        });

        if (revertResponse.ok) {
          const revertData = await revertResponse.json();
          console.log(`[Rollback Merged] Successfully created revert PR #${revertData.number}`);
          return res.json({
            status: "ok",
            revert_pr: revertData.number
          });
        }
      } catch (nativeError: any) {
        console.log(`[Rollback Merged] Native revert failed, trying Bridge fallback: ${nativeError.message}`);
      }

      // Fallback to Bridge revert endpoint
      console.log(`[Rollback Merged] Falling back to Bridge revert endpoint`);

      try {
        const bridgeResponse = await fetch(`${BRIDGE_URL}/api/bridge/revert`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            repo: AURORA_REPO,
            merge_sha: mergeSha,
            base: targetBase
          })
        });

        if (!bridgeResponse.ok) {
          const errorText = await bridgeResponse.text();
          console.error(`[Rollback Merged] Bridge revert failed: ${errorText}`);
          return res.status(502).json({
            status: "error",
            error: "Bridge revert failed",
            message: errorText.substring(0, 500)
          });
        }

        const bridgeData = await bridgeResponse.json();
        console.log(`[Rollback Merged] Bridge revert successful`);
        return res.json(bridgeData);

      } catch (bridgeError: any) {
        console.error(`[Rollback Merged] Bridge fallback failed: ${bridgeError.message}`);
        return res.status(502).json({
          status: "error",
          error: "Revert failed",
          message: "Both native and Bridge revert methods failed"
        });
      }

    } catch (error: any) {
      console.error(`[Rollback Merged] Unexpected error: ${error.message}`);
      return res.status(500).json({
        status: "error",
        error: "Internal error",
        message: error.message
      });
    }
  });

  const httpServer = createServer(app);

  // Set up WebSocket server for real-time progress updates
  wsServer = createWebSocketServer(httpServer);

  return httpServer;
}