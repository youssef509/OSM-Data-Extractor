# Points of Interest extraction
import json
import time
from typing import Dict, List
import overpy
from config import CONFIG, POI_CATEGORIES, REGIONS, OUTPUT_DIR
from src.utils.utils import setup_logging, save_json, execute_query_with_retry, get_element_coordinates

class POIExtractor:
    def __init__(self):
        self.api = overpy.Overpass()
        self.logger = setup_logging(f"{OUTPUT_DIR}/poi_extraction.log")
    
    def extract_poi_for_region(self, region_name: str, category: str, filters: List[str]) -> List[Dict]:
        """Extract POIs for a specific region and category"""
        pois = []
        
        for filter_str in filters:
            query = f"""
            [out:json][timeout:200];
            area["name"="{region_name}"]["admin_level"="4"]->.searchArea;
            
            (
              node[{filter_str}](area.searchArea);
              way[{filter_str}](area.searchArea);
              relation[{filter_str}](area.searchArea);
            );
            out body;
            >;
            out skel qt;
            """
            
            try:
                result = execute_query_with_retry(self.api, query)
                
                for element in result.nodes + result.ways + result.relations:
                    poi_data = {
                        'id': element.id,
                        'type': element.__class__.__name__.lower(),
                        'name': element.tags.get('name', ''),
                        'category': category,
                        'subcategory': filter_str,
                        'coordinates': get_element_coordinates(element),
                        'postal_code': element.tags.get('postal_code', ''),
                        'address': element.tags.get('addr:street', ''),
                        'city': element.tags.get('addr:city', ''),
                        'operator': element.tags.get('operator', ''),
                        'website': element.tags.get('website', ''),
                        'phone': element.tags.get('phone', ''),
                        'full_tags': dict(element.tags)
                    }
                    pois.append(poi_data)
                
                self.logger.info(f"  - {region_name}/{category}/{filter_str}: {len(result.nodes + result.ways + result.relations)} POIs")
                time.sleep(5)  # Rate limiting
                
            except Exception as e:
                self.logger.error(f"Error in {region_name}/{category}/{filter_str}: {e}")
                continue
        
        return pois
    
    def extract_all_poi_for_region(self, region_name: str) -> Dict:
        """Extract all POI categories for a region"""
        self.logger.info(f"Extracting POIs for {region_name}")
        
        region_pois = {}
        
        for category, config in POI_CATEGORIES.items():
            try:
                pois = self.extract_poi_for_region(
                    region_name, 
                    category, 
                    config['filters']
                )
                region_pois[category] = pois
                
                self.logger.info(f"✅ {region_name}/{category}: {len(pois)} POIs")
                time.sleep(10)  # Be nice to API
                
            except Exception as e:
                self.logger.error(f"❌ Failed to extract {category} for {region_name}: {e}")
                region_pois[category] = []
        
        # Save region POI data
        filename = f"{OUTPUT_DIR}/{region_name}_poi.json"
        save_json(region_pois, filename)
        
        total_pois = sum(len(pois) for pois in region_pois.values())
        self.logger.info(f"✅ {region_name}: {total_pois} total POIs saved")
        
        return region_pois
    
    def extract_all_regions_poi(self) -> Dict:
        """Extract POIs for all regions"""
        self.logger.info("Starting POI extraction for all regions")
        
        summary = {}
        
        for region in REGIONS:  # Process all regions
            try:
                region_pois = self.extract_all_poi_for_region(region)
                total_pois = sum(len(pois) for pois in region_pois.values())
                
                summary[region] = {
                    'total_pois': total_pois,
                    'categories': {cat: len(pois) for cat, pois in region_pois.items()},
                    'status': 'success'
                }
                
                time.sleep(30)  # Longer delay between regions
                
            except Exception as e:
                self.logger.error(f"❌ Failed to process {region}: {e}")
                summary[region] = {
                    'total_pois': 0,
                    'status': 'failed',
                    'error': str(e)
                }
        
        # Save POI extraction summary
        save_json(summary, f"{OUTPUT_DIR}/poi_extraction_summary.json")
        
        total_all_pois = sum(region['total_pois'] for region in summary.values())
        self.logger.info(f"🎉 POI extraction completed! Total POIs: {total_all_pois}")
        
        return summary

if __name__ == "__main__":
    extractor = POIExtractor()
    extractor.extract_all_regions_poi()