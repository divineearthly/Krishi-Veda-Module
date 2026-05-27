#!/bin/bash
set -e
MESSAGE="${1:-🕉️ Krishi-Veda update}"
echo "🚀 Krishi-Veda Auto-Deploy"
cd ~/Krishi-Veda-Module
git add .
if git diff --staged --quiet; then
    echo "No changes to commit."
else
    git commit -m "$MESSAGE"
    echo "✅ Committed"
fi
git push origin main 2>&1 | tail -3
echo "✅ Pushed to GitHub"
