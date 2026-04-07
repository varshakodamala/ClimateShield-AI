#!/bin/bash
# Bash wrapper to run Weather Platform with proper venv activation
# Usage: ./run.sh api | ./run.sh dashboard | ./run.sh pipeline

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
VENV_PATH="$SCRIPT_DIR/.venv"
ACTIVATE_SCRIPT="$VENV_PATH/bin/activate"

if [ -f "$ACTIVATE_SCRIPT" ]; then
    source "$ACTIVATE_SCRIPT"
else
    echo "Virtual environment not found at: $VENV_PATH"
    echo "Please create it with: python -m venv .venv"
    exit 1
fi

# Change to project directory
cd "$SCRIPT_DIR"

# Run the main script with arguments
python main.py "$@"
