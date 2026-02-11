---
inclusion: always
---

# Structure Patterns for Advanced-MRI Repository

## Repository Organization

### Actual Directory Structure
```
advanced-mri/
├── README.md                    # Repository overview for CLARiTI/SCAN workflows
├── ImageUploading/              # DICOM ZIP ingestion utility
│   ├── README.md                # Component documentation with usage examples
│   ├── fwImageUpload.py         # Main script with FlywheelConnector and UploadImageData classes
│   └── fwImageUpload.conf       # JSON config with APIKey and project prefix
├── QSMxT/                       # Flywheel gear for MEGRE → QSM processing
│   ├── README.md                # Gear documentation and testing instructions
│   ├── Dockerfile               # Container based on vnmd/qsmxt_8.2.0
│   ├── manifest.json            # Flywheel gear manifest with config options
│   └── run.py                   # Main processing script with flywheel_run()
└── QC Viewer Protocol/          # Quality control configuration
    ├── README.md                # QC protocol documentation
    ├── ViewerConfig.json        # Viewer UI configuration with mouse actions and presets
    └── ViewerForm.json          # QC assessment form with conditional logic
```

### File Naming Conventions (Actual Implementation)

#### Python Files
- Use snake_case for module names: `fwImageUpload.py`, `run.py`
- Use PascalCase for class names: `FlywheelConnector`, `UploadImageData`
- Use snake_case for method names: `setProject`, `uploadImages`, `CollectImageInformation`
- Use descriptive function names: `flywheel_run()`, `run_cmd()`

#### Configuration Files
- JSON format with descriptive names: `fwImageUpload.conf`, `manifest.json`
- Viewer configurations: `ViewerConfig.json`, `ViewerForm.json`
- Container files: `Dockerfile` (single-stage builds)

#### Documentation Files
- Component README files: `README.md` in each directory
- Repository overview: top-level `README.md`

### Code Organization Patterns (Actual Implementation)

#### Module Structure (ImageUploading Pattern)
```python
#!/usr/bin/env python3

import argparse
import json
import logging
import sys
import zipfile
import tempfile
from typing import Dict, List, Optional

import pydicom
import flywheel

from os import path
from fw_client import FWClient  # External dependency

###############################################################################
# Logging Setup
###############################################################################

logger = logging.getLogger("fw_uploader")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(handler)

###############################################################################
# Main Classes
###############################################################################

class FlywheelConnector:
    """Dual client wrapper for Flywheel SDK and REST API."""
    
    def __init__(self, api_key: str):
        self.APIKey: str = api_key
        self.project = None
        self.RestClient: FWClient = FWClient(api_key=self.APIKey)
        self.SDKClient: flywheel.Client = flywheel.Client(self.APIKey)
        self.imageList: List = []
        self.sessionList: List = []
```

#### Class Organization (Actual Pattern)
```python
class UploadImageData:
    """
    Handles DICOM ZIP processing and Flywheel upload.
    
    Parameters
    ----------
    fc : FlywheelConnector
        Initialized connector with project selected
    fileSpec : str
        Path to ZIP archive containing DICOM files
    """
    
    def __init__(self, fc: FlywheelConnector, fileSpec: str):
        self.fc = fc
        self.fileSpec = fileSpec
        try:
            self.zip = zipfile.ZipFile(fileSpec)
        except Exception as e:
            logger.error(f"Could not open zip file '{fileSpec}': {e}")
            raise
        self.baseName, _ = path.splitext(path.basename(fileSpec))
    
    def uploadImages(self, segIndex: int) -> None:
        """Main processing method with detailed workflow."""
        # Implementation with extensive logging and error handling
```

### Configuration Management (Actual Implementation)

#### ImageUploading Configuration (JSON Format)
```json
{
    "APIKey": "naccdata.flywheel.io:djErt5O2eKtEvoK1rJdpO6xbbHO5jn_ot0lqXUvTvZ66Ph_9LKI2jy3Sg",
    "project": "advanced-mri"
}
```
- Simple flat structure with embedded credentials
- Project specified as prefix string for matching
- No environment variable support (credentials in file)

#### QSMxT Flywheel Gear Manifest
```json
{
  "name": "qsmxt",
  "label": "QSMxT for Automated Quantitative Susceptibility Mapping",
  "description": "QSMxT is an end-to-end pipeline for Quantitative Susceptibility Mapping (QSM).",
  "author": "Ashley Stewart",
  "maintainer": "NACC <nacchelp@uw.edu>",
  "version": "qsmxt_8.1.3_3",
  "config": {
    "premade": {
      "description": "Premade pipeline configuration",
      "type": "string",
      "default": "gre",
      "enum": ["gre", "epi", "bet", "fast", "body", "nextqsm"]
    }
  },
  "inputs": {
    "input_file": {
      "base": "file",
      "type": {"enum": ["dicom"]},
      "description": "QSM image (in a compressed .ZIP folder)"
    }
  },
  "command": "python3 /flywheel/v0/run.py"
}
```

