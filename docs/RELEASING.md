# Releasing phonodist

The `v*` GitHub Actions workflow runs the supported Python test matrix, builds a
distribution set, validates the artifacts, and publishes those same artifacts to PyPI.

## PyPI authentication

The current publish job uses API-token authentication. The workflow passes the `PYPI_API_TOKEN`
GitHub Actions secret to `pypa/gh-action-pypi-publish` as the `__token__` username/password
credentials. Ensure that secret is available to the `pypi` environment and publish job.

The workflow also grants `id-token: write`, but the publishing action is explicitly given
API-token credentials; the current setup is not tokenless GitHub Actions OIDC Trusted
Publishing. Do not remove the token inputs until a PyPI Trusted Publisher is configured and
the publishing strategy is deliberately changed.

## Release rehearsal

A TestPyPI rehearsal is recommended before changing the production publishing configuration
or performing a high-risk release.
