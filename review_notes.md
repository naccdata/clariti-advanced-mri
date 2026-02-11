# Code Review Notes for Advanced-MRI Repository

## Priority Issues to Address

### 1. Add .gitignore for Python Projects

**Issue**: No `.gitignore` file exists, risking commits of build artifacts, cache files, and sensitive data.

**Solution**: Add comprehensive Python `.gitignore`

```bash
# Generate Python .gitignore
curl -s https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore > .gitignore
```

**Additional patterns to add**:

```gitignore
# Project-specific
*.conf
!*.conf.example
```

### 2. API Key Management

**Critical Security Issue**: API key is committed in `ImageUploading/fwImageUpload.conf`

**Immediate Actions**:

1. Remove the API key from the config file
2. Add `*.conf` to `.gitignore`
3. Create `fwImageUpload.conf.example` template:

```json
{
    "APIKey": "your_flywheel_api_key_here",
    "project": "advanced-mri"
}
```

1. Update code to use environment variables:

```python
import os
api_key = os.getenv('FLYWHEEL_API_KEY') or config.get('APIKey')
if not api_key:
    raise ValueError("FLYWHEEL_API_KEY environment variable or config APIKey required")
```

### 3. Dependencies Management

**Issue**: No dependency files exist, making setup unclear.

**Solution**: Use `uv` for modern Python dependency management

**Implementation**:

1. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Initialize project: `uv init --no-readme`
3. Add dependencies:

```bash
# For ImageUploading
cd ImageUploading
uv add flywheel-sdk pydicom

# For QSMxT  
cd ../QSMxT
uv add flywheel-sdk
```

**Note**: Document the external `fw_client` dependency in ImageUploading README.

### 4. Development Tooling Configuration

**Issue**: No linting, formatting, or testing setup.

**Solution**: Add `pyproject.toml` in repository root:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "advanced-mri"
version = "0.1.0"
description = "Advanced MRI processing tools for CLARiTI and SCAN workflows"
requires-python = ">=3.8"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
]

[tool.ruff]
line-length = 88
indent-width = 4
target-version = "py311"

[tool.ruff.lint]
select = ["A", "B", "E", "W", "F", "I", "RUF", "SIM", "C90", "PLW0406", "COM818", "SLF001"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = [
    "--cov=image_uploading",
    "--cov=qsmxt", 
    "--cov-report=html",
    "--cov-report=term-missing"
]
```

**Setup commands**:

```bash
# Install development dependencies
uv sync

# Run linter
uv run ruff check .

# Format code
uv run ruff format .

# Run tests
uv run pytest
```

### 5. Directory Naming Convention

**Issue**: Directory name `QC Viewer Protocol` contains spaces, which can cause command-line issues.

**Solution**: Rename to snake_case convention:

```bash
git mv "QC Viewer Protocol" qc_viewer_protocol
```

**Update any references** in documentation and code that reference the old directory name.

### 6. Fix Markdown Formatting

**Issue**: README.md and other markdown files use indentation instead of proper markdown list syntax.

**Current problematic format**:

```markdown
Contents
  Scripts
    Utilities for data preparation...
  Flywheel Gears
    Containerized analysis tools...
```

**Should be proper markdown lists**:

```markdown
## Contents

### Scripts
- Utilities for data preparation, DICOM metadata extraction, automated classification, reprocessing, and workflow orchestration

### Flywheel Gears
- Containerized analysis tools ready for execution within the Flywheel platform, including:
  - Sequence-specific QC pipelines
  - MEGRE → QSM workflows
  - ASL quantification and derived metrics
  - Reprocessing utilities for updated analysis methods
```

**Solution**: Add markdown linting to ruff configuration and fix existing files.

**Update pyproject.toml** to include markdown linting:

```toml
[tool.ruff.lint]
select = ["A", "B", "E", "W", "F", "I", "RUF", "SIM", "C90", "PLW0406", "COM818", "SLF001", "MD"]
```

**Check markdown files**:

```bash
# Lint markdown files
uv run ruff check *.md */README.md

# Or use a dedicated markdown linter
npm install -g markdownlint-cli
markdownlint *.md */README.md
```

## Implementation Order

1. **Immediate (Security)**: Remove API key, add .gitignore, create config template
2. **Setup (Development)**: Add pyproject.toml, install uv, set up tooling
3. **Dependencies**: Add uv dependency files for each component
4. **Structure**: Rename directories to snake_case
5. **Documentation**: Fix markdown formatting in README and other .md files
6. **Validation**: Run ruff and pytest to ensure everything works

## Quick Start After Changes

Once implemented, developers can:

```bash
# Clone and setup
git clone <repo>
cd advanced-mri

# Install dependencies and tools
uv sync

# Check code quality
uv run ruff check .
uv run ruff format .

# Run tests (once test files are added)
uv run pytest
```

## Next Steps (Future Improvements)

- Add basic test files for each component
- Set up GitHub Actions CI/CD
- Add more comprehensive documentation
- Consider using Pydantic for configuration validation

```bash
# Clone and setup
git clone <repo>
cd advanced-mri

# Install dependencies and tools
uv sync

# Check code quality
uv run ruff check .
uv run ruff format .

# Run tests (once test files are added)
uv run pytest
```

## Next Steps (Future Improvements)

- Add basic test files for each component
- Set up GitHub Actions CI/CD
- Add more comprehensive documentation
- Consider using Pydantic for configuration validation
