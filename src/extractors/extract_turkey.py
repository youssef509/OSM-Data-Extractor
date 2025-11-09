# Main extraction script
import time
import json
from datetime import datetime
from config import OUTPUT_DIR
from src.utils.utils import setup_logging, save_json
from src.extractors.extract_administrative import AdministrativeExtractor
from src.extractors.extract_streets import StreetExtractor
from src.extractors.extract_poi import POIExtractor

class TurkeyOSMExtractor:
    def __init__(self):
        self.logger = setup_logging(f"{OUTPUT_DIR}/main_extraction.log")
        self.admin_extractor = AdministrativeExtractor()
        self.street_extractor = StreetExtractor()
        self.poi_extractor = POIExtractor()
    
    def run_complete_extraction(self):
        """Run complete Turkey OSM data extraction"""
        start_time = datetime.now()
        self.logger.info("🚀 Starting complete Turkey OSM data extraction")
        
        extraction_summary = {
            'start_time': start_time.isoformat(),
            'project': 'Turkey OSM Data Extraction',
            'regions_processed': [],
            'total_data_points': 0
        }
        
        try:
            # 1. Extract administrative boundaries
            self.logger.info("📋 Step 1: Extracting administrative boundaries")
            admin_data = self.admin_extractor.extract_turkey_admin_hierarchy()
            extraction_summary['administrative_units'] = len(admin_data)
            
            time.sleep(60)
            
            # 2. Extract street networks
            self.logger.info("🛣️ Step 2: Extracting street networks")
            streets_summary = self.street_extractor.extract_all_regions_streets()
            extraction_summary['streets_summary'] = streets_summary
            extraction_summary['total_streets'] = sum(
                region['streets_count'] for region in streets_summary.values()
            )
            
            time.sleep(60)
            
            # 3. Extract Points of Interest
            self.logger.info("🏢 Step 3: Extracting Points of Interest")
            poi_summary = self.poi_extractor.extract_all_regions_poi()
            extraction_summary['poi_summary'] = poi_summary
            extraction_summary['total_poi'] = sum(
                region['total_pois'] for region in poi_summary.values()
            )
            
            # Calculate totals
            extraction_summary['total_data_points'] = (
                extraction_summary['administrative_units'] +
                extraction_summary['total_streets'] +
                extraction_summary['total_poi']
            )
            
            extraction_summary['end_time'] = datetime.now().isoformat()
            extraction_summary['duration'] = str(datetime.now() - start_time)
            
            # Save final summary
            save_json(extraction_summary, f"{OUTPUT_DIR}/complete_extraction_summary.json")
            
            self.logger.info("🎉 Complete extraction finished successfully!")
            self.logger.info(f"📊 Extraction Summary:")
            self.logger.info(f"   - Administrative units: {extraction_summary['administrative_units']}")
            self.logger.info(f"   - Total streets: {extraction_summary['total_streets']}")
            self.logger.info(f"   - Total POIs: {extraction_summary['total_poi']}")
            self.logger.info(f"   - Total data points: {extraction_summary['total_data_points']}")
            self.logger.info(f"   - Duration: {extraction_summary['duration']}")
            
        except Exception as e:
            self.logger.error(f"❌ Extraction failed: {e}")
            extraction_summary['error'] = str(e)
            extraction_summary['end_time'] = datetime.now().isoformat()
            save_json(extraction_summary, f"{OUTPUT_DIR}/extraction_failed.json")
            
        return extraction_summary

if __name__ == "__main__":
    extractor = TurkeyOSMExtractor()
    extractor.run_complete_extraction()