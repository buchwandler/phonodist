# Releasing phonodist

The `v*` GitHub Actions workflow verifies the supported Python matrix, builds one
artifact set, validates it, and publishes those exact artifacts to PyPI.

Before pushing a release tag, configure a PyPI Trusted Publisher for:

- repository: `buchwandler/phonodist`;
- workflow: `.github/workflows/python-publish.yml`;
- environment: `pypi`;
- publishing method: GitHub Actions OpenID Connect (OIDC), with no API token.

The PyPI account and GitHub environment are external configuration. Confirm the
publisher values match the workflow before the first production tag. A TestPyPI
run is recommended before publishing `v0.1.0`.
