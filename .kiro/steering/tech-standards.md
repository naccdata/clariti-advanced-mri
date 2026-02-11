---
inclusion: always
---

# Tech Patterns for Advanced-MRI Repository

## Development Environment (Actual Implementation)

### Python Environment
- **Version**: Python 3.8+ (as specified in ImageUploading README)
- **Dependencies**: Listed in README files, no requirements.txt files present
- **Import Style**: Mix of `from typing import List` and `list[str]` (Python 3.9+ style)
- **Path Handling**: Mix of `os.path` (ImageUploading) and `pathlib.Path` (QSMxT)

### Actual Dependencies Used
```python
# ImageUploading dependencies
import pydicom
import flywheel
from fw_client import FWClient  # External dependency not in repo

# QSMxT dependencies  
import flywheel
import zipfile
import subprocess
import glob
from pathlib import Path

# Common standard library
import json
import logging
import tempfile
import sys
```

## Code Quality Patterns (Current Implementation)

### Type Hints (Inconsistent Usage)
```python
# ImageUploading style - partial type hints
class FlywheelConnector:
    def __init__(self, api_key: str):
        self.APIKey: str = api_key
        self.imageList: List = []  # Generic List, not List[specific_type]
        
    def setProject(self, project_name: str) -> None:
        # Implementation

# QSMxT style - modern Python 3.9+ syntax
def run_cmd(cmd: list[str], description: str):
    """Run shell command with logging."""
    # Implementation
```

### Logging Standards (Actual Implementation)
```python
# Module-level logger setup (ImageUploading pattern)
logger = logging.getLogger("fw_uploader")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(handler)

# QSMxT pattern - simple print statements
def run_cmd(cmd: list[str], description: str):
    print(f"\n[CMD] {description}: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
```

### Error Handling Patterns (Actual Implementation)
```python
# Standard pattern: log then raise
try:
    project_list = self.RestClient.get("/api/projects")
except Exception as e:
    logger.error(f"Error retrieving project list: {e}")
    raise

# QSMxT pattern: raise with context
if result.returncode != 0:
    print(result.stderr)
    raise RuntimeError(f"Command failed during: {description}")
```

## Medical Imaging Technology (Actual Implementation)

### DICOM Processing Requirements (Current Patterns)
```python
# Efficient metadata extraction (ImageUploading pattern)
meta = pydicom.dcmread(path.join(tmpDir, f), stop_before_pixels=True)

# Extract key metadata using tag tuples
suid = meta.get((0x0020, 0x000E)).value  # SeriesInstanceUID
studyDate = meta.get((0x0008, 0x0020)).value  # StudyDate
seriesNumber = meta.get((0x0020, 0x0011)).value  # SeriesNumber

# Group files by SeriesInstanceUID
zipFiles: Dict[str, List[str]] = {}
zipFiles.setdefault(suid, []).append(f)
```

### Subject Identification Pattern (NACC-specific)
```python
# Extract subject labels from file paths
segments = f.split("/")
subject_label = next((s for s in segments if "NACC" in s), None)

if subject_label is None:
    logger.warning(f"No NACC ID in file path: {f}")
    continue

acqList.setdefault(subject_label, []).append(f)
```

### Flywheel Integration Standards (Dual Client Approach)
```python
class FlywheelConnector:
    """Dual client wrapper for comprehensive API access."""
    
    def __init__(self, api_key: str):
        self.APIKey: str = api_key
        self.RestClient: FWClient = FWClient(api_key=self.APIKey)  # REST API
        self.SDKClient: flywheel.Client = flywheel.Client(self.APIKey)  # SDK
        
    def setProject(self, project_name: str) -> None:
        """Find project by prefix matching."""
        project_list = self.RestClient.get("/api/projects")  # Use REST for queries
        
        for p in project_list:
            if p.label.startswith(project_name):  # Prefix matching
                self.project = self.SDKClient.get_project(p._id)  # Use SDK for objects
                return
```

### Container Technology Standards (Actual Implementation)

