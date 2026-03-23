# Contributing to Car Carer

Thank you for your interest in contributing! Car Carer is an open-source project and we welcome contributions of all kinds.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/car-carer.git`
3. Create a branch: `git checkout -b feature/your-feature`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in API keys
6. Run tests: `python -m pytest tests/ -v`

## Development Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py  # http://localhost:8200
```

## Running Tests

```bash
python -m pytest tests/ -v
```

All 65 tests must pass before submitting a PR.

## What to Contribute

Check the [issues labeled "good first issue"](https://github.com/Greal-dev/car-carer/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) for beginner-friendly tasks.

### Areas where help is needed
- **Translations**: Add or improve translations in `app/static/i18n/`
- **Tests**: Increase test coverage for new features
- **Documentation**: Improve README, add API docs, tutorials
- **Docker**: Improve Dockerfile, add healthcheck, Helm chart
- **Frontend**: UI improvements, accessibility, mobile UX

## Code Style

- Python: Follow existing patterns (FastAPI, SQLAlchemy 2.0, Pydantic v2)
- JavaScript: Alpine.js conventions, no build step
- Commit messages: descriptive, imperative mood

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Keep PRs focused (one feature per PR)
4. Add tests for new features

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
