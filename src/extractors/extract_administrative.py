# Administrative boundaries extraction
import json
import time
from typing import Dict, List
import overpy
from config import CONFIG, ADMIN_LEVELS, OUTPUT_DIR
from src.utils.utils import setup_logging, save_json, execute_query_with_retry

class AdministrativeExtractor:
    def __init__(self):
        self.api = overpy.Overpass()
        self.logger = setup_logging(f"{OUTPUT_DIR}/admin_extraction.log")
    
    def extract_turkey_admin_hierarchy(self) -> Dict:
        """Extract complete administrative hierarchy for Turkey"""
        self.logger.info("Starting Turkey administrative hierarchy extraction")
        
        query = """
        [out:json][timeout:600];
        area["name:en"="Turkey"]["admin_level"="2"]->.country;
        
        (
          relation["boundary"="administrative"](area.country);
        );
        out body;
        >;
        out skel qt;
        """
        
        try:
            result = execute_query_with_retry(self.api, query)
            admin_data = {}
            
            for relation in result.relations:
                admin_level = relation.tags.get('admin_level', '')
                name = relation.tags.get('name', '')
                
                if name and admin_level in ADMIN_LEVELS:
                    admin_data[relation.id] = {
                        'id': relation.id,
                        'name': name,
                        'admin_level': admin_level,
                        'admin_type': ADMIN_LEVELS[admin_level],
                        'postal_code': relation.tags.get('postal_code', ''),
                        'population': relation.tags.get('population', ''),
                        'wikidata': relation.tags.get('wikidata', ''),
                        'wikipedia': relation.tags.get('wikipedia', ''),
                        'area': relation.tags.get('area', ''),
                        'members_count': len(relation.members),
                        'tags': dict(relation.tags)
                    }
            
            # Save administrative data
            save_json(admin_data, f"{OUTPUT_DIR}/turkey_administrative.json")
            self.logger.info(f"✅ Administrative data saved: {len(admin_data)} entries")
            
            return admin_data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to extract administrative data: {e}")
            return {}
    
    def extract_region_admin_boundaries(self, region_name: str) -> Dict:
        """Extract administrative boundaries for a specific region"""
        self.logger.info(f"Extracting admin boundaries for {region_name}")
        
        query = f"""
        [out:json][timeout:300];
        area["name"="{region_name}"]["admin_level"="4"]->.searchArea;
        
        (
          relation["boundary"="administrative"](area.searchArea);
        );
        out body;
        >;
        out skel qt;
        """
        
        try:
            result = execute_query_with_retry(self.api, query)
            region_admin_data = []
            
            for relation in result.relations:
                admin_data = {
                    'id': relation.id,
                    'name': relation.tags.get('name', ''),
                    'admin_level': relation.tags.get('admin_level', ''),
                    'admin_type': ADMIN_LEVELS.get(relation.tags.get('admin_level', ''), 'unknown'),
                    'postal_code': relation.tags.get('postal_code', ''),
                    'boundary_type': relation.tags.get('boundary', ''),
                    'members': [
                        {'type': m.type, 'ref': m.ref, 'role': m.role}
                        for m in relation.members
                    ]
                }
                region_admin_data.append(admin_data)
            
            # Save region admin data
            filename = f"{OUTPUT_DIR}/{region_name}_administrative.json"
            save_json(region_admin_data, filename)
            
            self.logger.info(f"✅ {region_name}: {len(region_admin_data)} admin boundaries saved")
            return region_admin_data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to extract admin boundaries for {region_name}: {e}")
            return []

if __name__ == "__main__":
    extractor = AdministrativeExtractor()
    extractor.extract_turkey_admin_hierarchy()