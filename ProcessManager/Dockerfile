# Use standard Python 3 Linux base
FROM python:3.11-slim

# Define standard Flywheel directory structure
ENV FLYWHEEL=/flywheel/v0
#RUN mkdir -p ${FLYWHEEL}
WORKDIR ${FLYWHEEL}

# install Python dependencies
COPY requirements.txt ${FLYWHEEL}/requirements.txt
RUN pip3 install --no-cache-dir -r ${FLYWHEEL}/requirements.txt

COPY run.py ${FLYWHEEL}/run.py
COPY manifest.json ${FLYWHEEL}/manifest.json
RUN chmod +x ${FLYWHEEL}/run.py

ENTRYPOINT ["python3", "/flywheel/v0/run.py"]
