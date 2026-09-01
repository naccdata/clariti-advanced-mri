# QSM-MEDI Flywheel Gear
# Base image: Ubuntu 22.04 (jammy). MCR R2023b requires glibc >= 2.31.
# Platform is pinned to linux/amd64: the MATLAB Runtime for Linux ships x86_64
# binaries only (no arm64 installer), and Flywheel runs on x86_64. Building on
# an arm64 host (e.g. Apple Silicon) requires emulation via this platform flag.
FROM --platform=linux/amd64 ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"

# Locale setup and base utilities
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           apt-utils \
           bzip2 \
           ca-certificates \
           curl \
           locales \
           unzip \
    && rm -rf /var/lib/apt/lists/* \
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && update-locale LANG="en_US.UTF-8"

# MATLAB Compiler Runtime R2023b (Update 9)
ENV LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:/opt/MCR-2023b/v915/runtime/glnxa64:/opt/MCR-2023b/v915/bin/glnxa64:/opt/MCR-2023b/v915/sys/os/glnxa64:/opt/MCR-2023b/v915/extern/bin/glnxa64" \
    MATLABCMD="/opt/MCR-2023b/2023b/toolbox/matlab" \
    XAPPLRESDIR="/opt/MCR-2023b/v915/x11/app-defaults" \
    MCRROOT="/opt/MCR-2023b/2023b"

RUN export TMPDIR="$(mktemp -d)" \
    && apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           bc \
           curl \
           dbus-x11 \
           libncurses5 \
           libxext6 \
           libxmu6 \
           libxpm-dev \
           libxt6 \
           openjdk-8-jre \
           unzip \
    && rm -rf /var/lib/apt/lists/* \
    && echo "Downloading MATLAB Compiler Runtime ..." \
    && curl -o "$TMPDIR/mcr.zip" https://ssd.mathworks.com/supportfiles/downloads/R2023b/Release/9/deployment_files/installer/complete/glnxa64/MATLAB_Runtime_R2023b_Update_9_glnxa64.zip \
    && unzip -q "$TMPDIR/mcr.zip" -d "$TMPDIR/mcrtmp" \
    && "$TMPDIR/mcrtmp/install" -destinationFolder /opt/MCR-2023b -mode silent -agreeToLicense yes \
    && rm -rf "$TMPDIR" \
    && unset TMPDIR

# Pin uv from official distroless image for reproducibility
COPY --from=ghcr.io/astral-sh/uv:0.11.23 /uv /uvx /bin/
RUN mkdir -p /opt/uv/cache
ENV UV_CACHE_DIR="/opt/uv/cache"

# Python dependencies (copy pyproject.toml first for layer caching)
COPY ["src/hd-bet/HD-BET/", "/opt/HD-BET"]
COPY ["pyproject.toml", "/opt/process_QSM/pyproject.toml"]
COPY [".python-version", "/opt/process_QSM/.python-version"]
WORKDIR /opt/process_QSM
ENV PATH="/opt/process_QSM/.venv/bin:$PATH"
RUN uv sync --no-dev

# dcm2niix (pre-built release binary)
ENV PATH="/opt/dcm2niix/bin:$PATH"
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           ca-certificates \
           curl \
           pigz \
           unzip \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/dcm2niix/bin \
    && curl -fsSL -o /tmp/dcm2niix_lnx.zip \
       https://github.com/rordenlab/dcm2niix/releases/download/v1.0.20260416/dcm2niix_lnx.zip \
    && unzip -q /tmp/dcm2niix_lnx.zip -d /opt/dcm2niix/bin \
    && chmod +x /opt/dcm2niix/bin/dcm2niix \
    && rm /tmp/dcm2niix_lnx.zip

# Pipeline binary and scripts
COPY ["src/matlab_compiler/pipeline_qsm_v1.4.0/for_redistribution_files_only", \
      "/opt/process_QSM/for_redistribution_files_only"]
RUN chmod -R 755 /opt/process_QSM/for_redistribution_files_only
COPY ["src/scripts", "/opt/process_QSM"]
COPY ["src/flywheel/run.py", "/opt/process_QSM/flywheel/run.py"]

# Non-root execution
RUN useradd -m -s /bin/bash flywheel \
    && chown -R flywheel:flywheel /opt/process_QSM \
    && mkdir -p /flywheel/input /flywheel/output /input/parameters \
    && chown -R flywheel:flywheel /flywheel /input
USER flywheel

ENTRYPOINT ["/opt/process_QSM/run.sh"]
