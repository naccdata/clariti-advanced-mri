# Thin wrapper on the shared ASL base image (asl-base/).
#
# ROUTING: this FROM-line change is upstream-bound gear source — it belongs in a
# separate small PR to rt-ward/Advanced-MRI. It is kept on this fork branch for
# development/testing. Building/pushing the base image itself is fork-only
# (.github/workflows/build-asl-base.yml), and never flows upstream.
#
# The @sha256 digest below is a PLACEHOLDER. Replace it with the real digest
# printed by build-asl-base.yml after the base is first built and pushed to ECR.
# ASLscp/ and GEASLscp/ must FROM the same digest and stay byte-identical.
FROM 380366436539.dkr.ecr.us-west-2.amazonaws.com/clariti/asl-base@sha256:PLACEHOLDER_REPLACE_AFTER_FIRST_BASE_PUSH

# Copy files and set permissions
COPY ./input/ ${FLYWHEEL}/input/
COPY ./workflows/ ${FLYWHEEL}/workflows/
COPY ./pipeline_singlePLD.sh ${FLYWHEEL}/
RUN chmod -R 777 ${FLYWHEEL}

# Set entrypoint
ENTRYPOINT ["/bin/bash", "/flywheel/v0/pipeline_singlePLD.sh"]
