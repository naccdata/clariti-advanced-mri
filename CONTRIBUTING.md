# Contributing

`naccdata/clariti-advanced-mri` (git remote `origin`) is a fork of
`rt-ward/Advanced-MRI` (git remote `upstream`). Gear/pipeline code and gear
deployment are owned by different repositories, so changes must be routed to the
right place. Read this before opening a branch or a pull request.

## Remotes

Set up both remotes once:

```sh
git remote -v
# origin    https://github.com/naccdata/clariti-advanced-mri.git
# upstream  https://github.com/rt-ward/Advanced-MRI.git
```

If `upstream` is missing:

```sh
git remote add upstream https://github.com/rt-ward/Advanced-MRI.git
```

## Ownership split

- **upstream (`rt-ward/Advanced-MRI`)** owns the gear and pipeline *code* — what
  each gear does. It is the source of truth for gear source.
- **origin (`naccdata/clariti-advanced-mri`)** owns *deployment* — how gears are
  built and released to Flywheel. Releases happen in the fork, never upstream.

Rule of thumb: **code flows down from upstream; deployment lives only in the
fork and never flows up.**

## Routing a change

Decide up front whether a change is upstream-bound or fork-only. That decision
determines where you base the branch and what the branch is allowed to contain.

### Upstream-bound (gear/pipeline source, shared CI)

Anything that changes gear behavior — files under a gear directory (`qsm-medi/`,
`QSMxT/`, `ASLscp/`, `GEASLscp/`, etc.) — and shared test/lint CI such as
`.github/workflows/test-qsm-medi.yml`.

1. Sync `main` with upstream first (see "Keeping in sync").
2. Branch from the synced `main` (i.e. from `upstream/main`).
3. Keep the change set to gear source + shared CI only. No deploy/infra files.
4. Open the PR against `rt-ward/Advanced-MRI`.

### Fork-only (deployment, releases, infra coordination)

Deploy workflows (`.github/workflows/deploy-*.yml`) and anything that references
the shared-services AWS account, ECR repositories, IAM roles, SSM parameters, or
the fork's GitHub deployment environments.

1. Branch from the fork's `main`.
2. Open the PR against `naccdata/clariti-advanced-mri`.
3. These files stay on the fork and are never included in an upstream PR.

## The deciding factor

It is not only *where* you branch from — it is *where you branch from AND what
the change set contains*. A branch based on upstream that accidentally includes
a `deploy-*.yml` would still carry fork-only deployment config upstream. Before
opening an upstream PR, review the file list and confirm it contains no
deploy/infra files.

## Branch protection

`main` is protected: all changes land through a pull request (no direct pushes),
a review is required, and the `test` check must pass. Admins can override in a
pinch, but the default path — including syncing from upstream — is always a PR.
Do not push directly to `main` even when you can.

## Keeping in sync

Pull upstream changes down regularly so the fork does not drift. Because `main`
is protected, do this on a branch and open a PR — never push the sync straight
to `main`:

```sh
git fetch upstream
git checkout -b sync-upstream main
git merge upstream/main          # a real merge; upstream usually diverges, so
                                 # --ff-only will not apply once the fork has
                                 # its own commits
# reconcile deploy-only manifest fields (see below), then:
git push origin sync-upstream
gh pr create --base main --head sync-upstream   # PR into the fork
```

To contribute code upstream, open a PR from a fork branch to `rt-ward`, scoped
to gear source + shared CI only.

### Reconcile deploy-only manifest fields after every upstream pull

A gear's `manifest.json` mixes gear definition (upstream's) with a few
deploy-only fields the fork owns. Upstream deliberately does NOT carry the
fork's Flywheel/ECR deployment values, so upstream's copy of these fields
differs from the fork's. A merge may CONFLICT on them (safe — you are forced to
reconcile) or SILENTLY take upstream's value (dangerous — it can quietly revert
the fork's deploy config). So do not rely on a conflict appearing: after every
upstream pull, verify the fork's manifest still has its deploy values.

Fork-owned manifest fields to confirm after a pull (per gear):

- `version` — the clean semver release (e.g. `2.5.2`). Upstream carries a
  pre-release suffix (e.g. `2.5.2-beta`); strip it to the clean release here.
- `custom.gear-builder.image` — the fork's ECR image
  (`clariti/<gear>:<version>`). Upstream uses a different registry.
- `custom.flywheel.private` — `true` on the fork. Absent upstream.

There must be **no `exchange` block** in `manifest.json`. The gear manifest
schema does not allow it (`flyw gear upload` rejects it), and the publish
tooling sets `exchange` itself at upload time. Earlier fork revisions carried an
`exchange.rootfs-url` pointing at ECR — that was a mistake and has been removed.
If an upstream pull reintroduces an `exchange` key (upstream historically
carried `exchange: null`), delete it during reconcile.

Quick check after a pull (adjust the expected image per gear):

```sh
jq '{version, image: .custom["gear-builder"].image,
     private: .custom.flywheel.private,
     exchange: (has("exchange"))}' qsm-medi/manifest.json
# expect: version = clean semver, image = clariti/<gear>:<version>,
#         private = true, exchange = false (key absent)
```

If any field reverted to an upstream value, or an `exchange` key reappeared,
fix it before tagging a release. The deploy workflow's version-consistency and
manifest sanity-check steps catch the version and `gear-builder.image` tag, but
`private` is not gated — and an `exchange` block would fail the deploy later at
`flyw gear upload` (manifest validation), so strip it here.

## Deployment

Deployment is a fork-only concern and is intentionally guarded so the deploy
workflows cannot run outside `naccdata/clariti-advanced-mri`:

1. An owner gate on every job:
   `if: github.repository == 'naccdata/clariti-advanced-mri'`.
2. Per-gear GitHub deployment environments (`<gear>-sandbox`,
   `<gear>-production`), with a required-reviewer rule on production.
3. AWS OIDC role trust policies scoped to the fork's environment subjects
   (`repo:naccdata/clariti-advanced-mri:environment:<gear>-<env>`), enforced on
   the AWS side.

These guards are a safety net, not a reason to include deploy files in an
upstream PR. Keep deployment in the fork.

## Development environment

- Python is managed with [`uv`](https://docs.astral.sh/uv/).
- Linting and formatting use [`ruff`](https://docs.astral.sh/ruff/).
- Tests run with `pytest`.
- Gear containers build with Docker.

Each gear directory is self-contained (its own `pyproject.toml`, `Dockerfile`,
and tests); run tooling from within the gear directory you are working on.
