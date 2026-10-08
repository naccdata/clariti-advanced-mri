# ASL Shared Base Image (asl-base)

Shared Docker base image for the two ASL gears in this repository, `ASLscp` and
`GEASLscp`. It bundles the heavy, gear-agnostic layer those gears have in common
so the expensive install runs once instead of being rebuilt per gear.

This is a **build dependency, not a runnable gear**: it has no entrypoint and
produces no outputs. Both ASL gears `FROM` it and add only their gear-specific
tail (source copy, permissions, entrypoint).

## What's in it

Extracted verbatim from the ASL gears' common Dockerfile head:

- **FreeSurfer 7.4.1** - skull stripping (mri_synthstrip)
- **FSL 6.0.7.1** - motion correction, image math, registration tools
- **ANTs 2.5.4** - nonlinear registration
- **dcm2niix** - DICOM to NIfTI conversion
- **Python 3** deps: scipy, nibabel, matplotlib, transforms3d, flywheel-sdk,
  aspose-words, reportlab, nilearn, with NumPy pinned to `<2.0.0`
- The shared ENV (FreeSurfer/FSL/ANTs paths, `FLYWHEEL=/flywheel/v0`, FSL and
  thread/OMP vars) and the apt layer

Base: `ubuntu:22.04` (`--platform=linux/amd64`), matching the gears exactly.

## ECR location

```
380366436539.dkr.ecr.us-west-2.amazonaws.com/clariti/asl-base
```

Account 380366436539 (shared-services), region `us-west-2`. The `:buildcache`
tag holds the BuildKit registry layer cache and must be **mutable** (excluded
from ECR tag immutability) so each build can overwrite it.

## Routing: fork-only base, upstream-bound gears

- Building and pushing this base image is a **fork-only** concern. The base
  Dockerfile and the `build-asl-base.yml` workflow live only on
  `naccdata/clariti-advanced-mri` and never flow upstream.
- The gear Dockerfiles' `FROM` line that consumes this image is
  **upstream-bound gear source**. Changes to it belong in a separate small PR to
  `rt-ward/Advanced-MRI`; they are kept on the fork branch now only for
  development/testing.

## Build and push

### Via the workflow (preferred)

`.github/workflows/build-asl-base.yml` builds and pushes to ECR with layer
caching. Trigger it either way:

- Push a tag matching `asl-base-v*` (e.g. `asl-base-v1`), which also tags the
  image with the version suffix.
- Run it manually (`workflow_dispatch`), which tags the image with a UTC
  timestamp.

Both runs also push `:latest`. The workflow prints the pushed image **digest**
in its logs and job output — you need that digest for the gear update below.

### Manually (local)

```bash
docker buildx build --platform linux/amd64 \
  -t 380366436539.dkr.ecr.us-west-2.amazonaws.com/clariti/asl-base:latest \
  asl-base/
```

Add `--push` (after `aws ecr get-login-password | docker login ...`) to publish.

## Updating a tool version: the two-step dance

When a tool version or any base layer changes, update in two steps because the
base build and the gear `FROM` are routed to different repos:

1. **Rebuild and push the base** (fork-only): edit `asl-base/Dockerfile`, then
   run `build-asl-base.yml` (or build/push manually). Note the new digest.
2. **Update the gear `FROM` lines** (upstream-bound): replace the `@sha256:`
   digest in the `FROM` line of **both** `ASLscp/Dockerfile` and
   `GEASLscp/Dockerfile`. These two files must stay byte-identical and the
   change goes to upstream in its own PR.

The gear Dockerfiles currently carry a `PLACEHOLDER_REPLACE_AFTER_FIRST_BASE_PUSH`
digest; replace it with the real digest after the base is first built and pushed.

## Infra prerequisites

Before `build-asl-base.yml` can succeed, provision (a new entry not yet in
`scratch/gear-deploy-aws-requirements.md`):

- The `clariti/asl-base` ECR repo (Terraform, shared-services, `us-west-2`).
- The `clariti-asl-base-push` IAM role with an OIDC trust policy scoped to
  `repo:naccdata/clariti-advanced-mri:environment:asl-base-sandbox`.
- The `asl-base-sandbox` GitHub environment in the fork (scopes the OIDC
  subject; no promotion split since nothing is published to Flywheel).
- A **mutable** `:buildcache` tag on the ECR repo.
