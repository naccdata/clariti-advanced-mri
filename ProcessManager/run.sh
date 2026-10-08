#!/usr/bin/env bash 

IMAGE="process-manager_0.1.2"

# Command:
docker run -u 0:0 -v '/mounts/data/home/tward/Development/Flywheel/Advanced MRI \
	Pipeline/advanced_mri/ProcessManager/config.json:/flywheel/v0/config.json' -v \
	'/mounts/data/home/tward/Development/Flywheel/Advanced MRI \
	Pipeline/advanced_mri/ProcessManager/manifest.json:/flywheel/v0/manifest.json' \
	--entrypoint=/bin/sh -e FLYWHEEL=/flywheel/v0 -e \
	GPG_KEY=A035C8C19219BA821ECEA86B64E628F8D684696D -e LANG=C.UTF-8 -e \
	PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin -e \
	PWD=/flywheel/v0 -e \
	PYTHON_SHA256=91bcdebfdde239a003ae93738a7fce0f9230fee5c4bc2b86f6e6e8c6f98aabe8 -e \
	PYTHON_VERSION=3.11.16 "$IMAGE" -c 'python3 /flywheel/v0/run.py' \
