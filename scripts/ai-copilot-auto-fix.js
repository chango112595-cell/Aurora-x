// scripts/ai-copilot-auto-fix.js
// AI Copilot Auto Fix Script (run locally)
import { Octokit } from "@octokit/rest";
import fetch from "node-fetch";
import { execSync } from "child_process";
import fs from "fs";
import path from "path";

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const REPO_OWNER = process.env.REPO_OWNER || "chango112595-cell";
const REPO_NAME = process.env.REPO_NAME || "Aurora-x";
const BASE_BRANCH = process.env.BASE_BRANCH || "main";
const FIX_BRANCH = `ai-fixes-${Date.now()}`;
const TEST_COMMAND = process.env.TEST_COMMAND || "pytest";

const octokit = new Octokit({ auth: GITHUB_TOKEN });

const copilotInstructions = `
You are an expert software engineer. Your task:
1. Review the repository for bugs and failing tests.
2. Propose fixes preserving functionality.
3. Return only corrected file contents for each changed file.
`;

function cloneRepo() {
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
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "You are an expert developer." },
        { role: "user", content: `${copilotInstructions}\n---\n${content}\n---` }
      ],
    }),
  });

  const data = await response.json();
  return data.choices?.[0]?.message?.content ?? content;
}

async function applyFixes(files) {
  for (const file of files) {
    const content = fs.readFileSync(file, "utf8");
    const fixedContent = await generateFix(content);
    fs.writeFileSync(file, fixedContent);
    console.log(`✅ Fixed: ${file}`);
  }
}

function commitAndPush() {
  execSync(`git add .`);
  execSync(`git commit -m "AI Copilot fixes applied" || true`);
  execSync(`git push origin ${FIX_BRANCH}`);
}

async function createPullRequest() {
  const { data: pr } = await octokit.pulls.create({
    owner: REPO_OWNER,
    repo: REPO_NAME,
    title: "AI Copilot Auto Fixes",
    head: FIX_BRANCH,
    base: BASE_BRANCH,
    body: "This PR contains AI-generated fixes for the repository.",
  });
  console.log(`🔗 PR created: ${pr.html_url}`);
  return pr.number;
}

async function main() {
  cloneRepo();
  const files = await scanFiles(".");
  await applyFixes(files);
  commitAndPush();
  const prNumber = await createPullRequest();
  console.log(`Created PR #${prNumber} — please review and approve.`);
}

main().catch(console.error);
