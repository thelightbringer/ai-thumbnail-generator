#!/bin/bash

# Exit on error
set -e

echo "🔨 Building frontend..."
cd frontend
npm install
npm run build

echo "📦 Preparing backend static directory..."

# Remove previous frontend build, but keep other static assets like Logo.png
cd ../backend
mkdir -p static
rm -rf static/*

# Re-copy logo manually if needed (only if removed above)
cp ../frontend/src/assets/Logo.png static/Logo.png

# Copy frontend build to static
cp -r ../frontend/dist/* static/

echo "✅ Done preparing static files."
