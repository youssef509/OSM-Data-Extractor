#!/usr/bin/env python3
"""
Extract Turkey OSM data from PBF file
Much faster than Overpass API!
"""

import osmium
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Output directory
OUTPUT_DIR = Path("/mnt/osm-data/turkey-osm-extractor/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Regions to extract (major Turkish cities)
REGIONS = [
    'İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya',
    'Adana', 'Konya', 'Gaziantep', 'Şanlıurfa', 'Diyarbakır',
    'Mersin', 'Kayseri', 'Eskişehir', 'Trabzon', 'Erzurum'
]

# POI categories
POI_CATEGORIES = {
    'education': ['school', 'university', 'college', 'kindergarten'],
    'healthcare': ['hospital', 'clinic', 'doctors', 'pharmacy'],
    'government': ['townhall', 'police', 'post_office', 'courthouse'],
    'religious': ['place_of_worship'],
    'commercial': ['bank', 'atm', 'supermarket', 'marketplace'],
    'transportation': ['bus_station', 'ferry_terminal', 'taxi', 'fuel']
}


class TurkeyExtractor(osmium.SimpleHandler):
    """Extract streets and POIs from Turkey OSM data"""
    
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.streets = defaultdict(list)
        self.pois = defaultdict(lambda: defaultdict(list))
        self.admin_boundaries = []
        self.stats = {
            'nodes': 0,
            'ways': 0,
            'relations': 0,
            'streets': 0,
            'pois': 0
        }
    
    def node(self, n):
        """Process nodes (POIs are usually nodes)"""
        self.stats['nodes'] += 1
        
        if 'amenity' in n.tags:
            amenity = n.tags.get('amenity')
            name = n.tags.get('name', '')
            
            # Check which category this POI belongs to
            for category, amenity_types in POI_CATEGORIES.items():
                if amenity in amenity_types:
                    # Get city from tags
                    city = n.tags.get('addr:city', n.tags.get('addr:province', 'Unknown'))
                    
                    poi_data = {
                        'id': n.id,
                        'type': 'node',
                        'name': name,
                        'amenity': amenity,
                        'category': category,
                        'lat': n.location.lat,
                        'lon': n.location.lon,
                        'address': n.tags.get('addr:street', ''),
                        'city': city,
                        'postcode': n.tags.get('addr:postcode', ''),
                        'phone': n.tags.get('phone', ''),
                        'website': n.tags.get('website', ''),
                        'operator': n.tags.get('operator', '')
                    }
                    
                    self.pois[city][category].append(poi_data)
                    self.stats['pois'] += 1
                    
                    if self.stats['pois'] % 10000 == 0:
                        logger.info(f"Processed {self.stats['pois']:,} POIs...")
    
    def way(self, w):
        """Process ways (streets are ways with highway tag)"""
        self.stats['ways'] += 1
        
        # Extract streets (ways with highway tag and name)
        if 'highway' in w.tags and 'name' in w.tags:
            name = w.tags.get('name', '')
            highway_type = w.tags.get('highway', '')
            
            # Get city from tags
            city = w.tags.get('addr:city', w.tags.get('addr:province', 'Unknown'))
            
            # Calculate approximate center point
            if len(w.nodes) > 0:
                try:
                    center_lat = sum(n.location.lat for n in w.nodes) / len(w.nodes)
                    center_lon = sum(n.location.lon for n in w.nodes) / len(w.nodes)
                    
                    street_data = {
                        'id': w.id,
                        'name': name,
                        'highway_type': highway_type,
                        'city': city,
                        'surface': w.tags.get('surface', ''),
                        'lanes': w.tags.get('lanes', ''),
                        'maxspeed': w.tags.get('maxspeed', ''),
                        'oneway': w.tags.get('oneway', ''),
                        'lit': w.tags.get('lit', ''),
                        'bridge': w.tags.get('bridge', ''),
                        'tunnel': w.tags.get('tunnel', ''),
                        'center_lat': center_lat,
                        'center_lon': center_lon,
                        'nodes_count': len(w.nodes)
                    }
                    
                    self.streets[city].append(street_data)
                    self.stats['streets'] += 1
                    
                    if self.stats['streets'] % 10000 == 0:
                        logger.info(f"Processed {self.stats['streets']:,} streets...")
                        
                except Exception as e:
                    pass  # Skip ways with location issues
    
    def relation(self, r):
        """Process relations (administrative boundaries)"""
        self.stats['relations'] += 1
        
        # Extract administrative boundaries
        if r.tags.get('boundary') == 'administrative':
            admin_level = r.tags.get('admin_level', '')
            name = r.tags.get('name', '')
            
            if admin_level in ['2', '4', '6', '8']:  # Country, province, district, neighborhood
                boundary_data = {
                    'id': r.id,
                    'name': name,
                    'admin_level': admin_level,
                    'type': r.tags.get('type', ''),
                    'population': r.tags.get('population', ''),
                    'postal_code': r.tags.get('postal_code', '')
                }
                self.admin_boundaries.append(boundary_data)


def main():
    """Main extraction process"""
    logger.info("🗺️  Starting Turkey OSM PBF Extraction")
    logger.info("=" * 60)
    
    pbf_file = "/mnt/osm-data/turkey-osm-extractor/turkey-251020.osm.pbf"
    
    # Check if file exists
    if not Path(pbf_file).exists():
        logger.error(f"PBF file not found: {pbf_file}")
        return
    
    logger.info(f"Reading PBF file: {pbf_file}")
    logger.info("This will take 10-30 minutes...")
    logger.info("")
    
    # Create handler and parse file
    handler = TurkeyExtractor()
    
    try:
        handler.apply_file(pbf_file, locations=True)
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ Extraction Complete!")
        logger.info(f"Total nodes processed: {handler.stats['nodes']:,}")
        logger.info(f"Total ways processed: {handler.stats['ways']:,}")
        logger.info(f"Total relations processed: {handler.stats['relations']:,}")
        logger.info(f"Total streets extracted: {handler.stats['streets']:,}")
        logger.info(f"Total POIs extracted: {handler.stats['pois']:,}")
        logger.info("")
        
        # Save administrative boundaries
        logger.info("💾 Saving administrative boundaries...")
        admin_file = OUTPUT_DIR / "turkey_administrative.json"
        with open(admin_file, 'w', encoding='utf-8') as f:
            json.dump({
                'extracted_at': datetime.now().isoformat(),
                'total_count': len(handler.admin_boundaries),
                'boundaries': handler.admin_boundaries
            }, f, ensure_ascii=False, indent=2)
        logger.info(f"   Saved {len(handler.admin_boundaries)} boundaries")
        
        # Save streets by city
        logger.info("")
        logger.info("💾 Saving streets by city...")
        total_streets = 0
        for city, streets in handler.streets.items():
            if streets:  # Only save if we have data
                # Clean city name for filename (remove slashes and special chars)
                safe_city_name = city.replace('/', '_').replace('\\', '_').replace(':', '_')
                city_file = OUTPUT_DIR / f"{safe_city_name}_streets.json"
                with open(city_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'city': city,
                        'extracted_at': datetime.now().isoformat(),
                        'total_count': len(streets),
                        'streets': streets
                    }, f, ensure_ascii=False, indent=2)
                logger.info(f"   {city}: {len(streets):,} streets")
                total_streets += len(streets)
        
        # Save POIs by city and category
        logger.info("")
        logger.info("💾 Saving POIs by city...")
        total_pois = 0
        for city, categories in handler.pois.items():
            if categories:  # Only save if we have data
                city_pois = []
                for category, pois in categories.items():
                    city_pois.extend(pois)
                
                if city_pois:
                    # Clean city name for filename
                    safe_city_name = city.replace('/', '_').replace('\\', '_').replace(':', '_')
                    city_file = OUTPUT_DIR / f"{safe_city_name}_poi.json"
                    with open(city_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            'city': city,
                            'extracted_at': datetime.now().isoformat(),
                            'total_count': len(city_pois),
                            'pois': city_pois
                        }, f, ensure_ascii=False, indent=2)
                    logger.info(f"   {city}: {len(city_pois):,} POIs")
                    total_pois += len(city_pois)
        
        # Save summary
        logger.info("")
        logger.info("💾 Saving extraction summary...")
        summary_file = OUTPUT_DIR / "extraction_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                'extraction_date': datetime.now().isoformat(),
                'source_file': pbf_file,
                'method': 'PBF file parsing (osmium)',
                'statistics': {
                    'total_nodes': handler.stats['nodes'],
                    'total_ways': handler.stats['ways'],
                    'total_relations': handler.stats['relations'],
                    'total_streets': total_streets,
                    'total_pois': total_pois,
                    'cities_processed': len(handler.streets)
                },
                'cities': {
                    city: {
                        'streets': len(streets),
                        'pois': sum(len(pois) for pois in handler.pois.get(city, {}).values())
                    }
                    for city, streets in handler.streets.items()
                }
            }, f, ensure_ascii=False, indent=2)
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("🎉 ALL DONE!")
        logger.info(f"📊 Final Stats:")
        logger.info(f"   - Streets: {total_streets:,}")
        logger.info(f"   - POIs: {total_pois:,}")
        logger.info(f"   - Cities: {len(handler.streets)}")
        logger.info(f"📁 Output directory: {OUTPUT_DIR}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
