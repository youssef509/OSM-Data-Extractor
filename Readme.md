# OSM Data Extractor

> A scalable, production-ready tool for extracting and processing OpenStreetMap data with hierarchical geographic structure.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenStreetMap](https://img.shields.io/badge/Data-OpenStreetMap-7ebc6f.svg)](https://www.openstreetmap.org)

## 🌍 Overview

OSM Data Extractor is a comprehensive pipeline for extracting, processing, and structuring geographic data from OpenStreetMap. Currently focused on **Turkey** 🇹🇷 as the primary dataset, with plans to expand to additional countries.

The tool extracts:
- **Administrative boundaries** (country, region, province, district, neighborhood)
- **Street networks** organized by region
- **Points of Interest** (POI) including education, healthcare, government facilities, and more

## ✨ Features

- 🗺️ **Hierarchical Data Structure**: Organized geographic data with proper parent-child relationships
- 🔄 **Retry Logic**: Built-in error handling and automatic retries for API requests
- 📊 **Progress Tracking**: Real-time logging and progress monitoring
- 🌐 **UTF-8 Support**: Full support for international characters (Turkish, Arabic, etc.)
- ⚡ **Batch Processing**: Efficient data extraction with configurable batch sizes
- 🔧 **Modular Design**: Easy to extend for additional countries or data types
- ☁️ **Cloud-Ready**: Deployable on GCP, AWS, or Azure

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/youssef509/OSM-Data-Extractor.git
cd OSM-Data-Extractor

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run the complete extraction pipeline
python run_pipeline.py

# Or run individual extractors
python -m src.extractors.extract_administrative
python -m src.extractors.extract_streets
python -m src.extractors.extract_poi
```

## 📁 Project Structure

```
OSM-Data-Extractor/
├── src/
│   ├── extractors/           # Data extraction modules
│   │   ├── extract_administrative.py
│   │   ├── extract_streets.py
│   │   ├── extract_poi.py
│   │   └── extract_turkey.py
│   └── utils/                # Utility functions
│       └── utils.py
├── data/
│   ├── raw/                  # Raw OSM data files
│   └── processed/            # Processed output files
├── config/                   # Deployment configurations
├── tests/                    # Test suite
├── docs/                     # Documentation
├── config.py                 # Application configuration
├── run_pipeline.py           # Main entry point
├── requirements.txt          # Python dependencies
└── README.md
```

## 📊 Output Format

### Administrative Boundaries
```json
{
  "type": "province",
  "name": "İstanbul",
  "admin_level": 4,
  "children": [
    {
      "type": "district",
      "name": "Kadıköy",
      "admin_level": 6
    }
  ]
}
```

### Streets
```json
{
  "region": "İstanbul",
  "streets": [
    {
      "name": "Bağdat Caddesi",
      "type": "primary",
      "surface": "asphalt"
    }
  ]
}
```

## ⚙️ Configuration

Edit `config.py` to customize:
- **Regions**: Add or remove geographic regions
- **POI Categories**: Define custom points of interest
- **API Settings**: Adjust timeout, retries, and batch sizes

```python
# Example: Add a new region
REGIONS = [
    'İstanbul', 'Ankara', 'İzmir',
    'Your-New-Region'  # Add here
]
```

## 🌐 Expanding to Other Countries

The project is designed to be country-agnostic. To add support for a new country:

1. Create a new extractor in `src/extractors/extract_[country].py`
2. Update `config.py` with country-specific regions
3. Run the pipeline with your new extractor

**Coming Soon**: France 🇫🇷, Germany 🇩🇪, Spain 🇪🇸, and more!

## ☁️ Cloud Deployment

<details>
<summary><b>Google Cloud Platform (GCP)</b></summary>

```bash
# Run the GCP setup script
chmod +x config/gcp-setup.sh
./config/gcp-setup.sh

# SSH to VM
gcloud compute ssh --zone=us-central1-a osm-extractor

# Run the pipeline
python run_pipeline.py
```

See [docs/GCP_DEPLOYMENT.md](docs/GCP_DEPLOYMENT.md) for detailed instructions.
</details>

<details>
<summary><b>AWS / Azure</b></summary>

Documentation coming soon!
</details>

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_extraction.py
```

## 📈 Performance

- **Turkey Complete Dataset**: ~24-48 hours
- **Single Region**: ~1-2 hours
- **Memory Usage**: ~2-4 GB
- **Storage**: ~250 GB for full Turkey dataset

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Data sourced from [OpenStreetMap](https://www.openstreetmap.org) contributors
- Built with [OverPy](https://github.com/DinoTools/python-overpy) and [osmium](https://osmcode.org/pyosmium/)

## 📧 Contact

Youssef - [@youssef509](https://github.com/youssef509)

Project Link: [https://github.com/youssef509/OSM-Data-Extractor](https://github.com/youssef509/OSM-Data-Extractor)

---

**Note**: This project currently focuses on Turkey as the primary dataset. Support for additional countries is planned and contributions are welcome!