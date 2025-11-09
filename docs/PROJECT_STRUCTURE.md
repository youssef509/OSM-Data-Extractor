# Project Structure

## 📂 Directory Layout

```
OSM-Data-Extractor/
│
├── 📄 README.md                    # Main project documentation
├── 📄 LICENSE                      # MIT License
├── 📄 CONTRIBUTING.md              # Contribution guidelines
├── 📄 requirements.txt             # Python dependencies
├── 📄 setup.py                     # Package installation setup
├── 📄 config.py                    # Main configuration file
├── 📄 run_pipeline.py              # Main entry point
├── 📄 .gitignore                   # Git ignore rules
│
├── 📁 src/                         # Source code
│   ├── 📁 extractors/              # Data extraction modules
│   │   ├── extract_administrative.py  # Admin boundaries extractor
│   │   ├── extract_streets.py         # Street network extractor
│   │   ├── extract_poi.py             # Points of interest extractor
│   │   └── extract_turkey.py          # Turkey-specific orchestrator
│   │
│   └── 📁 utils/                   # Utility functions
│       └── utils.py                # Logging, file I/O, API helpers
│
├── 📁 scripts/                     # Standalone utility scripts
│   ├── build_hierarchy.py          # Build hierarchical address structure
│   ├── deploy.py                   # Deployment test script
│   └── extract_from_pbf.py         # Fast PBF file extraction
│
├── 📁 data/                        # Data directory
│   ├── 📁 raw/                     # Raw OSM data (.pbf files)
│   └── 📁 processed/               # Extracted and processed data
│
├── 📁 tests/                       # Test suite
│   ├── test_extraction.py          # Extraction tests
│   └── verify_fixes.py             # Fix verification
│
├── 📁 docs/                        # Documentation
│   ├── DEPLOYMENT.md               # Cloud deployment guide
│   └── ROADMAP.md                  # Future plans and features
│
├── 📁 config/                      # Cloud configuration scripts
│   ├── gcp-setup.sh                # GCP VM setup
│   └── vm-startup-script.sh        # VM initialization
│
├── 📁 logs/                        # Application logs (auto-created)
│
└── 📁 output/                      # Legacy output folder
    └── turkey-osm-output/          # Turkey extraction results
```

## 🎯 Key Files Explained

### Core Files

- **`run_pipeline.py`**: Main entry point to run the complete extraction pipeline
- **`config.py`**: Central configuration (regions, POI categories, paths, API settings)
- **`requirements.txt`**: All Python package dependencies

### Source Code (`src/`)

#### Extractors (`src/extractors/`)
- **`extract_administrative.py`**: Extracts administrative boundaries (provinces, districts, neighborhoods)
- **`extract_streets.py`**: Extracts street networks and road information
- **`extract_poi.py`**: Extracts points of interest (schools, hospitals, etc.)
- **`extract_turkey.py`**: Orchestrates the complete Turkey extraction process

#### Utilities (`src/utils/`)
- **`utils.py`**: Helper functions for logging, JSON file operations, API retry logic

### Utility Scripts (`scripts/`)

- **`build_hierarchy.py`**: Post-processing script to build hierarchical address structure (Province → District → Neighborhood → Street)
- **`deploy.py`**: Quick deployment test script for single-region extraction
- **`extract_from_pbf.py`**: Alternative high-speed extraction directly from PBF files (bypasses Overpass API)

### Data Directories

- **`data/raw/`**: Place downloaded OSM `.pbf` files here
- **`data/processed/`**: Output location for extracted JSON files
- **`logs/`**: Application logs (auto-created)

### Documentation (`docs/`)

- **`DEPLOYMENT.md`**: Comprehensive cloud deployment guide (GCP, AWS, Azure)
- **`ROADMAP.md`**: Project roadmap and future feature plans

### Tests (`tests/`)

- **`test_extraction.py`**: Unit tests for extraction functions
- **`verify_fixes.py`**: Validation script to ensure data quality

## 🚀 Quick Start Workflow

1. **Setup**: `pip install -r requirements.txt`
2. **Configure**: Edit `config.py` to set regions and parameters
3. **Run**: `python run_pipeline.py`
4. **Check Output**: Results in `data/processed/`
5. **Build Hierarchy** (optional): `python scripts/build_hierarchy.py`

## 📊 Data Flow

```
Raw OSM Data (.pbf)
    ↓
[Extractors] → Administrative Boundaries
             → Street Networks
             → Points of Interest
    ↓
Processed JSON Files
    ↓
[build_hierarchy.py]
    ↓
Hierarchical Address Structure
```

## 🔧 Development

- All source code is in `src/`
- Tests are in `tests/`
- Configuration is centralized in `config.py`
- Use `setup.py` to install as a package: `pip install -e .`

## 📝 Notes

- The project uses UTF-8 encoding throughout for international character support
- All paths use `pathlib.Path` for cross-platform compatibility
- Logging is implemented across all modules for easy debugging
- Error handling includes automatic retries for API requests
