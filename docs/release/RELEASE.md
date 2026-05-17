# Releasing kubeflow-mcp

This repository publishes the `kubeflow-mcp` Python package to PyPI using
GitHub Actions and PyPI trusted publishing. No PyPI API token is stored in the
repository.

## Versioning

`kubeflow-mcp` follows Python's [PEP 440](https://peps.python.org/pep-0440/)
version format for releases:

- Final releases use `X.Y.Z`, for example `0.1.0`.
- Release candidates use `X.Y.ZrcN`, for example `0.1.0rc1`.

The package version currently lives in two places and both must be updated in
the same pull request:

- `pyproject.toml`: `[project] version`
- `kubeflow_mcp/__init__.py`: `__version__`

The project uses Hatchling as the build backend and the release workflow builds
the package with `uv build`, matching the SDK release workflow.

## Tags

Release tags must match the package version exactly:

- `0.1.0`
- `0.1.0rc1`

Do not prefix release tags with `v`.

## Release Process

1. Create a version bump branch from `main`.

   Update `pyproject.toml` and `kubeflow_mcp/__init__.py` to the same PEP 440
   version.

2. Update release notes.

   This repository does not currently have a committed `CHANGELOG.md` or
   `CHANGELOG/` structure on `main`. Use the GitHub Release body as the release
   changelog and summarize notable changes from merged pull requests. If a
   changelog file or directory is added later, update it in the same PR as the
   version bump and copy the relevant section into the GitHub Release body.

3. Run local verification.

   ```sh
   make verify
   make test-python
   uv build
   uvx twine check dist/*
   ```

4. Open a PR to `main` and get it reviewed and merged.

5. Create a GitHub Release in `kubeflow/mcp-server`.

   Use a tag that exactly matches the package version, target the merged commit
   on `main`, and include the release notes in the release body. Publishing the
   GitHub Release triggers the `Release` workflow.

6. Approve the `release` environment gate in GitHub Actions.

   After approval, the workflow publishes the built artifacts to PyPI using OIDC
   trusted publishing.

7. Verify the published package.

   ```sh
   pip install kubeflow-mcp==X.Y.Z
   kubeflow-mcp --version
   ```

## Test PyPI Dry Run

Use Test PyPI before publishing when validating a release candidate or checking
the publishing path.

1. Go to GitHub Actions -> `Release` -> `Run workflow`.
2. Select the branch or tag that contains the version you want to test.
3. Set `test_pypi` to `true`.
4. Approve the `test-pypi` environment gate.
5. Verify the package from Test PyPI.

   ```sh
   pip install \
     --index-url https://test.pypi.org/simple/ \
     --extra-index-url https://pypi.org/simple/ \
     kubeflow-mcp==X.Y.ZrcN
   kubeflow-mcp --version
   ```

Each Test PyPI upload must use a version that has not already been uploaded to
Test PyPI.

## Trusted Publisher Setup

Configure trusted publishing for both PyPI and Test PyPI. The workflow uses
`id-token: write` permissions and does not read a PyPI token from secrets.

For PyPI, add a publisher for the `kubeflow-mcp` project with these values:

| Field | Value |
| --- | --- |
| Owner | `kubeflow` |
| Repository name | `mcp-server` |
| Workflow name | `release.yaml` |
| Environment name | `release` |

For Test PyPI, add a publisher for the `kubeflow-mcp` project with these values:

| Field | Value |
| --- | --- |
| Owner | `kubeflow` |
| Repository name | `mcp-server` |
| Workflow name | `release.yaml` |
| Environment name | `test-pypi` |

Create matching GitHub environments named `release` and `test-pypi`. Configure
required reviewers on those environments if manual approval is required before
publishing.
