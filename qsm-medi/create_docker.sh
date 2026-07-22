# SPDX-FileCopyrightText: 2025 Arnold Evia <Arnold_Evia@rush.edu>
#
# SPDX-License-Identifier: BSD-3-Clause

docker_repo="aevia.azurecr.io"
docker_img_tag="qsm-medi:2.5.0"

docker run --rm repronim/neurodocker:2.1.1 generate docker \
  -b ubuntu:22.04 \
  -p apt \
  --matlabmcr version=2023b \
  --run "curl -LsSf https://astral.sh/uv/install.sh | sh" \
  --run "mkdir -p /opt/uv/cache" --env UV_CACHE_DIR="/opt/uv/cache" \
  --copy src/hd-bet/HD-BET/ /opt/HD-BET \
  --copy pyproject.toml /opt/process_QSM/pyproject.toml --copy .python-version /opt/process_QSM/.python-version \
  --workdir /opt/process_QSM --env PATH='/opt/process_QSM/.venv/bin:/root/.local/bin:$PATH' --run "uv sync --no-dev" \
  --dcm2niix version=v1.0.20260416 method=source \
  --copy src/matlab_compiler/pipeline_qsm_v1.4.0 /opt/process_QSM \
  --run "chmod -R 755 /opt/process_QSM/for_redistribution_files_only" \
  --copy src/scripts /opt/process_QSM \
  --copy src/config /config \
  --copy src/flywheel/run.py /opt/process_QSM/flywheel/run.py \
  --entrypoint='/opt/process_QSM/run.sh' > Dockerfile

docker build -t ${docker_repo}/${docker_img_tag} --progress=plain .
#docker push ${docker_repo}/${docker_img_tag}