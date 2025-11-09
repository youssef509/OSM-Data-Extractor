# Utility functions for OSM extraction
import time
import logging
import json
from datetime import datetime
from typing import Dict, List, Any
import overpy

def setup_logging(log_file: str) -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger('osm_extractor')
    logger.setLevel(logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def save_json(data: Any, filename: str) -> None:
    """Save data to JSON file with proper encoding"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filename: str) -> Any:
    """Load data from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def execute_query_with_retry(api: overpy.Overpass, query: str, max_retries: int = 3) -> overpy.Result:
    """Execute Overpass query with retry logic"""
    for attempt in range(max_retries):
        try:
            return api.query(query)
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 30 * (attempt + 1)
                logging.warning(f"Query failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                raise e

def extract_address_from_tags(tags: Dict) -> str:
    """Extract complete address from OSM tags"""
    address_parts = [
        tags.get('addr:housenumber', ''),
        tags.get('addr:street', ''),
        tags.get('addr:city', ''),
        tags.get('addr:postcode', ''),
        tags.get('addr:country', 'Türkiye')
    ]
    return ', '.join(filter(None, address_parts))

def get_element_coordinates(element) -> Dict[str, float]:
    """Extract coordinates from OSM element"""
    if hasattr(element, 'lat') and hasattr(element, 'lon'):
        return {'lat': float(element.lat), 'lon': float(element.lon)}
    elif hasattr(element, 'nodes') and element.nodes:
        # Return center point for ways
        lats = [float(node.lat) for node in element.nodes if hasattr(node, 'lat')]
        lons = [float(node.lon) for node in element.nodes if hasattr(node, 'lon')]
        if lats and lons:
            return {
                'lat': sum(lats) / len(lats),
                'lon': sum(lons) / len(lons)
            }
    return {'lat': None, 'lon': None}