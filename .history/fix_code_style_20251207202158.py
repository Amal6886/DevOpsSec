#!/usr/bin/env python
"""
Auto-fix script for code style issues.
Fixes trailing whitespace, trailing newlines, and other formatting issues.
"""
import os
import re
import sys
from pathlib import Path


def fix_trailing_whitespace(file_path):
    """Remove trailing whitespace from lines."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        modified = False
        
        for line in lines:
            # Remove trailing whitespace but preserve newline
            original_line = line
            fixed_line = line.rstrip() + '\n' if line.endswith('\n') else line.rstrip()
            
            if original_line != fixed_line:
                modified = True
            
            fixed_lines.append(fixed_line)
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def fix_trailing_newlines(file_path):
    """Ensure file ends with exactly one newline."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove all trailing newlines
        content = content.rstrip('\n')
        # Add exactly one newline
        content += '\n'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def should_process_file(file_path):
    """Check if file should be processed."""
    # Skip migration files
    if 'migrations' in str(file_path):
        return False
    
    # Skip __pycache__ and other hidden directories
    if '__pycache__' in str(file_path) or '.pyc' in str(file_path):
        return False
    
    # Only process Python files
    return file_path.suffix == '.py'


def main():
    """Main function to fix code style issues."""
    # Get project root directory
    project_root = Path(__file__).parent
    
    # Directories to process
    directories = [
        project_root / 'accounts',
        project_root / 'diet_plans',
        project_root / 'products',
        project_root / 'orders',
        project_root / 'notifications',
        project_root / 'diet_planner',
    ]
    
    # Also process root level Python files
    root_files = [project_root / 'manage.py']
    
    files_processed = 0
    files_modified = 0
    
    # Process directories
    for directory in directories:
        if not directory.exists():
            continue
        
        for file_path in directory.rglob('*.py'):
            if should_process_file(file_path):
                files_processed += 1
                print(f"Processing: {file_path}")
                
                modified_ws = fix_trailing_whitespace(file_path)
                modified_nl = fix_trailing_newlines(file_path)
                
                if modified_ws or modified_nl:
                    files_modified += 1
                    print(f"  ✓ Fixed: {file_path}")
    
    # Process root files
    for file_path in root_files:
        if file_path.exists() and should_process_file(file_path):
            files_processed += 1
            print(f"Processing: {file_path}")
            
            modified_ws = fix_trailing_whitespace(file_path)
            modified_nl = fix_trailing_newlines(file_path)
            
            if modified_ws or modified_nl:
                files_modified += 1
                print(f"  ✓ Fixed: {file_path}")
    
    print(f"\n{'='*60}")
    print(f"Files processed: {files_processed}")
    print(f"Files modified: {files_modified}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
