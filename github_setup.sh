#!/bin/bash

# GitHub Setup Script for Agentic AI Framework
# This script automates the initial Git setup

echo "╔══════════════════════════════════════════════════════════╗"
echo "║        GitHub Setup - Agentic AI Framework              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: Git is not installed"
    echo "   Install git: brew install git"
    exit 1
fi

echo "✅ Git is installed"
echo ""

# Initialize git repository
echo "📦 Initializing Git repository..."
if [ -d ".git" ]; then
    echo "⚠️  Git repository already initialized"
else
    git init
    echo "✅ Git repository initialized"
fi
echo ""

# Check if there are files to commit
echo "📝 Checking for files to commit..."
git add .

# Show status
echo "📊 Current status:"
git status --short
echo ""

# Create initial commit
echo "💾 Creating initial commit..."
read -p "Enter commit message (or press Enter for default): " COMMIT_MSG
if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Initial commit: Agentic AI Framework v0.1.0"
fi

git commit -m "$COMMIT_MSG"
if [ $? -eq 0 ]; then
    echo "✅ Initial commit created"
else
    echo "⚠️  Commit skipped (no changes or already committed)"
fi
echo ""

# Set default branch to main
echo "🌿 Setting default branch to 'main'..."
git branch -M main
echo "✅ Default branch set to 'main'"
echo ""

# Prompt for GitHub username
echo "🔗 GitHub Repository Setup"
echo "─────────────────────────────"
read -p "Enter your GitHub username: " GITHUB_USER

if [ -z "$GITHUB_USER" ]; then
    echo "❌ Error: GitHub username is required"
    exit 1
fi

# Prompt for repository name
read -p "Enter repository name (default: aiagentic): " REPO_NAME
if [ -z "$REPO_NAME" ]; then
    REPO_NAME="aiagentic"
fi

# Check if remote already exists
if git remote get-url origin &> /dev/null; then
    echo "⚠️  Remote 'origin' already exists"
    CURRENT_REMOTE=$(git remote get-url origin)
    echo "   Current remote: $CURRENT_REMOTE"
    read -p "Do you want to update it? (y/n): " UPDATE_REMOTE
    if [ "$UPDATE_REMOTE" = "y" ]; then
        git remote set-url origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
        echo "✅ Remote updated"
    fi
else
    git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
    echo "✅ Remote added: https://github.com/$GITHUB_USER/$REPO_NAME.git"
fi
echo ""

# Create tag
echo "🏷️  Creating version tag..."
TAG_NAME="v0.1.0"
if git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
    echo "⚠️  Tag $TAG_NAME already exists"
else
    git tag -a "$TAG_NAME" -m "Initial release: Agentic AI Framework"
    echo "✅ Tag $TAG_NAME created"
fi
echo ""

# Instructions for pushing
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                 Setup Complete! 🎉                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Create a new repository on GitHub:"
echo "   → Go to: https://github.com/new"
echo "   → Repository name: $REPO_NAME"
echo "   → Description: A modular framework for building AI agents"
echo "   → Visibility: Public (to showcase)"
echo "   → DO NOT initialize with README"
echo ""
echo "2. Push your code to GitHub:"
echo "   $ git push -u origin main"
echo "   $ git push origin $TAG_NAME"
echo ""
echo "3. Configure your repository on GitHub:"
echo "   → Add topics: ai-agents, python, llm, multi-agent-systems"
echo "   → Enable Issues and Discussions"
echo "   → Pin the repository on your profile"
echo ""
echo "4. Create a release:"
echo "   → Go to Releases → Create new release"
echo "   → Choose tag: $TAG_NAME"
echo "   → Title: v0.1.0 - Initial Release"
echo "   → Copy description from CHANGELOG.md"
echo ""
echo "📚 Full guide: See GITHUB_SETUP.md"
echo ""
echo "🚀 Your GitHub URL will be:"
echo "   https://github.com/$GITHUB_USER/$REPO_NAME"
echo ""
