# Contributing to OSM Data Extractor

Thank you for considering contributing to OSM Data Extractor! 🎉

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version)

### Suggesting Features

Feature suggestions are welcome! Please:
- Check if the feature has already been requested
- Clearly describe the use case
- Explain how it would benefit the project

### Adding New Countries

To add support for a new country:

1. **Fork the repository**
2. **Create a new extractor** in `src/extractors/extract_[country].py`
3. **Update configuration** in `config.py`:
   ```python
   # Add regions for the new country
   [COUNTRY]_REGIONS = [
       'Region1', 'Region2', ...
   ]
   ```
4. **Test thoroughly** with a small region first
5. **Submit a pull request** with:
   - Clear description of changes
   - Example output
   - Any special considerations

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and modular

### Testing

Before submitting a PR:
```bash
# Run tests
python -m pytest tests/

# Test on a small dataset first
python run_pipeline.py
```

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/OSM-Data-Extractor.git
cd OSM-Data-Extractor

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create a new branch
git checkout -b feature/your-feature-name
```

## Pull Request Process

1. Update the README.md if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update documentation
5. Submit PR with clear description

## Questions?

Feel free to open an issue for any questions or clarifications!

---

Thank you for contributing! 🙌
