const { execSync } = require("child_process");

const ports = [5000, 8000, 9000, 9100, 9200];

console.log("🛑 Stopping Aurora-X...");

for (const port of ports) {
  try {
    const pid = execSync(`npx kill-port ${port}`).toString();
    console.log(`🔻 Cleared port ${port}`);
  } catch (e) {
    console.log(`✔ Port ${port} already free`);
  }
}

console.log("✅ Aurora-X stopped.");
