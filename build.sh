#!/bin/bash

# Exit on error
set -e

echo "🔨 Building frontend..."
cd frontend
npm install
npm run build

echo "📦 Copying frontend build to backend/static..."
rm -rf ../backend/static
cp -r dist ../backend/static

echo "✅ Done preparing static files."
