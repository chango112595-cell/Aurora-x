# Aurora-X Pre-commit Hook (PowerShell)
# Runs validation checks before allowing commit

$ErrorActionPreference = "Stop"

# Set PYTHONPATH
$env:PYTHONPATH = $PWD

# Run all validations
python tools/run_all_validations.py

# Exit with validation result
exit $LASTEXITCODE
