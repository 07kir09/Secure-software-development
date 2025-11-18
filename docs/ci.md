# CI/CD pipeline

This repository ships a hardened GitHub Actions workflow that keeps all pull requests and pushes green while producing the artifacts we use for releases.

## Overview of jobs

| Job | Purpose | Notes |
| --- | --- | --- |
| `qa-matrix` | Runs Ruff + tests across a matrix of operating systems (`ubuntu-latest`, `macos-latest`) and Python versions (3.11, 3.12). | Uses pip caching based on `requirements*.txt` and `pyproject.toml`. |
| `quality-reports` | Re-runs the test-suite with coverage enabled, emits JUnit XML + HTML coverage report. | Uploaded as `test-artifacts` for every run. |
| `python-package` | Builds wheel + sdist via `python -m build`. | Outputs `python-package` artifact and feeds release automation. |
| `docker-image` | Builds/pushes the production Docker image to GHCR. | Layer cache stored in GitHub’s registry cache (`type=gha`). |
| `staging-smoke` | Pulls the freshly-built image, loads the AppArmor profile, and runs `docker compose up` to smoke-test `/health`. | Acts as a mock deploy to the staging namespace. |

All jobs run on PRs, pushes to `main`, and on manual dispatch.

## Required secrets/variables

| Name | Type | Used in job | Description |
| --- | --- | --- | --- |
| `APP_API_TOKEN` | Secret | `qa-matrix`, `quality-reports`, `staging-smoke` | Token FastAPI uses to authorize write operations. |
| `CI_DATABASE_URL` | Repository variable | `qa-matrix`, `quality-reports`, `staging-smoke` | SQLAlchemy connection string for CI (defaults to `sqlite:///:memory:` if unset). |
| `CI_CACHE_URL` | Repository variable | `staging-smoke` | Redis DSN for the preview stack. Defaults to the in-compose Redis service. |
| `CI_BROKER_URL` | Repository variable | `staging-smoke` | RabbitMQ DSN for the preview stack. Defaults to the compose service. |

> Tip: when secrets/vars are missing, the workflow falls back to safe defaults so local forks stay buildable, but production repos should fill them in.

## Artifacts

- `test-artifacts`: contains `reports/pytest.xml`, `coverage.xml`, and the generated HTML coverage site.
- `python-package`: includes the wheel and source distribution from `python -m build`.
- Docker image tags: `ghcr.io/<owner>/<repo>:<sha>` (always) and `ghcr.io/<owner>/<repo>:latest` (only on `main`).

Download any artifact from the Actions run page or install the image straight from GHCR.

## Mock deploy / promotion

The `staging-smoke` job promotes the freshly-built container into an ephemeral staging namespace on the runner:

1. Loads the AppArmor profile (`deploy/security/apparmor/secdev-course-app`) with `apparmor_parser`.
2. Pulls the GHCR image produced by the `docker-image` job.
3. Runs `docker compose up --build -d` so the full stack (Postgres, Redis, RabbitMQ, API) boots with hardened options.
4. Polls `http://127.0.0.1:8000/health` until it returns `{"status": "ok"}` and tears the stack down with `docker compose down -v`.

This gives us a deterministic green signal that the container we plan to release can survive a deployment with realistic dependencies.
