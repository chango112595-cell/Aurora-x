module.exports = {
  root: true,
  env: { node: true, es2022: true },
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint", "import"],
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:import/recommended",
    "plugin:import/typescript",
    "prettier",
  ],
  rules: {
    "import/order": ["error", { "newlines-between": "always", "alphabetize": { "order": "asc" } }],
  },
  ignorePatterns: [
    "node_modules/",
    "dist/",
    "build/",
    ".next/",
    "client/.next/",
    "client/dist/",
    "k8s/",
    ".aurora/",
    ".github/",
    "**/*.d.ts",
  ],
  overrides: [{ files: ["**/*.js"], parser: "espree" }],
};
