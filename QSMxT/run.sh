#!/usr/bin/env bash 

IMAGE=naccdata.flywheel.io/qsmxt_flywheel_8.1.3_5

# Command:
docker run -u 0:0 -v /mounts/data/home/tward/Development/Flywheel/Advanced MRI \
	Pipeline/advanced_mri/QSMxT/input:/flywheel/v0/input -v \
	/mounts/data/home/tward/Development/Flywheel/Advanced MRI \
	Pipeline/advanced_mri/QSMxT/output:/flywheel/v0/output -v \
	/mounts/data/home/tward/Development/Flywheel/Advanced MRI \
	Pipeline/advanced_mri/QSMxT/work:/flywheel/v0/work -v \
	/mounts/data/home/tward/Development/Flywheel/Advanced MRI \
	Pipeline/advanced_mri/QSMxT/config.json:/flywheel/v0/config.json -v \
	/mounts/data/home/tward/Development/Flywheel/Advanced MRI \
	Pipeline/advanced_mri/QSMxT/manifest.json:/flywheel/v0/manifest.json \
	--entrypoint=/bin/sh -e \
	PATH='/opt/miniconda-4.12.0/bin:/opt/ants-2.4.3/bin:/opt/ants-2.4.3/Scripts:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/FastSurfer:/opt/miniconda-latest/bin:/opt/bru2:/opt/julia-1.9.3/bin:/opt/node-v14.17.0-linux-x64/bin' \
	-e SUBJECTS_DIR='/tmp' -e JULIA_DEPOT_PATH='~/.julia:/opt/julia_depot' -e \
	FASTSURFER_HOME='/opt/FastSurfer' -e ANTSPATH='/opt/ants-2.4.3/bin' -e \
	FLYWHEEL='/flywheel/v0/' -e LANG='C.UTF-8' -e DEBIAN_FRONTEND='noninteractive' -e \
	CONDA_DIR='/opt/miniconda-4.12.0' -e \
	DEPLOY_BINS='python3:python:nii2dcm:nextqsm:nipypecli:bet:dcm2niix:Bru2:Bru2Nii:julia:qsmxt:dicom-convert:nifti-convert' \
	-e LC_ALL='C.UTF-8' -e PWD='/opt' -e \
	DEPLOY_PATH='/opt/ants-2.4.3/bin:/opt/FastSurfer:/opt/QSMxT-UI' -e \
	ND_ENTRYPOINT='/neurodocker/startup.sh' -e LD_LIBRARY_PATH='/opt/ants-2.4.3/lib:' -e \
	TZ='UTC' $IMAGE -c python3 /flywheel/v0/run.py \
