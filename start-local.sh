#!/bin/bash

# Croupier Local Startup Script
# This script prepares and starts the application for local development

echo "=========================================="
echo "  Croupier - Local Startup"
echo "=========================================="
echo ""

# Step 1: Check if .env exists, if not copy from .env.example
if [ ! -f .env ]; then
    echo "[INFO] .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "[SUCCESS] .env file created. Please review and update if needed."
    echo ""
else
    echo "[INFO] .env file already exists."
    echo ""
fi

# Step 2: Check if MongoDB is accessible
echo "[INFO] Checking MongoDB connection..."
MONGODB_URL=$(grep MONGODB_URL .env | cut -d '=' -f2)
if [ -z "$MONGODB_URL" ]; then
    MONGODB_URL="mongodb://localhost:27017"
fi
echo "[INFO] Using MongoDB at: $MONGODB_URL"
echo ""

# Step 3: Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "[INFO] Virtual environment not found. Creating..."
    python -m venv venv
    echo "[SUCCESS] Virtual environment created."
fi

echo "[INFO] Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

echo "[INFO] Installing dependencies..."
pip install -q -r requirements.txt
echo "[SUCCESS] Dependencies installed."
echo ""

# Step 4: Start the FastAPI application
echo "=========================================="
echo "  Starting Croupier API Server"
echo "=========================================="
echo ""
echo "[INFO] Server will be available at: http://localhost:8000"
echo "[INFO] API Documentation: http://localhost:8000/docs"
echo "[INFO] Press CTRL+C to stop the server"
echo ""

uvicorn main:app --reload
