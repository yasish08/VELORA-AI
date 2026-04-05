#!/bin/bash

echo "===================================="
echo "  Starting Velora AI Frontend"
echo "===================================="
echo ""

cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    echo ""
fi

echo "===================================="
echo "  Starting Vite Dev Server"
echo "===================================="
echo "Frontend will run at: http://localhost:5173"
echo "Press Ctrl+C to stop"
echo ""

npm run dev
