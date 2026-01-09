# VS Code 2 Integration Guide

This PR adds comprehensive VS Code integration for the Aurora-x project, making it easier to develop, debug, and test the application.

## What's New

### VS Code Configuration Files (`.vscode/`)
- **settings.json** - Editor settings optimized for Aurora-x development
- **launch.json** - Debug configurations for Python, Node.js, and full-stack debugging
- **tasks.json** - Common development tasks (build, test, lint, etc.)
- **extensions.json** - Recommended VS Code extensions
- **README.md** - Detailed documentation for VS Code features

### Enhanced Workspace File
- Updated `tools/Aurora-x.code-workspace` with recommended settings and extensions

### Updated `.gitignore`
- Modified to track essential VS Code configuration files while excluding user-specific settings

## Quick Start

### Option 1: Open Workspace
```bash
code tools/Aurora-x.code-workspace
```

### Option 2: Open Folder
```bash
code .
```

Both methods will load the VS Code configuration automatically.

## Key Features

### 1. Debugging
Press F5 or use the Debug panel to start debugging:
- **Python E2E Tests** - Debug end-to-end tests with breakpoints
- **Node Server** - Debug the Node.js backend
- **Full Stack** - Debug both Python and Node simultaneously

### 2. Testing
Run tests directly from VS Code:
- Press `Ctrl+Shift+P` → "Tasks: Run Test Task"
- Or use the Testing sidebar to run individual tests

### 3. Auto-Formatting
Code is automatically formatted on save:
- Python: Black formatter
- JavaScript/TypeScript: Prettier
- Consistent code style across the project

### 4. Linting
Real-time linting with:
- Python: Pylint
- JavaScript/TypeScript: ESLint
- Auto-fix on save when possible

## E2E Testing Integration

The E2E workflow from `.github/workflows/aurora-e2e.yml` is fully integrated:

1. **Run E2E Tests**
   - Use Task: "Run E2E Tests"
   - Executes `scripts/ci-start.sh`
   - Same workflow as CI/CD pipeline

2. **Debug E2E Tests**
   - Set breakpoints in test files
   - Select "Python: Debug E2E Tests"
   - Step through test execution

3. **View Logs**
   - Test output in integrated terminal
   - Logs available at `/tmp/aurora.log`

## Recommended Extensions

VS Code will prompt you to install these extensions:
- **ms-python.python** - Python language support
- **ms-python.black-formatter** - Python code formatter
- **esbenp.prettier-vscode** - Code formatter for JS/TS
- **dbaeumer.vscode-eslint** - JavaScript/TypeScript linting
- **github.copilot** - AI pair programmer
- **github.copilot-chat** - AI chat assistant

## Development Workflow

### 1. Setup
```bash
# Install dependencies
npm install
pip install -e ".[dev]"
```

### 2. Development
- Open files and start editing
- Auto-formatting on save
- Real-time linting feedback

### 3. Testing
- Run specific tests: Select "Python: Debug Current Test File"
- Run all tests: Use "Run E2E Tests" task

### 4. Debugging
- Set breakpoints (click left of line numbers)
- Press F5 to start debugging
- Use Debug Console for REPL

## File Structure

```
.vscode/
├── README.md           # Detailed VS Code documentation
├── settings.json       # Editor and language settings
├── launch.json         # Debug configurations
├── tasks.json          # Build and test tasks
└── extensions.json     # Recommended extensions

tools/
└── Aurora-x.code-workspace  # Workspace configuration
```

## Benefits

1. **Consistent Development Environment** - All developers use the same settings
2. **Faster Onboarding** - New developers get recommended extensions and configurations
3. **Improved Debugging** - Pre-configured debug setups for common scenarios
4. **Better Productivity** - Auto-formatting, linting, and task shortcuts
5. **CI/CD Alignment** - Local testing matches GitHub Actions workflows

## Related Files

- **E2E Workflow**: `.github/workflows/aurora-e2e.yml`
- **CI Start Script**: `scripts/ci-start.sh`
- **Test Configuration**: `pytest.ini`
- **Python Config**: `pyproject.toml`
- **TypeScript Config**: `tsconfig.json`

## Troubleshooting

### Extensions Not Loading
1. Install recommended extensions when prompted
2. Or: `Ctrl+Shift+P` → "Extensions: Show Recommended Extensions"

### Debugger Not Working
1. Verify Python/Node are installed
2. Select correct Python interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"
3. Restart VS Code

### Tests Not Running
1. Install dependencies: `pip install -e ".[dev]"`
2. Verify pytest is installed: `pytest --version`
3. Check Python interpreter is selected

## Contributing

When modifying VS Code configurations:
1. Test on multiple platforms (Windows, macOS, Linux)
2. Update documentation in `.vscode/README.md`
3. Ensure settings don't break existing workflows
4. Add comments for complex configurations

## Additional Resources

- [VS Code Documentation](https://code.visualstudio.com/docs)
- [Python in VS Code](https://code.visualstudio.com/docs/python/python-tutorial)
- [Debugging in VS Code](https://code.visualstudio.com/docs/editor/debugging)
- [Tasks in VS Code](https://code.visualstudio.com/docs/editor/tasks)