#### Dockerfile Pattern (QSMxT)
```dockerfile
# Single-stage build from existing base image
FROM vnmd/qsmxt_8.2.0

# Install Python dependencies
RUN pip3 install flywheel-sdk

# Copy and set permissions
COPY run.py /flywheel/v0/run.py
RUN chmod +x /flywheel/v0/run.py

# Simple entrypoint
ENTRYPOINT ["python3", "/flywheel/v0/run.py"]
```

#### Flywheel Gear Integration
```python
def flywheel_run():
    """Main gear execution using Flywheel context."""
    with flywheel.GearContext() as context:
        config = context.config
        dicom_megre_zip = context.get_input_path("input_file")
        dicom_t1w_zip = context.get_input_path("anatomical")
        out_dir = context.output_dir
        
        # Processing workflow
```

## Processing Technology (Actual Implementation)

### Subprocess Execution Pattern (QSMxT)
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

# Usage examples
run_cmd(["dicom-convert", "/dicoms/", "/bids/", "--auto_yes"], 
        description="DICOM → BIDS conversion (MEGRE)")

run_cmd(["dcm2niix", "-o", str(t1_output_dir), str(t1_input_dir)], 
        description="T1w DICOM → NIfTI conversion")
```

### File Operations (Mixed Patterns)
```python
# ImageUploading - os.path style
from os import path
self.baseName, _ = path.splitext(path.basename(fileSpec))
meta = pydicom.dcmread(path.join(tmpDir, f), stop_before_pixels=True)

# QSMxT - pathlib style  
from pathlib import Path
anat_list = list(Path("/bids/").glob("sub*/ses*/anat/*.nii"))
qsm_files = glob.glob("/qsm/**/*.nii", recursive=True)
```

### Temporary File Management (Current Pattern)
```python
# ImageUploading pattern
with tempfile.TemporaryDirectory() as tmpDir:
    zipFiles: Dict[str, List[str]] = {}
    
    for f in file_list:
        self.zip.extract(f, path=tmpDir)
        meta = pydicom.dcmread(path.join(tmpDir, f), stop_before_pixels=True)
        # Process files
    # Automatic cleanup when context exits
```

### Configuration Loading (Actual Implementation)
```python
# Simple JSON loading without validation
def load_config(config_path: str) -> dict:
    """Load JSON configuration file."""
    with open(config_path, 'r') as f:
        return json.load(f)

# Usage
config = load_config("fwImageUpload.conf")
api_key = config["APIKey"]  # Direct access, no validation
project = config["project"]
```

## Quality Control Technology Standards (Actual Implementation)

### QC Form Structure (JSON Schema)
```json
{
    "studyForm": {
        "components": [
            {
                "html": "<h1>Reconstruction</h1>"
            },
            {
                "label": "Is the series complete?",
                "key": "series_complete",
                "type": "dropdown",
                "values": [
                    {"value": "Complete", "label": "Complete"},
                    {"value": "Incomplete", "label": "Incomplete"}
                ]
            },
            {
                "label": "",
                "key": "series_complete_comment",
                "type": "textarea",
                "hidden": true,
                "conditional": {
                    "json": {
                        "==": [{"var": "series_complete_comment_open"}, true]
                    }
                }
            }
        ]
    }
}
```

### QC Assessment Categories (Actual Implementation)
- **Series Completeness**: Complete/Incomplete with optional comments
- **Motion Artifact**: Pass/Mild/Moderate/Severe severity scale
- **FOV Coverage**: Pass/Mild/Moderate/Severe severity scale  
- **Artifact Types**: Field inhomogeneity, ghosting/wrapping, banding
- **Conditional Comments**: Optional textarea fields with conditional visibility

## Missing Implementation Patterns

### Areas Not Currently Implemented
- **Requirements Files**: No requirements.txt or dependency management
- **Testing Framework**: No test files or testing structure
- **Environment Variables**: Configuration uses embedded credentials
- **Custom Exceptions**: Generic Exception used throughout
- **Comprehensive Logging**: Mix of logging and print statements
- **Input Validation**: Minimal configuration validation
- **Performance Monitoring**: No resource usage tracking
- **Documentation Generation**: No automated API documentation