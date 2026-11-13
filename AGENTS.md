# AGENTS.md

aiogoogle is an async client for Google's APIs. It has no per-API code. At runtime it fetches an API's discovery document and builds requests from it (`aiogoogle/resource.py`). A session (`aiogoogle/sessions/`) sends them, and the auth managers sign them. A fix that works for one API therefore applies to every API.

- `README.md` is the PyPI landing page.
- `docs/index.rst` holds all of the docs (Sphinx, published on Read the Docs), including the design goals and contribution notes. Update it and `examples/` when user-facing behavior changes.
- To release, follow `.claude/skills/release/SKILL.md`.

## Before pushing

```bash
flake8 .                                        # config in setup.cfg
PYTHONPATH=. python tests/refresh_all_apis.py   # once per checkout; needs network
python -m pytest tests/test_units
```

`tox -e py` runs the same steps as CI, integration tests included. If you touched docstrings or `docs/`, also run `cd docs && make html` (install `docs_requirements.txt` first).

## Gotchas

- Keep the library independent of any one async framework: I/O belongs in sessions, not in the core. aiohttp is the default session and the only full one. The curio and trio sessions raise `NotImplementedError` for some features, such as media upload.
- Don't run `black` on the codebase, despite the README badge. Most files aren't black-formatted, and CI only runs flake8, so reformatting just buries the real change in the diff.
- Unit tests load Google discovery docs from `tests/data/`. That folder is gitignored, so it's empty on a fresh checkout and every API test fails with `FileNotFoundError` until you run `refresh_all_apis.py`. The script prints 404s for some APIs. Those are expected.
- `refresh_all_apis.py` also rewrites the tracked `tests/ALL_APIS.py`. Keep that change locally, because the committed list goes stale and the tests fail without the refreshed one. Leave it out of your commit unless updating the list is the point.
- `tests/test_integration/` calls live Google endpoints (no credentials needed), so it fails offline.
