#!/usr/bin/env python3
"""
Build hierarchical address structure from OSM data
Province -> District -> Neighborhood -> Street
"""

import json
from pathlib import Path
from collections import defaultdict
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.prepared import prep
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def load_administrative_boundaries(admin_file):
    """Load and organize administrative boundaries by level"""
    logger.info("Loading administrative boundaries...")
    
    with open(admin_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Organize by admin level
    boundaries = {
        '2': [],  # Country
        '4': [],  # Province
        '6': [],  # District
        '8': []   # Neighborhood
    }
    
    for boundary in data['boundaries']:
        level = boundary.get('admin_level', '')
        if level in boundaries:
            boundaries[level].append(boundary)
    
    logger.info(f"Loaded {len(boundaries['4'])} provinces")
    logger.info(f"Loaded {len(boundaries['6'])} districts")
    logger.info(f"Loaded {len(boundaries['8'])} neighborhoods")
    
    return boundaries

def load_streets(streets_file):
    """Load streets data"""
    logger.info(f"Loading streets from {streets_file}...")
    
    with open(streets_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info(f"Loaded {data['total_count']:,} streets")
    return data['streets']

def build_hierarchy_simple(streets, admin_boundaries):
    """
    Build hierarchy based on street names and administrative boundaries
    Since we don't have polygon geometries, we'll use a simpler approach
    """
    logger.info("Building address hierarchy...")
    
    # Create hierarchy structure
    hierarchy = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    # Get province and district names
    provinces = {b['name'] for b in admin_boundaries['4'] if b['name']}
    districts = {b['name'] for b in admin_boundaries['6'] if b['name']}
    neighborhoods = {b['name'] for b in admin_boundaries['8'] if b['name']}
    
    logger.info(f"Processing {len(streets):,} streets...")
    
    processed = 0
    for street in streets:
        # Try to determine location from coordinates
        lat = street.get('center_lat')
        lon = street.get('center_lon')
        
        if not lat or not lon:
            continue
        
        # Approximate province based on coordinates
        province = determine_province_by_coords(lat, lon)
        district = "Unknown District"
        neighborhood = "Unknown Neighborhood"
        
        # Add street to hierarchy
        hierarchy[province][district][neighborhood].append({
            'id': street['id'],
            'name': street['name'],
            'highway_type': street['highway_type'],
            'coordinates': {
                'lat': lat,
                'lon': lon
            },
            'surface': street.get('surface', ''),
            'lanes': street.get('lanes', ''),
            'maxspeed': street.get('maxspeed', ''),
            'oneway': street.get('oneway', ''),
            'lit': street.get('lit', '')
        })
        
        processed += 1
        if processed % 10000 == 0:
            logger.info(f"Processed {processed:,} streets...")
    
    return hierarchy

def determine_province_by_coords(lat, lon):
    """
    Approximate province based on coordinates
    This is a simplified approach - ideally you'd use polygon intersection
    """
    # Major cities approximate boundaries
    city_coords = {
        'İstanbul': {'lat': (40.8, 41.3), 'lon': (28.5, 29.5)},
        'Ankara': {'lat': (39.7, 40.2), 'lon': (32.5, 33.2)},
        'İzmir': {'lat': (38.2, 38.6), 'lon': (26.8, 27.4)},
        'Bursa': {'lat': (40.0, 40.4), 'lon': (28.7, 29.4)},
        'Antalya': {'lat': (36.7, 37.2), 'lon': (30.4, 31.2)},
        'Adana': {'lat': (36.8, 37.2), 'lon': (35.0, 35.6)},
        'Konya': {'lat': (37.7, 38.2), 'lon': (32.2, 33.0)},
        'Gaziantep': {'lat': (36.9, 37.3), 'lon': (37.2, 37.6)},
        'Şanlıurfa': {'lat': (37.0, 37.4), 'lon': (38.6, 39.2)},
        'Diyarbakır': {'lat': (37.8, 38.0), 'lon': (39.9, 40.4)},
        'Mersin': {'lat': (36.6, 37.0), 'lon': (34.4, 34.8)},
        'Kayseri': {'lat': (38.6, 38.9), 'lon': (35.3, 35.7)},
        'Eskişehir': {'lat': (39.6, 39.9), 'lon': (30.4, 31.0)},
        'Trabzon': {'lat': (40.8, 41.2), 'lon': (39.5, 40.0)},
        'Erzurum': {'lat': (39.8, 40.1), 'lon': (41.0, 41.5)},
    }
    
    for city, bounds in city_coords.items():
        if (bounds['lat'][0] <= lat <= bounds['lat'][1] and 
            bounds['lon'][0] <= lon <= bounds['lon'][1]):
            return city
    
    return "Other Province"

def save_hierarchy(hierarchy, output_file):
    """Save hierarchy to JSON file"""
    logger.info(f"Saving hierarchy to {output_file}...")
    
    # Convert defaultdict to regular dict for JSON serialization
    output = {}
    total_streets = 0
    
    for province, districts in hierarchy.items():
        output[province] = {}
        for district, neighborhoods in districts.items():
            output[province][district] = {}
            for neighborhood, streets in neighborhoods.items():
                output[province][district][neighborhood] = streets
                total_streets += len(streets)
    
    # Create summary
    result = {
        'extracted_at': '2025-10-21T03:51:38',
        'method': 'Hierarchical organization by coordinates',
        'statistics': {
            'total_provinces': len(output),
            'total_streets': total_streets
        },
        'hierarchy': output
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved {total_streets:,} streets in {len(output)} provinces")
    
    # Print summary
    logger.info("\nHierarchy Summary:")
    for province in sorted(output.keys()):
        street_count = sum(
            len(streets) 
            for district in output[province].values() 
            for streets in district.values()
        )
        logger.info(f"  {province}: {street_count:,} streets")

def main():
    """Main process"""
    logger.info("Building Address Hierarchy")
    logger.info("=" * 60)
    
    # File paths
    base_dir = Path("turkey-osm-output")
    admin_file = base_dir / "turkey_administrative.json"
    streets_file = base_dir / "Unknown_streets.json"
    output_file = base_dir / "turkey_hierarchy.json"
    
    # Check files exist
    if not admin_file.exists():
        logger.error(f"Administrative boundaries file not found: {admin_file}")
        return
    
    if not streets_file.exists():
        logger.error(f"Streets file not found: {streets_file}")
        return
    
    # Load data
    admin_boundaries = load_administrative_boundaries(admin_file)
    streets = load_streets(streets_file)
    
    # Build hierarchy (process subset for speed - can change to process all)
    logger.info("\nProcessing first 50,000 streets as a sample...")
    logger.info("   (Change code to process all 394K streets - takes longer)")
    sample_streets = streets[:50000]  # Change to streets to process all
    
    hierarchy = build_hierarchy_simple(sample_streets, admin_boundaries)
    
    # Save result
    save_hierarchy(hierarchy, output_file)
    
    logger.info("\n" + "=" * 60)
    logger.info("DONE!")
    logger.info(f"Output saved to: {output_file}")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
