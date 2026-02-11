---
inclusion: always
---

# Product Patterns for Advanced-MRI Repository

## Repository Purpose and Components

### Repository Purpose (From README)
This repository contains scripts, Flywheel gears, and viewer protocols that support the processing, quality control, and visualization of Advanced MRI data, including MEGRE, ASL, and vNAV sequences. It provides a centralized, version-controlled workspace for developing, testing, and deploying tools used across CLARiTI, SCAN, and related imaging workflows.

### Components (Actual Implementation)
- **ImageUploading**: DICOM ZIP ingestion utility that extracts metadata, groups by series, and uploads to Flywheel
- **QSMxT**: Flywheel gear for end-to-end MEGRE → QSM processing pipeline with BIDS conversion  
- **QC Viewer Protocol**: Structured quality control assessment forms for reconstruction and artifact evaluation

### Implementation Patterns
- Tools provide console output with timestamps and operation descriptions
- Configuration uses simple JSON format with minimal required parameters
- Processing status visible through stdout logging with operation descriptions
- Results include both processed outputs and workflow archives

### Core Functionality (Actual Implementation)
- **DICOM Processing**: Extract metadata using pydicom with stop_before_pixels=True for efficiency
- **Series Grouping**: Group DICOM files by SeriesInstanceUID before processing
- **Flywheel Integration**: Use dual client approach (SDK + REST) for comprehensive API access
- **Subject Identification**: Extract subject labels from file paths containing "NACC" identifiers

### Processing Patterns (Current Implementation)
- **Batch Processing**: Process multiple subjects from single ZIP archive
- **Memory Efficiency**: Use stop_before_pixels for metadata extraction
- **Temporary Storage**: Use tempfile.TemporaryDirectory() for automatic cleanup
- **Parallel Operations**: Support multiple series processing within single subject

### Integration Patterns (Actual Implementation)
- **Flywheel Compatibility**: Support both flywheel.Client SDK and FWClient REST wrapper
- **BIDS Conversion**: Use dicom-convert and dcm2niix tools for standardized conversion
- **Container Support**: Flywheel gear format with manifest.json configuration
- **QSM Processing**: Integration with QSMxT CLI tools and premade pipeline configurations

### Quality Control Implementation
- **DICOM Metadata**: Preserve SeriesInstanceUID, SeriesNumber, StudyDate, PatientID
- **Series Integrity**: Maintain complete series groupings during processing
- **Quality Assessment**: Structured QC forms capturing completeness, motion, FOV, artifacts
- **Output Formats**: Generate NIfTI outputs (QSM maps, SWI images) with workflow archives

### Interface Patterns (Actual Implementation)
- **Error Logging**: Log errors with context before raising exceptions
- **Progress Indication**: Print operation descriptions and file counts during processing
- **Configuration Simplicity**: Use minimal JSON config with APIKey and project prefix
- **Structured QC**: Dropdown selections with severity scales (Pass/Mild/Moderate/Severe)

### Implementation Checklist

#### Component Requirements (Based on Current Implementation)
For any new feature or component:
- [ ] Functionality works with DICOM ZIP archives containing NACC subject identifiers
- [ ] Error conditions logged with descriptive messages before raising exceptions
- [ ] Documentation includes usage examples and configuration format
- [ ] Integration with Flywheel project hierarchy (subject → session → acquisition)
- [ ] Temporary files cleaned up using context managers
- [ ] Logging output includes timestamps and operation descriptions

#### Deployment Requirements (Current Implementation)
- [ ] Components work with existing Flywheel gear manifest format
- [ ] Container builds successfully from base images (vnmd/qsmxt_8.2.0)
- [ ] JSON configuration files validated and documented
- [ ] QC forms include conditional comment fields and severity scales
- [ ] Processing outputs include both results and workflow archives

### Current Implementation Status

#### Component Status (Actual Implementation)
- **ImageUploading**: Functional DICOM ingestion with series grouping and Flywheel upload
- **QSMxT**: Complete MEGRE processing pipeline with BIDS conversion and QSM generation
- **QC Viewer Protocol**: Structured assessment forms with conditional logic and artifact categorization

#### Areas for Development (Based on Analysis)
1. **Dependency Management**: Add requirements.txt files and external dependency documentation
2. **Error Handling**: Standardize exception handling patterns across components
3. **Configuration**: Add environment variable support for sensitive credentials
4. **Testing**: Add test structure and sample data for validation
5. **Documentation**: Expand README files with complete setup and troubleshooting

### Processing Metrics

#### Technical Metrics (Current Implementation Focus)
- DICOM ZIP processing success rate for archives with NACC identifiers
- Series grouping accuracy by SeriesInstanceUID
- Flywheel upload success rate with proper metadata tagging
- QSM processing completion rate with workflow archive generation

#### Operational Metrics (Current Deployment)
- Flywheel gear execution success rate
- Container startup time for QSMxT processing
- BIDS conversion success rate using dicom-convert
- Temporary file cleanup success rate