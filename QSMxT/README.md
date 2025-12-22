Flywheel gear implementation for QSMxT v8.2.0
  Implements full MEGRE pipeline: DICOM unzip → BIDS conversion → QSMxT execution
  Produces QSM maps, SWI images, segmentation outputs, and tabular metrics
  Adds workflow archive creation, crash file capture, and container version recording
  Designed for integration into CLARiTI/MEGRE neuroimaging workflows
  Validated with test MEGRE data and QSMxT reference outputs

Testing
  Run uploaded gear in the development instance using a MEGRE image such as 5-CLARITI_NACC136672_MR_CLARiTI_Axial_3D_ME_T2_GRE_(MSV24).zip.
  For the option T1 image you can select an MPRAGE image from the same subject.
  The analysis directory will contain .nii images for SWI and QSM maps along with a ZIP that can tains all the logs and results.

QSMxT source: https://github.com/QSMxT/QSMxT 
