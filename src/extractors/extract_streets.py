# Street network extraction
import json
import time
from typing import Dict, List
import overpy
from config import CONFIG, REGIONS, OUTPUT_DIR
from src.utils.utils import setup_logging, save_json, execute_query_with_retry

class StreetExtractor:
    def __init__(self):
        self.api = overpy.Overpass()
        self.logger = setup_logging(f"{OUTPUT_DIR}/street_extraction.log")
    
    def extract_region_streets(self, region_name: str) -> List[Dict]:
        """Extract complete street network for a region"""
        self.logger.info(f"Extracting streets for {region_name}")
        
        query = f"""
        [out:json][timeout:300];
        area["name"="{region_name}"]["admin_level"="4"]->.searchArea;
        
        (
          way["highway"]["name"](area.searchArea);
        );
        out body;
        >;
        out skel qt;
        """
        
        try:
            result = execute_query_with_retry(self.api, query)
            streets = []
            
            for way in result.ways:
                street_data = {
                    'id': way.id,
                    'name': way.tags.get('name', ''),
                    'highway_type': way.tags.get('highway', ''),
                    'postal_code': way.tags.get('postal_code', ''),
                    'length': way.tags.get('length', ''),
                    'lanes': way.tags.get('lanes', ''),
                    'maxspeed': way.tags.get('maxspeed', ''),
                    'surface': way.tags.get('surface', ''),
                    'lit': way.tags.get('lit', ''),
                    'oneway': way.tags.get('oneway', ''),
                    'bridge': way.tags.get('bridge', ''),
                    'tunnel': way.tags.get('tunnel', ''),
                    'geometry': [
                        {'lat': float(node.lat), 'lon': float(node.lon)} 
                        for node in way.nodes
                        if hasattr(node, 'lat') and hasattr(node, 'lon')
                    ],
                    'nodes_count': len(way.nodes),
                    'full_tags': dict(way.tags)
                }
                streets.append(street_data)
            
            # Save streets data
            filename = f"{OUTPUT_DIR}/{region_name}_streets.json"
            save_json(streets, filename)
            
            self.logger.info(f"✅ {region_name}: {len(streets)} streets saved")
            return streets
            
        except Exception as e:
            self.logger.error(f"❌ Failed to extract streets for {region_name}: {e}")
            return []
    
    def extract_all_regions_streets(self) -> Dict:
        """Extract streets for all regions"""
        self.logger.info("Starting street extraction for all regions")
        
        summary = {}
        
        for region in REGIONS:
            try:
                streets = self.extract_region_streets(region)
                summary[region] = {
                    'streets_count': len(streets),
                    'status': 'success'
                }
                
                # Be nice to the API
                time.sleep(CONFIG['retry_delay'])
                
            except Exception as e:
                self.logger.error(f"❌ Failed to process {region}: {e}")
                summary[region] = {
                    'streets_count': 0,
                    'status': 'failed',
                    'error': str(e)
                }
        
        # Save extraction summary
        save_json(summary, f"{OUTPUT_DIR}/streets_extraction_summary.json")
        
        total_streets = sum(region['streets_count'] for region in summary.values())
        self.logger.info(f"🎉 Street extraction completed! Total streets: {total_streets}")
        
        return summary

if __name__ == "__main__":
    extractor = StreetExtractor()
    extractor.extract_all_regions_streets()