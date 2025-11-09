#!/usr/bin/env python3
"""
Deployment script with options for testing and full extraction
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.extract_streets import StreetExtractor
from scripts.extract_poi import POIExtractor
from scripts.extract_administrative import AdministrativeExtractor

def test_single_region():
    """Quick test with one region"""
    print("="*60)
    print("TESTING WITH ISTANBUL (Quick Test)")
    print("="*60)
    print()
    
    test_region = "İstanbul"
    
    print("Step 1: Testing Streets Extraction...")
    street_extractor = StreetExtractor()
    streets = street_extractor.extract_region_streets(test_region)
    print(f"Extracted {len(streets)} streets from {test_region}")
    print()
    
    print("Step 2: Testing POI Extraction...")
    poi_extractor = POIExtractor()
    pois = poi_extractor.extract_all_poi_for_region(test_region)
    total_pois = sum(len(p) for p in pois.values())
    print(f"Extracted {total_pois} POIs from {test_region}")
    print()
    
    print("="*60)
    print("TEST SUCCESSFUL!")
    print(f"Results: {len(streets)} streets, {total_pois} POIs")
    print(f"Check output/ folder for JSON files")
    print("="*60)
    print()
    print("Ready to run full extraction? Run:")
    print("  python deploy.py --full")
    
def run_full_extraction():
    """Full extraction of all regions"""
    print("="*60)
    print("FULL EXTRACTION - ALL 15 REGIONS")
    print("="*60)
    print()
    print("This will take 4-8 hours")
    print("You can stop with Ctrl+C and resume later")
    print()
    
    confirm = input("Continue? (yes/no): ").lower()
    if confirm != 'yes':
        print("Cancelled.")
        return
    
    print()
    print("Starting full extraction...")
    print()
    
    from run_pipeline import TurkeyOSMExtractor
    extractor = TurkeyOSMExtractor()
    extractor.run_complete_extraction()
    
    print()
    print("="*60)
    print("EXTRACTION COMPLETE!")
    print("="*60)
    print("Check output/ folder for all results")
    print("Check complete_extraction_summary.json for statistics")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--full':
        run_full_extraction()
    else:
        test_single_region()

if __name__ == "__main__":
    print()
    print("Turkey OSM Data Extractor")
    print("="*60)
    print()
    
    if len(sys.argv) == 1:
        print("Running QUICK TEST with Istanbul...")
        print("(For full extraction, use: python deploy.py --full)")
        print()
    
    main()
