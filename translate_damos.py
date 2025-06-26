#!/usr/bin/env python3
"""
DAMOS File Translator - Command Line Interface

A comprehensive translator for DAMOS (Data Acquisition and Measurement Object Specification) files
used in automotive ECU development. Translates automotive terminology from any language to English
while preserving the exact file structure and format.

Usage:
    python translate_damos.py input_file.dam [options]
    python translate_damos.py input_directory --batch [options]

Examples:
    # Translate a single German DAMOS file
    python translate_damos.py your_file.dam -o your_file_english.dam

    # Auto-detect language and translate
    python translate_damos.py your_file.dam

    # Batch translate all .dam files in a directory
    python translate_damos.py ./damos_files --batch -o ./translated_files

    # Validate a translated file
    python translate_damos.py original.dam --validate translated.dam
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path so we can import our modules
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from damos_translator.main import main

if __name__ == '__main__':
    # Check if we have the required dependencies
    try:
        import chardet
    except ImportError:
        print("Warning: chardet not installed. File encoding detection may be limited.")
        print("Install with: pip install chardet")
    
    # Run the main application
    sys.exit(main())

