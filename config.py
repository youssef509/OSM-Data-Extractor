# Configuration for OSM Data Extraction
import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "processed"
RAW_DATA_DIR = DATA_DIR / "raw"
LOG_DIR = BASE_DIR / "logs"

# Create directories
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Extraction configuration
CONFIG = {
    'timeout': 600,  # 10 minutes per query
    'max_retries': 3,
    'retry_delay': 30,
    'batch_size': 100
}

# Turkey regions to process
REGIONS = [
    'İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya', 'Adana',
    'Konya', 'Gaziantep', 'Şanlıurfa', 'Diyarbakır', 'Mersin',
    'Kayseri', 'Eskişehir', 'Trabzon', 'Erzurum'
]

# Administrative levels for Turkey
ADMIN_LEVELS = {
    '1': 'country',
    '2': 'region', 
    '4': 'province',
    '6': 'district',
    '8': 'neighborhood',
    '10': 'quarter'
}

# POI categories
POI_CATEGORIES = {
    'education': {
        'filters': ['amenity=university', 'amenity=school', 'amenity=college', 'amenity=kindergarten'],
        'tags': ['name', 'operator', 'capacity']
    },
    'healthcare': {
        'filters': ['amenity=hospital', 'amenity=clinic', 'amenity=pharmacy', 'amenity=doctors'],
        'tags': ['name', 'healthcare', 'beds']
    },
    'government': {
        'filters': ['amenity=townhall', 'office=government', 'amenity=courthouse'],
        'tags': ['name', 'government']
    },
    'religious': {
        'filters': ['amenity=place_of_worship', 'building=mosque', 'building=church'],
        'tags': ['name', 'religion', 'denomination']
    },
    'commercial': {
        'filters': ['shop=supermarket', 'amenity=bank', 'amenity=restaurant', 'amenity=cafe'],
        'tags': ['name', 'cuisine', 'operator']
    },
    'transportation': {
        'filters': ['amenity=bus_station', 'railway=station', 'aeroway=airport'],
        'tags': ['name', 'operator', 'public_transport']
    }
}