#!/usr/bin/env python3
"""
Pre-commit validation script
Checks for AI-generated files and common issues before committing
"""

import os
import sys
from pathlib import Path

# Patterns that indicate AI-generated files
AI_PATTERNS = [
    '*_ANALYSIS.md',
    '*_APPLIED.md',
    '*_DEPLOYMENT.md',
    '*_TALK.md',
    '*_REVIEW.md',
    'START_HERE.md',
    'FIXES_*.md',
    'SCRIPT_*.md',
    'DATA_*.md',
    'REAL_*.md',
    '*-quick-deploy.sh',
    'project_structure.txt',
]

# Exceptions: legitimate project files that match patterns
EXCEPTIONS = [
    'docs/PUBLISHING_CHECKLIST.md',
    'docs/PROJECT_STRUCTURE.md',
    'docs/DEPLOYMENT.md',
]

# Files that should NOT be committed
FORBIDDEN_FILES = [
    '.env',
    '*.pyc',
    '__pycache__',
    '.DS_Store',
    'Thumbs.db',
    '*.log',
    'nohup.out',
]

def check_ai_files():
    """Check for AI-generated files"""
    root = Path('.')
    found_issues = []
    
    for pattern in AI_PATTERNS:
        matches = list(root.glob(f'**/{pattern}'))
        if matches:
            for match in matches:
                # Skip hidden directories and exceptions
                if any(part.startswith('.') for part in match.parts):
                    continue
                # Check if this file is in our exceptions list
                match_str = str(match).replace('\\', '/')
                if any(exc in match_str for exc in EXCEPTIONS):
                    continue
                found_issues.append(f"  ⚠️  AI-generated file: {match}")
    
    return found_issues

def check_forbidden_files():
    """Check for files that should not be committed"""
    root = Path('.')
    found_issues = []
    
    for pattern in FORBIDDEN_FILES:
        matches = list(root.glob(f'**/{pattern}'))
        if matches:
            for match in matches:
                if not any(part.startswith('.git') or part.startswith('.venv') for part in match.parts):
                    found_issues.append(f"  ❌ Forbidden file: {match}")
    
    return found_issues

def check_large_files():
    """Check for large files (>100MB)"""
    root = Path('.')
    found_issues = []
    max_size = 100 * 1024 * 1024  # 100MB
    
    for file in root.rglob('*'):
        if file.is_file():
            if any(part.startswith('.') for part in file.parts):
                continue
            try:
                if file.stat().st_size > max_size:
                    size_mb = file.stat().st_size / (1024 * 1024)
                    found_issues.append(f"  📦 Large file ({size_mb:.1f}MB): {file}")
            except:
                pass
    
    return found_issues

def main():
    """Run all pre-commit checks"""
    print("🔍 Running pre-commit checks...\n")
    
    all_issues = []
    
    # Check for AI-generated files
    print("Checking for AI-generated files...")
    ai_issues = check_ai_files()
    all_issues.extend(ai_issues)
    
    # Check for forbidden files
    print("Checking for forbidden files...")
    forbidden_issues = check_forbidden_files()
    all_issues.extend(forbidden_issues)
    
    # Check for large files
    print("Checking for large files...")
    large_issues = check_large_files()
    all_issues.extend(large_issues)
    
    print()
    
    if all_issues:
        print("❌ Issues found:\n")
        for issue in all_issues:
            print(issue)
        print("\n💡 Please fix these issues before committing.")
        print("   Add them to .gitignore or remove them from the repository.\n")
        return 1
    else:
        print("✅ All checks passed! Safe to commit.\n")
        return 0

if __name__ == "__main__":
    sys.exit(main())
