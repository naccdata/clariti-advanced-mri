# start with qsmxt container
FROM vnmd/qsmxt_8.3.2@sha256:b55d509aa5e6227a59adfba874aedb0933373105b55bdbd115e9a5a6023bccf3

# install Python dependencies
COPY requirements.txt /flywheel/v0/requirements.txt
RUN pip3 install --no-cache-dir -r /flywheel/v0/requirements.txt

COPY run.py /flywheel/v0/run.py
RUN chmod +x /flywheel/v0/run.py
#ENTRYPOINT [ "/bin/bash" ]
ENTRYPOINT ["python3",  "/flywheel/v0/run.py"]
