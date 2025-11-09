#!/usr/bin/env python3
"""Main pipeline runner for OSM Data Extraction."""
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

from src.extractors.extract_turkey import TurkeyOSMExtractor

if __name__ == "__main__":
    print("╔══════════════════════════════════════════╗")
    print("║   OSM Data Extractor Pipeline           ║")
    print("║   Currently extracting: Turkey 🇹🇷       ║")
    print("╚══════════════════════════════════════════╝\n")
    
    extractor = TurkeyOSMExtractor()
    extractor.run_complete_extraction()