#!/usr/bin/env python
"""Flywheel Gear: QSM-MEDI Processing Pipeline.

This gear entry point:
1. Extracts DICOM zip archives to a working directory.
2. Generates a parameters JSON from Flywheel gear configuration.
3. Launches the QSM-MEDI shell pipeline (run.sh).
4. Validates that the expected QSM output was produced.
"""

# SPDX-FileCopyrightText: 2025 Arnold Evia <Arnold_Evia@rush.edu>
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import json
import logging
import subprocess
import time
import zipfile
from pathlib import Path

import flywheel

log = logging.getLogger(__name__)

PATH_PARAMETERS_JSON = Path("/input/parameters/qsm_parameters.json")

# Configuration variables passed through to the MATLAB pipeline.
# Names must match what the pipeline expects in its JSON config.
CONFIG_VARIABLES = [
    "load_nifti_common_prefix",
    "load_negate_every_other_axis",
    "invert_phase",
    "method_phase_unwrap",
    "phase_corr",
    "csf_thresh_R2s",
    "csf_flag_erode",
    "pdf_tol",
    "pdf_n_cg",
    "pdf_space",
    "pdf_n_pad",
    "prefilter",
    "bipolar_complex_fit",
    "debug_mode",
    "medi_msmv",
    "medi_lambda",
    "medi_max_iter",
    "medi_tol_norm_ratio",
    "medi_cg_verbose",
    "medi_cg_max_iter",
    "medi_cg_tol",
]


def run_command(command: list[str]) -> int:
    """Run a command, streaming stdout/stderr to the log.

    Parameters
    ----------
    command : list[str]
        Command and arguments to execute.

    Returns
    -------
    int
        Process return code.
    """
    process = subprocess.Popen(
        args=command,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )

    def stream_process(proc: subprocess.Popen) -> bool:
        go = proc.poll() is None
        for line in proc.stdout:
            log.info(line.rstrip())
        return go

    while stream_process(process):
        time.sleep(0.1)

    return process.returncode


def safe_extract_zip(zip_path: str, destination: str) -> None:
    """Extract a zip archive with zip-slip protection.

    Parameters
    ----------
    zip_path : str
        Path to the zip file.
    destination : str
        Directory to extract into.

    Raises
    ------
    ValueError
        If a zip entry attempts path traversal outside the destination.
    """
    dest = Path(destination).resolve()
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            member_path = (dest / member).resolve()
            if not str(member_path).startswith(str(dest)):
                raise ValueError(
                    f"Zip entry would escape target directory: {member}"
                )
        zf.extractall(destination)


def create_parameters_json(context: flywheel.GearContext) -> None:
    """Create a parameters JSON file from the Flywheel gear configuration.

    Only includes config values that are not None, allowing the MATLAB
    pipeline to use its own defaults for omitted parameters.

    Parameters
    ----------
    context : flywheel.GearContext
        The active gear context containing user-provided config values.
    """
    PATH_PARAMETERS_JSON.parent.mkdir(parents=True, exist_ok=True)

    parameters_dict = {}
    for config_variable in CONFIG_VARIABLES:
        config_value = context.config.get(config_variable)
        if config_value is not None:
            parameters_dict[config_variable] = config_value

    PATH_PARAMETERS_JSON.write_text(
        json.dumps(parameters_dict, ensure_ascii=False, indent=4), encoding="utf-8"
    )


def main() -> None:
    """Execute the QSM-MEDI gear workflow."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    input_folder = Path("/flywheel/input")
    dicom_staging = input_folder / "dicom_data"

    with flywheel.GearContext() as context:
        dicom_zip_paths = [
            context.get_input_path("input_file"),
            context.get_input_path("input_file_opt"),
        ]
        output_folder = Path(context.output_dir)

        log.info("Unzipping MEGRE DICOMs: %s", dicom_zip_paths)
        for i, zip_path in enumerate(dicom_zip_paths):
            if zip_path is not None:
                dest = dicom_staging / str(i)
                dest.mkdir(parents=True, exist_ok=True)
                safe_extract_zip(zip_path, str(dest))

        num_threads_hdbet = context.config.get("num_threads_hdbet", 0)

        create_parameters_json(context)

        pipeline_command = [
            "/opt/process_QSM/run.sh",
            "-i",
            str(input_folder),
            "-o",
            str(output_folder),
            "-p",
            str(PATH_PARAMETERS_JSON),
            "-n",
            str(num_threads_hdbet),
        ]
        returncode = run_command(pipeline_command)

        if returncode != 0:
            raise RuntimeError(
                "run.sh returned a non-zero exit code. "
                "Check processing.log for details."
            )

        if not (output_folder / "QSM.nii.gz").is_file():
            raise RuntimeError(
                "Final check failed: QSM.nii.gz was not created. "
                "Check processing.log for details."
            )

        log.info("QSM-MEDI gear completed successfully.")


if __name__ == "__main__":
    main()
