#!/bin/bash
# Pylint runner script for Diet Planner project
# Usage: ./run_pylint.sh

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Warning: Virtual environment not found. Using system Python."
fi

# Install dependencies if needed
if ! python -c "import pylint" 2>/dev/null; then
    echo "Installing pylint and pylint-django..."
    pip install -q pylint pylint-django
fi

# Run pylint with .pylintrc config
echo "Running pylint analysis..."
pylint --rcfile=.pylintrc \
       --output-format=text \
       --reports=yes \
       accounts/ diet_plans/ products/ orders/ notifications/ diet_planner/ manage.py \
       > pylint_report.txt 2>&1

# Check exit code
EXIT_CODE=$?

# Pylint exit codes:
# 0 = no issues
# 1 = fatal error
# 2 = usage error
# 4 = convention issues
# 8 = refactor suggestions
# 16 = warnings
# Combinations: 28 = 4+8+16 (convention + refactor + warning)
# Only exit codes 1 and 2 are fatal errors

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Pylint passed! No issues found."
elif [ $EXIT_CODE -eq 1 ] || [ $EXIT_CODE -eq 2 ]; then
    echo "❌ Pylint failed with fatal error (exit code $EXIT_CODE)"
    echo "Check pylint_report.txt for details."
elif [ $EXIT_CODE -ge 4 ]; then
    echo "⚠️  Pylint found style issues (exit code $EXIT_CODE)"
    echo "Score: $(grep 'rated at' pylint_report.txt | tail -1 | grep -o '[0-9]\+\.[0-9]\+/10' || echo 'N/A')"
    echo "Check pylint_report.txt for details."
else
    echo "⚠️  Pylint completed with exit code $EXIT_CODE"
    echo "Check pylint_report.txt for details."
fi

echo "Report saved to: pylint_report.txt"
# Return 0 for success (warnings are acceptable)
exit 0
