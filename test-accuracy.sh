#!/bin/bash
# Velora AI - Prediction Accuracy Test Runner
# Runs quick accuracy validation

echo ""
echo "========================================"
echo "  VELORA AI - ACCURACY TEST"
echo "========================================"
echo ""

cd "$(dirname "$0")/backend"

if [ ! -f "venv/bin/python" ]; then
    echo "ERROR: Virtual environment not found."
    echo "Please run setup first."
    exit 1
fi

echo "Running quick accuracy test..."
echo ""

venv/bin/python quick_test.py

echo ""
echo "========================================"
echo ""
echo "To run full test suite, execute:"
echo "  cd backend"
echo "  venv/bin/python tests/test_accuracy.py"
echo ""
echo "========================================"
