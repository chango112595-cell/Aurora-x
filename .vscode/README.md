# VS Code Integration for Aurora-x

This directory contains VS Code configuration files to enhance the development experience for Aurora-x project.

## Features

### 1. **Editor Settings** (`.vscode/settings.json`)
- Auto-formatting on save with Prettier and Black
- Python linting with Pylint
- ESLint integration for JavaScript/TypeScript
- Pytest configuration for running tests
- Optimized file exclusions for better performance

### 2. **Debug Configurations** (`.vscode/launch.json`)
- **Python: Debug E2E Tests** - Debug end-to-end tests
- **Python: Debug Current Test File** - Debug the currently open test file
- **Python: Current File** - Debug any Python script
- **Node: Debug Server** - Debug the Node.js server
- **Node: Attach to Process** - Attach debugger to a running Node process
- **Python: Attach to Local** - Attach debugger to a running Python process
- **Full Stack Debug** - Debug both Python current file and Node server simultaneously

### 3. **Tasks** (`.vscode/tasks.json`)
- **Run E2E Tests** - Execute end-to-end tests using ci-start.sh
- **Install Python Dependencies** - Install Python packages
- **Install Node Dependencies** - Install Node.js packages
- **Build Project** - Build the entire project
- **Run Linter (Python)** - Lint Python code with Pylint
- **Start Dev Server** - Start the development server
- **Run All Tests** - Execute all test suites
- **Type Check** - Run TypeScript type checking

### 4. **Recommended Extensions** (`.vscode/extensions.json`)
Essential VS Code extensions for Aurora-x development:
- Python support
- Black formatter
- Pylint
- Prettier
- ESLint
- Tailwind CSS IntelliSense
- GitHub Copilot
- Test Explorer
- GitLens
- YAML support

## Getting Started

1. **Open the Workspace**
   ```bash
   code tools/Aurora-x.code-workspace
   ```
   Or simply open the repository folder in VS Code.

2. **Install Recommended Extensions**
   - VS Code will prompt you to install recommended extensions
   - Click "Install All" in the notification

3. **Run Tests**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Tasks: Run Test Task"
   - Select "Run E2E Tests"

4. **Debug**
   - Open the Debug panel (`Ctrl+Shift+D` or `Cmd+Shift+D`)
   - Select a debug configuration from the dropdown
   - Press F5 to start debugging

## Quick Commands

- **Run Tests**: `Ctrl+Shift+P` → "Tasks: Run Test Task"
- **Build**: `Ctrl+Shift+B`
- **Debug**: F5
- **Format Document**: `Shift+Alt+F`
- **Fix Linting Issues**: `Ctrl+Shift+P` → "ESLint: Fix all auto-fixable Problems"

## E2E Testing in VS Code

The E2E workflow is integrated into VS Code:

1. **Run E2E Tests Manually**
   - Use the "Run E2E Tests" task
   - Or run `bash scripts/ci-start.sh` from the integrated terminal

2. **Debug E2E Tests**
   - Set breakpoints in your test files
   - Select "Python: Debug E2E Tests" configuration
   - Press F5

3. **View Test Results**
   - Test output appears in the integrated terminal
   - Logs are written to `/tmp/aurora.log`

## Workspace vs Folder Settings

- **Workspace File**: `tools/Aurora-x.code-workspace` - Contains workspace-specific settings
- **Folder Settings**: `.vscode/` - Contains settings that apply when opening the folder directly

Both configurations are maintained for flexibility.

## Troubleshooting

### Python Interpreter Not Found
1. Press `Ctrl+Shift+P` → "Python: Select Interpreter"
2. Choose the Python interpreter with project dependencies installed

### ESLint Not Working
1. Ensure Node.js dependencies are installed: `npm install`
2. Restart VS Code

### Tests Not Discovered
1. Ensure pytest is installed: `pip install pytest`
2. Check Python interpreter is correctly selected
3. Reload window: `Ctrl+Shift+P` → "Developer: Reload Window"

## Contributing

When adding new VS Code configurations:
1. Update this README
2. Test configurations on both Windows and Unix systems
3. Ensure settings don't conflict with existing editor configurations
