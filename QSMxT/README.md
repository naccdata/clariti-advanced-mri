
# Flywheel gear implementation for QSMxT v8.3.2

- Implements full MEGRE pipeline: DICOM unzip → BIDS conversion → QSMxT execution
- Produces QSM maps, SWI images, segmentation outputs, and tabular metrics
- Adds workflow archive creation, crash file capture, and container version recording
- Designed for integration into CLARiTI/MEGRE neuroimaging workflows

QSMxT source: <https://github.com/QSMxT/QSMxT>

## Development

This Flywheel gear is containerized and designed to run within the Flywheel platform. For local development and testing:

### Prerequisites

- Docker
- Flywheel SDK (for testing gear context)

### Building the Container

```bash
cd QSMxT
docker build -t qsmxt-gear .
```

### Testing Locally

The gear can be tested locally using Flywheel's gear testing tools. See the [Flywheel Gear Development Guide](https://docs.flywheel.io/hc/en-us/articles/360008162214) for details.

### Development with uv

For Python development outside the container:

```bash
# From repository root
uv sync --group dev

# Run linting
uv run ruff check QSMxT/

# Format code
uv run ruff format QSMxT/
```

## Pre-deploy Checks

Before deploying, run these checks from the repository root:

```bash
# Lint
uv run ruff check QSMxT/

# Verify formatting
uv run ruff format --check QSMxT/

# Lint the Dockerfile
hadolint QSMxT/Dockerfile

# Build the Docker image (tags using manifest's custom.gear-builder.image)
flyw gear build QSMxT
```

## Deploying to Flywheel

The gear is deployed to `naccdata.flywheel.io` using the Flywheel CLI (`flyw`).

```bash
# Log in (prompts for your API key)
flyw login

# Validate the gear manifest
flyw gear --validate QSMxT/manifest.json

# Upload the gear (tags and pushes the locally built image)
flyw gear upload QSMxT/
```

The `flyw gear upload` command tags the local image (from `custom.gear-builder.image`
in `manifest.json`) for the Flywheel registry and pushes it.

## Maintaining the Base Image

This gear builds on the Neurodesk QSMxT image (`vnmd/qsmxt_*`), which bundles a
large set of neuroimaging tools and their dependencies. The Dockerfile pins the
image by SHA256 digest to ensure reproducible builds.

Because we don't control the base image, vulnerabilities in its bundled libraries
(OpenSSL, zlib, curl, MbedTLS, etc.) can only be resolved by updating to a newer
Neurodesk release. Periodically:

1. Check for new releases at <https://hub.docker.com/r/vnmd/qsmxt/tags>
2. Pull the new image and run a vulnerability scan:

   ```bash
   trivy image --timeout 30m --scanners vuln vnmd/qsmxt_<new_version>
   ```

3. Verify the environment variables haven't changed:

   ```bash
   docker run --rm vnmd/qsmxt_<new_version> env | sort
   ```

4. Update the `FROM` line in `Dockerfile` with the new tag and digest
5. Update the `environment` block in `manifest.json` if paths changed
6. Update the `version` field in `manifest.json` and `custom.gear-builder.image`
7. Test the gear on reference data before deploying
