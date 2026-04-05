#!/bin/bash

echo "===================================="
echo "  Starting Velora AI Backend"
echo "===================================="
echo ""

cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing/Updating dependencies..."
pip install -r requirements.txt

echo ""
echo "===================================="
echo "  Starting FastAPI Server"
echo "===================================="
echo "Backend will run at: http://127.0.0.1:8000"
echo "Press Ctrl+C to stop"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
