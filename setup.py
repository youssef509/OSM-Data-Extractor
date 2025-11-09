"""Setup configuration for OSM Data Extractor."""
from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "Readme.md").read_text(encoding='utf-8')

setup(
    name="osm-data-extractor",
    version="1.0.0",
    author="Youssef",
    description="A scalable tool for extracting OpenStreetMap data with hierarchical structure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/youssef509/OSM-Data-Extractor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "overpy>=0.6",
        "requests>=2.31.0",
        "pandas>=2.0.3",
        "shapely>=2.0.1",
        "ujson>=5.8.0",
        "tqdm>=4.65.0",
        "osmium",
    ],
    entry_points={
        "console_scripts": [
            "osm-extract=run_pipeline:main",
        ],
    },
)