#### QC Viewer Configuration Patterns
```json
{
    "showStudyList": true,
    "contourUnique": false,
    "mouseActions": [
        {"toolName": "Zoom", "button": "middle"},
        {"toolName": "Pan", "button": "right"}
    ],
    "wwwcPresets": {
        "1": {"description": "Soft tissue", "window": "550", "level": "40"}
    }
}
```

### Dependency Management

#### Requirements Structure
```
# requirements.txt - Production dependencies
flywheel-sdk>=16.3.0,<17.0.0
pydicom>=2.3.0,<3.0.0
numpy>=1.21.0,<2.0.0
requests>=2.28.0,<3.0.0

# requirements-dev.txt - Development dependencies
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=0.991

# requirements-test.txt - Testing dependencies
pytest-mock>=3.8.0
responses>=0.21.0
factory-boy>=3.2.0
```

#### Dependency Pinning Strategy
- **Production**: Pin major and minor versions (`>=1.2.0,<1.3.0`)
- **Development**: Pin major versions only (`>=1.0.0,<2.0.0`)
- **Security**: Always pin exact versions for security-critical dependencies

### Error Handling Structure (Actual Implementation)

#### Current Error Handling Pattern
```python
def setProject(self, project_name: str) -> None:
    """Set project with error logging before raising."""
    try:
        project_list = self.RestClient.get("/api/projects")
    except Exception as e:
        logger.error(f"Error retrieving project list: {e}")
        raise

    for p in project_list:
        if p.label.startswith(project_name):
            try:
                self.project = self.SDKClient.get_project(p._id)
            except Exception as e:
                logger.error(f"Cannot fetch project '{project_name}' via SDK: {e}")
                raise
            logger.info(f"Project set: {self.project.label}")
            return

    raise ValueError(f"No project found starting with '{project_name}'")
```

#### QSMxT Error Handling Pattern
```python
def run_cmd(cmd: list[str], description: str):
    """Run shell command with logging and error trapping."""
    print(f"\n[CMD] {description}: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError(f"Command failed during: {description}")

    return result
```

#### Error Handling Conventions
- Log errors with context before raising: `logger.error(f"Error message: {e}")` then `raise`
- Use generic Exception types, not custom exception hierarchy
- Include operation context in error messages
- Print stdout/stderr for subprocess failures

### Testing Structure

#### Test Organization
```
tests/
├── conftest.py                  # Pytest configuration and fixtures
├── unit/                        # Unit tests
│   ├── test_dicom_processor.py  # Test individual modules
│   ├── test_flywheel_client.py  # Test API clients
│   └── test_config_manager.py   # Test configuration handling
├── integration/                 # Integration tests
│   ├── test_full_pipeline.py    # End-to-end pipeline tests
│   ├── test_flywheel_integration.py  # External service tests
│   └── test_container_deployment.py  # Container tests
└── fixtures/                    # Test data and mocks
    ├── sample_dicom/            # Sample DICOM files
    ├── config_examples/         # Configuration examples
    └── expected_outputs/        # Expected test results
```

#### Test Naming Conventions
```python
class TestFlywheelConnector:
    """Test class for FlywheelConnector."""
    
    def test_init_with_valid_config(self):
        """Test initialization with valid configuration."""
        pass
    
    def test_init_with_invalid_config_raises_error(self):
        """Test initialization with invalid config raises appropriate error."""
        pass
    
    def test_connect_to_flywheel_success(self):
        """Test successful connection to Flywheel."""
        pass
    
    def test_connect_to_flywheel_failure_retries(self):
        """Test connection failure triggers retry logic."""
        pass
```

### Documentation Structure

#### README Template
```markdown
# Component Name

Brief description of what this component does.

## Quick Start

```bash
# Installation
pip install -r requirements.txt

# Basic usage
python component.py --config config.json --input data.zip
```

## Configuration

[Configuration details with examples]

## Usage Examples

[Multiple usage scenarios]

## Testing

[How to run tests]

## Troubleshooting

[Common issues and solutions]
```

#### API Documentation Structure
- Use docstrings for all public APIs
- Generate documentation with Sphinx or similar
- Include usage examples in docstrings
- Maintain separate API reference documentation

### Version Control Standards

#### Git Workflow
- Use feature branches for all changes
- Require pull requests for main branch
- Use conventional commit messages
- Tag releases with semantic versioning

#### Commit Message Format
```
type(scope): brief description

Longer description if needed, explaining what and why.

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Deployment Structure

#### Container Organization
```dockerfile
# Multi-stage build pattern
FROM python:3.9-slim as base
# Base dependencies

FROM base as development
# Development tools and dependencies

FROM base as production
# Production-only setup
```

#### Configuration Management
- Use environment variables for runtime configuration
- Provide configuration templates and examples
- Validate configuration at startup
- Support configuration hot-reloading where appropriate