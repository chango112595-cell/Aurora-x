✅ One Big Script for Copilot Instructions
/**
 * AI Copilot Auto Fix Script
 * Features:
 * - Scans entire repo for code files
 * - Uses AI (Copilot-like instructions) to fix bugs and improve code
 * - Creates a new branch and PR
 * - Runs tests and waits for checks
 * - Merges automatically if successful
 */

import { Octokit } from "@octokit/rest";
import fetch from "node-fetch";
import { execSync } from "child_process";
import fs from "fs";
import path from "path";

// ✅ Environment Variables
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const REPO_OWNER = process.env.REPO_OWNER || "your-username";
const REPO_NAME = process.env.REPO_NAME || "your-repo";
const BASE_BRANCH = process.env.BASE_BRANCH || "main";
const FIX_BRANCH = `ai-fixes-${Date.now()}`;
const TEST_COMMAND = process.env.TEST_COMMAND || "npm test";

const octokit = new Octokit({ auth: GITHUB_TOKEN });

// ✅ Copilot-style instructions for AI
const copilotInstructions = `
You are an expert software engineer. Your task:
1. Review the entire repository for bugs, syntax errors, and failing tests.
2. Fix broken code while preserving functionality.
3. Ensure code follows best practices for readability and maintainability.
4. Do NOT remove essential logic or features.
5. After fixing, ensure all tests pass and code builds successfully.
Return ONLY the corrected code for each file.
`;

async function cloneRepo() {
  console.log("📥 Cloning repo...");
  execSync(`git clone https://github.com/${REPO_OWNER}/${REPO_NAME}.git`);
  process.chdir(REPO_NAME);
  execSync(`git checkout -b ${FIX_BRANCH}`);
}

async function scanFiles(dir, extensions = [".js", ".ts", ".py", ".java"]) {
  let files = [];
  for (const file of fs.readdirSync(dir)) {
    const fullPath = path.join(dir, file);
    if (fs.statSync(fullPath).isDirectory()) {
      files = files.concat(await scanFiles(fullPath, extensions));
    } else if (extensions.some(ext => file.endsWith(ext))) {
      files.push(fullPath);
    }
  }
  return files;
}

async function generateFix(content) {
  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${OPENAI_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "gpt-4.1",
      messages: [
        { role: "system", content: "You are an expert developer." },
        { role: "user", content: `${copilotInstructions}\n---\n${content}\n---` }
      ],
    }),
  });

  const data = await response.json();
  return data.choices[0].message.content;
}

async function applyFixes(files) {
  for (const file of files) {
    const content = fs.readFileSync(file, "utf8");
    const fixedContent = await generateFix(content);
    fs.writeFileSync(file, fixedContent);
    console.log(`✅ Fixed: ${file}`);
  }
}

async function commitAndPush() {
  execSync(`git add .`);
  execSync(`git commit -m "AI Copilot fixes applied"`);
  execSync(`git push origin ${FIX_BRANCH}`);
}

async function createPullRequest() {
  const { data: pr } = await octokit.pulls.create({
    owner: REPO_OWNER,
    repo: REPO_NAME,
    title: "AI Copilot Auto Fixes",
    head: FIX_BRANCH,
    base: BASE_BRANCH,
    body: "This PR contains AI-generated fixes for the entire repo.",
  });
  console.log(`🔗 PR created: ${pr.html_url}`);
  return pr.number;
}

async function runTests() {
  console.log("🧪 Running tests...");
  try {
    execSync(TEST_COMMAND, { stdio: "inherit" });
    return true;
  } catch {
    return false;
  }
}

async function waitForChecks(prNumber) {
  console.log("⏳ Waiting for checks to pass...");
  let checksPassed = false;
  while (!checksPassed) {
    const { data: status } = await octokit.checks.listForRef({
      owner: REPO_OWNER,
      repo: REPO_NAME,
      ref: FIX_BRANCH,
    });
    checksPassed = status.check_runs.every(run => run.conclusion === "success");
    if (!checksPassed) {
      console.log("Checks still running...");
      await new Promise(res => setTimeout(res, 30000));
    }
  }
  console.log("✅ All checks passed!");
}

async function mergePullRequest(prNumber) {
  await octokit.pulls.merge({
    owner: REPO_OWNER,
    repo: REPO_NAME,
    pull_number: prNumber,
    merge_method: "squash",
  });
  console.log("🎉 PR merged successfully!");
}

async function main() {
  cloneRepo();
  const files = await scanFiles(".");
  await applyFixes(files);
  commitAndPush();
  const prNumber = await createPullRequest();

  if (await runTests()) {
    await waitForChecks(prNumber);
    await mergePullRequest(prNumber);
  } else {
    console.log("❌ Tests failed after AI fixes. PR will remain open for manual review.");
  }
}

main().catch(console.error);


---

✅ How to Use:
1. Install dependencies:
1. npm install @octokit/rest node-fetch

2. Set environment variables:
2. export GITHUB_TOKEN=your_token
export OPENAI_API_KEY=your_openai_key
export REPO_OWNER=your-username
export REPO_NAME=your-repo
export BASE_BRANCH=main
export TEST_COMMAND="npm test"

3. Run locally:
3. node ai-copilot-auto-fix.js
