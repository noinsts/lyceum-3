#!/bin/bash

set -e

echo "📥 Updating repo..."
git pull origin master --rebase

echo "🐍 Starting bot..."
poetry run python3.12 run.py
