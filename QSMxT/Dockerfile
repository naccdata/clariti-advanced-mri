# start with qsmxt container
FROM vnmd/qsmxt_8.3.2@sha256:b55d509aa5e6227a59adfba874aedb0933373105b55bdbd115e9a5a6023bccf3

ENV BASE_DIR=/flywheel/v0
RUN mkdir -p ${BASE_DIR}/input
WORKDIR ${BASE_DIR}

# Create non-root user and working directories
RUN useradd -m -s /bin/bash flywheel && \
    mkdir -p /dicoms /bids /qsm && \
    chown flywheel:flywheel /dicoms /bids /qsm ${BASE_DIR}

# install Python dependencies
COPY requirements.txt ${BASE_DIR}/requirements.txt
RUN pip3 install --no-cache-dir -r ${BASE_DIR}/requirements.txt

COPY run.py ${BASE_DIR}/run.py
COPY manifest.json ${BASE_DIR}/manifest.json
RUN chmod +x ${BASE_DIR}/run.py

USER flywheel
ENTRYPOINT ["python3", "/flywheel/v0/run.py"]
