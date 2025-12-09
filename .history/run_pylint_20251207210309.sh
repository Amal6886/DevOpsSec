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

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Pylint passed! No issues found."
elif [ $EXIT_CODE -eq 16 ]; then
    echo "⚠️  Pylint found issues. Check pylint_report.txt for details."
    echo "Score: $(grep 'rated at' pylint_report.txt | tail -1)"
else
    echo "❌ Pylint failed with exit code $EXIT_CODE"
fi

echo "Report saved to: pylint_report.txt"
exit $EXIT_CODE
