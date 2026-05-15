#!/usr/bin/env python3
"""Flywheel Gear: QSMxT Processing Pipeline.

This gear:
1. Unzips MEGRE and T1w DICOM archives.
2. Converts MEGRE using `dicom-convert`.
3. Converts T1w DICOMs using `dcm2niix`.
4. Launches QSMxT with user-provided config options.
5. Collects workflow outputs, standard NIfTI results, and crash logs.
6. Packages results into artifacts suitable for Flywheel.

Environment Assumptions
-----------------------
- QSMxT, dicom-convert, and dcm2niix are already installed in the container.
- Filesystem paths /dicoms, /bids, /qsm are writable.
"""

import glob
import logging
import os
import shutil
import sys
import zipfile
from pathlib import Path

from fw_gear.context import GearContext
from fw_gear.utils.archive.zip_manager import unzip_archive, zip_output
from fw_gear.utils.wrapper import exec_command

log = logging.getLogger(__name__)


def unzip_inputs(megre_paths: list[str | None], t1w_path: str | None) -> None:
    """Unzip MEGRE and T1w DICOM archives to working directories."""
    log.info("Unzipping MEGRE DICOMs: %s", megre_paths)
    for path in megre_paths:
        if path is not None:
            unzip_archive(path, "/dicoms/qsm")

    log.info("Unzipping T1w DICOMs: %s", t1w_path)
    if t1w_path is not None:
        unzip_archive(t1w_path, "/dicoms/T1w")


def convert_megre_to_bids() -> None:
    """Convert MEGRE DICOMs to BIDS using dicom-convert."""
    exec_command(
        ["dicom-convert", "/dicoms/", "/bids/", "--auto_yes"],
        stream=True,
    )


def convert_t1w_to_bids() -> None:
    """Convert T1w DICOMs into BIDS-compatible naming via dcm2niix."""
    anat_list = list(Path("/bids/").glob("sub*/ses*/anat/*.nii"))

    if not anat_list:
        log.warning("No MEGRE anat/*.nii found. Skipping T1w conversion.")
        return

    first_file = anat_list[0]
    important_parts = [
        s for s in first_file.name.split("_") if "sub" in s or "ses" in s
    ]
    t1_target_name = "_".join([*important_parts, "T1w"])

    exec_command(
        [
            "dcm2niix",
            "-b", "y",
            "-f", t1_target_name,
            "-o", str(first_file.parent),
        ],
        stream=True,
    )


def run_qsmxt(config: dict) -> None:
    """Build and execute the QSMxT command from gear configuration."""
    qsmxt_cmd = [
        "qsmxt",
        "/bids",
        "/qsm",
        "--premade", str(config.get("premade", "gre")),
        "--auto_yes",
    ]

    for arg in ["do_qsm", "do_swi", "do_segmentation",
                "do_t2starmap", "do_r2starmap", "do_analysis",
                "combine_phase", "export_dicoms"]:
        if config.get(arg, False):
            qsmxt_cmd.append(f"--{arg}")

    # Optional string/numeric arguments
    masking_input = config.get("masking_input", "")
    if masking_input:
        qsmxt_cmd.extend(["--masking_input", masking_input])

    obliquity_threshold = config.get("obliquity_threshold")
    if obliquity_threshold is not None:
        qsmxt_cmd.extend(["--obliquity_threshold", str(obliquity_threshold)])

    log.info("Running QSMxT: %s", qsmxt_cmd)
    exec_command(qsmxt_cmd, stream=True)


def package_outputs(output_dir: str) -> None:
    """Package QSMxT results into gear output artifacts."""
    # Package workflow directory
    workflow_path = "/qsm/workflow"
    if os.path.isdir(workflow_path):
        log.info("Packaging workflow directory")
        zip_output(
            root_dir="/qsm",
            source_dir="workflow",
            output_zip_filename=os.path.join(output_dir, "workflow.zip"),
        )
        shutil.rmtree(workflow_path, ignore_errors=True)

    # Copy NIfTI results
    nifti_files = glob.glob("/qsm/**/*.nii", recursive=True)
    log.info("NIfTI files detected: %d", len(nifti_files))
    for f in nifti_files:
        shutil.copy2(f, os.path.join(output_dir, os.path.basename(f)))

    # Create a zip of the entire qsm output tree
    zip_output(
        root_dir="/",
        source_dir="qsm",
        output_zip_filename=os.path.join(output_dir, "qsm.zip"),
    )


def check_for_crashes(output_dir: str) -> bool:
    """Check for crash files and package them if found.

    Returns
    -------
    bool
        True if crashes were detected.
    """
    crash_files = glob.glob("/flywheel/v0/crash*.pklz")
    if not crash_files:
        return False

    crash_zip = os.path.join(output_dir, "crashes.zip")
    log.error("Crashes detected. Packaging crash reports: %s", crash_zip)

    with zipfile.ZipFile(crash_zip, "w") as zf:
        for crash in crash_files:
            zf.write(crash, os.path.basename(crash))

    return True


def main(context: GearContext) -> None:
    """Execute main gear workflow."""
    config = context.config.opts

    # Gather input paths
    megre_paths = [
        context.config.get_input_path("input_file"),
        context.config.get_input_path("input_file_opt"),
        context.config.get_input_path("input_file_opt2"),
    ]
    t1w_path = context.config.get_input_path("anatomical")

    # Step 1-2: Unzip and convert MEGRE
    unzip_inputs(megre_paths, t1w_path)
    convert_megre_to_bids()

    # Step 3: Convert T1w
    convert_t1w_to_bids()

    # Step 4: Run QSMxT
    run_qsmxt(config)

    # Step 5: Package outputs
    package_outputs(context.output_dir)

    # Step 6: Check for crashes
    if check_for_crashes(context.output_dir):
        log.error("Inspect workflow.zip and crashes.zip for details.")
        sys.exit(1)

    log.info("QSMxT Gear completed successfully.")


if __name__ == "__main__":
    with GearContext() as context:
        context.init_logging()
        context.log_config()
        main(context)
