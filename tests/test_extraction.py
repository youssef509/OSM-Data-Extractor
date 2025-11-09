#!/usr/bin/env python3
"""
Test script to verify OSM data extraction for a single location
Tests: 1 Province -> 1 District -> Neighborhoods -> Streets -> POIs
"""
import sys
import os
import json
import time
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.utils import setup_logging, save_json
import requests

# Test configuration
TEST_PROVINCE = "İstanbul"
TEST_DISTRICT = "Kadıköy"  # Well-known district with lots of data
OUTPUT_DIR = "test_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Overpass API endpoint
OVERPASS_URL = "https://overpass-api.de/api/interpreter"


class OSMTestExtractor:
    def __init__(self):
        self.logger = setup_logging(f"{OUTPUT_DIR}/test_extraction.log")
        self.results = {
            'test_time': datetime.now().isoformat(),
            'test_location': f"{TEST_PROVINCE} - {TEST_DISTRICT}",
            'results': {}
        }
    
    def query_overpass(self, query, description):
        """Execute Overpass API query with retry logic"""
        self.logger.info(f"🔍 Testing: {description}")
        self.logger.info(f"Query: {query[:200]}...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    OVERPASS_URL,
                    data={'data': query},
                    timeout=120
                )
                
                if response.status_code == 200:
                    data = response.json()
                    element_count = len(data.get('elements', []))
                    self.logger.info(f"✅ Success! Found {element_count} elements")
                    return data
                elif response.status_code == 429:
                    wait_time = 60 * (attempt + 1)
                    self.logger.warning(f"⏳ Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"❌ Error {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                self.logger.error(f"❌ Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(30)
        
        return None
    
    def test_province(self):
        """Test: Extract province boundary"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"TEST 1: Province Extraction - {TEST_PROVINCE}")
        self.logger.info(f"{'='*60}")
        
        query = f"""
        [out:json][timeout:60];
        area["name:en"="Turkey"]["admin_level"="2"];
        (
          relation["name"="{TEST_PROVINCE}"]["admin_level"="4"]["boundary"="administrative"](area);
        );
        out body;
        >;
        out skel qt;
        """
        
        result = self.query_overpass(query, f"Province: {TEST_PROVINCE}")
        
        if result and result.get('elements'):
            province_data = {
                'name': TEST_PROVINCE,
                'found': True,
                'elements_count': len(result['elements']),
                'relations': [e for e in result['elements'] if e['type'] == 'relation'],
                'sample_data': result['elements'][0] if result['elements'] else None
            }
            self.results['results']['province'] = province_data
            self.logger.info(f"📊 Province data: {len(province_data['relations'])} relations found")
            return True
        else:
            self.results['results']['province'] = {'name': TEST_PROVINCE, 'found': False}
            self.logger.error(f"❌ Province not found or no data returned")
            return False
    
    def test_district(self):
        """Test: Extract district within province"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"TEST 2: District Extraction - {TEST_DISTRICT} in {TEST_PROVINCE}")
        self.logger.info(f"{'='*60}")
        
        query = f"""
        [out:json][timeout:60];
        area["name"="{TEST_PROVINCE}"]["admin_level"="4"]->.province;
        (
          relation["name"="{TEST_DISTRICT}"]["admin_level"="6"]["boundary"="administrative"](area.province);
        );
        out body;
        >;
        out skel qt;
        """
        
        result = self.query_overpass(query, f"District: {TEST_DISTRICT}")
        
        if result and result.get('elements'):
            district_data = {
                'name': TEST_DISTRICT,
                'province': TEST_PROVINCE,
                'found': True,
                'elements_count': len(result['elements']),
                'relations': [e for e in result['elements'] if e['type'] == 'relation'],
                'sample_data': result['elements'][0] if result['elements'] else None
            }
            self.results['results']['district'] = district_data
            self.logger.info(f"📊 District data: {len(district_data['relations'])} relations found")
            return True
        else:
            self.results['results']['district'] = {'name': TEST_DISTRICT, 'found': False}
            self.logger.error(f"❌ District not found or no data returned")
            return False
    
    def test_neighborhoods(self):
        """Test: Extract neighborhoods in district"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"TEST 3: Neighborhoods in {TEST_DISTRICT}")
        self.logger.info(f"{'='*60}")
        
        query = f"""
        [out:json][timeout:60];
        area["name"="{TEST_DISTRICT}"]["admin_level"="6"]->.district;
        (
          relation["admin_level"="8"]["boundary"="administrative"](area.district);
          relation["admin_level"="9"]["boundary"="administrative"](area.district);
          relation["admin_level"="10"]["boundary"="administrative"](area.district);
        );
        out body;
        >;
        out skel qt;
        """
        
        result = self.query_overpass(query, f"Neighborhoods in {TEST_DISTRICT}")
        
        if result and result.get('elements'):
            neighborhoods = [e for e in result['elements'] if e['type'] == 'relation']
            neighborhood_names = [n.get('tags', {}).get('name', 'Unknown') for n in neighborhoods[:5]]
            
            neighborhood_data = {
                'district': TEST_DISTRICT,
                'found': True,
                'total_count': len(neighborhoods),
                'sample_names': neighborhood_names,
                'sample_data': neighborhoods[0] if neighborhoods else None
            }
            self.results['results']['neighborhoods'] = neighborhood_data
            self.logger.info(f"📊 Neighborhoods found: {len(neighborhoods)}")
            self.logger.info(f"📝 Sample names: {', '.join(neighborhood_names)}")
            return len(neighborhoods) > 0
        else:
            self.results['results']['neighborhoods'] = {'district': TEST_DISTRICT, 'found': False}
            self.logger.error(f"❌ No neighborhoods found")
            return False
    
    def test_streets(self):
        """Test: Extract streets in district"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"TEST 4: Streets in {TEST_DISTRICT}")
        self.logger.info(f"{'='*60}")
        
        query = f"""
        [out:json][timeout:90];
        area["name"="{TEST_DISTRICT}"]["admin_level"="6"]->.district;
        (
          way["highway"]["name"](area.district);
        );
        out body;
        >;
        out skel qt;
        """
        
        result = self.query_overpass(query, f"Streets in {TEST_DISTRICT}")
        
        if result and result.get('elements'):
            streets = [e for e in result['elements'] if e['type'] == 'way' and e.get('tags', {}).get('name')]
            street_names = [s.get('tags', {}).get('name', 'Unknown') for s in streets[:10]]
            street_types = {}
            
            for street in streets:
                highway_type = street.get('tags', {}).get('highway', 'unknown')
                street_types[highway_type] = street_types.get(highway_type, 0) + 1
            
            street_data = {
                'district': TEST_DISTRICT,
                'found': True,
                'total_count': len(streets),
                'sample_names': street_names,
                'street_types': street_types,
                'sample_data': streets[0] if streets else None
            }
            self.results['results']['streets'] = street_data
            self.logger.info(f"📊 Streets found: {len(streets)}")
            self.logger.info(f"📝 Sample streets: {', '.join(street_names[:5])}")
            self.logger.info(f"🏷️  Street types: {street_types}")
            return len(streets) > 0
        else:
            self.results['results']['streets'] = {'district': TEST_DISTRICT, 'found': False}
            self.logger.error(f"❌ No streets found")
            return False
    
    def test_pois(self):
        """Test: Extract POIs in district"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"TEST 5: Points of Interest in {TEST_DISTRICT}")
        self.logger.info(f"{'='*60}")
        
        query = f"""
        [out:json][timeout:90];
        area["name"="{TEST_DISTRICT}"]["admin_level"="6"]->.district;
        (
          node["amenity"]["name"](area.district);
          way["amenity"]["name"](area.district);
          node["shop"]["name"](area.district);
          way["shop"]["name"](area.district);
        );
        out body;
        >;
        out skel qt;
        """
        
        result = self.query_overpass(query, f"POIs in {TEST_DISTRICT}")
        
        if result and result.get('elements'):
            pois = [e for e in result['elements'] if e.get('tags', {}).get('name')]
            poi_names = [p.get('tags', {}).get('name', 'Unknown') for p in pois[:10]]
            poi_categories = {}
            
            for poi in pois:
                tags = poi.get('tags', {})
                category = tags.get('amenity') or tags.get('shop') or 'other'
                poi_categories[category] = poi_categories.get(category, 0) + 1
            
            poi_data = {
                'district': TEST_DISTRICT,
                'found': True,
                'total_count': len(pois),
                'sample_names': poi_names,
                'categories': poi_categories,
                'sample_data': pois[0] if pois else None
            }
            self.results['results']['pois'] = poi_data
            self.logger.info(f"📊 POIs found: {len(pois)}")
            self.logger.info(f"📝 Sample POIs: {', '.join(poi_names[:5])}")
            self.logger.info(f"🏷️  Categories: {poi_categories}")
            return len(pois) > 0
        else:
            self.results['results']['pois'] = {'district': TEST_DISTRICT, 'found': False}
            self.logger.error(f"❌ No POIs found")
            return False
    
    def run_all_tests(self):
        """Run all extraction tests"""
        self.logger.info(f"\n{'#'*60}")
        self.logger.info(f"🧪 STARTING OSM EXTRACTION TEST")
        self.logger.info(f"📍 Location: {TEST_PROVINCE} - {TEST_DISTRICT}")
        self.logger.info(f"{'#'*60}\n")
        
        start_time = time.time()
        test_results = []
        
        # Run tests sequentially with delays
        tests = [
            ('Province', self.test_province),
            ('District', self.test_district),
            ('Neighborhoods', self.test_neighborhoods),
            ('Streets', self.test_streets),
            ('POIs', self.test_pois)
        ]
        
        for test_name, test_func in tests:
            success = test_func()
            test_results.append((test_name, success))
            time.sleep(5)  # Delay between tests to avoid rate limiting
        
        # Summary
        duration = time.time() - start_time
        self.results['duration_seconds'] = duration
        self.results['all_tests_passed'] = all(result[1] for result in test_results)
        
        self.logger.info(f"\n{'#'*60}")
        self.logger.info(f"📊 TEST SUMMARY")
        self.logger.info(f"{'#'*60}")
        
        for test_name, success in test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            self.logger.info(f"{status} - {test_name}")
        
        self.logger.info(f"\n⏱️  Total duration: {duration:.2f} seconds")
        self.logger.info(f"🎯 Overall: {'✅ ALL TESTS PASSED' if self.results['all_tests_passed'] else '❌ SOME TESTS FAILED'}")
        
        # Save results
        save_json(self.results, f"{OUTPUT_DIR}/test_results.json")
        self.logger.info(f"\n💾 Results saved to: {OUTPUT_DIR}/test_results.json")
        self.logger.info(f"📝 Logs saved to: {OUTPUT_DIR}/test_extraction.log")
        
        return self.results


if __name__ == "__main__":
    print("="*60)
    print("🧪 OSM Extraction Test Script")
    print("="*60)
    print(f"Testing location: {TEST_PROVINCE} - {TEST_DISTRICT}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("="*60)
    print()
    
    tester = OSMTestExtractor()
    results = tester.run_all_tests()
    
    print("\n" + "="*60)
    if results['all_tests_passed']:
        print("✅ SUCCESS! All tests passed.")
        print("✅ The extraction code is working correctly!")
        print("✅ You can proceed with full deployment.")
    else:
        print("⚠️  WARNING: Some tests failed.")
        print("⚠️  Review the logs before full deployment.")
        print(f"📝 Check: {OUTPUT_DIR}/test_extraction.log")
    print("="*60)
