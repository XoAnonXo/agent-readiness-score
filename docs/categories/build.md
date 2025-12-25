# Build Systems Category (10% Weight)

The Build Systems category measures your project's automated build and deployment infrastructure. CI/CD pipelines are essential for AI agents to validate their changes automatically.

## Why Build Systems Matter for Agents

AI agents rely on automated build systems to:

1. **Validate Changes** - CI runs tests on every commit
2. **Quick Feedback** - Know immediately if changes break builds
3. **Deployment Automation** - Changes automatically deployed
4. **Quality Gates** - Enforce standards before merge
5. **Build Consistency** - Same build process everywhere

**Without CI/CD, agents cannot verify their changes work in production-like environments.**

## What This Category Checks

### GitHub Actions (Weight: 2.0)

`.github/workflows/` directory with YAML workflow files.

**Example CI workflow:**
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -e '.[dev]'

      - name: Run tests
        run: pytest --cov

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: chartboost/ruff-action@v1
```

### GitLab CI (Weight: 2.0)

`.gitlab-ci.yml` configuration file.

**Example:**
```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.12
  script:
    - pip install -e '.[dev]'
    - pytest --cov
  coverage: '/TOTAL.*\s+(\d+%)$/'

build:
  stage: build
  script:
    - docker build -t myapp:$CI_COMMIT_SHA .
  only:
    - main

deploy:
  stage: deploy
  script:
    - kubectl apply -f k8s/
  only:
    - main
  when: manual
```

### CircleCI (Weight: 1.5)

`.circleci/config.yml` configuration.

**Example:**
```yaml
version: 2.1

jobs:
  test:
    docker:
      - image: cimg/python:3.12
    steps:
      - checkout
      - run: pip install -e '.[dev]'
      - run: pytest --cov

workflows:
  test-and-deploy:
    jobs:
      - test
```

### Travis CI (Weight: 1.0)

`.travis.yml` configuration file.

### Jenkins (Weight: 1.0)

`Jenkinsfile` configuration.

**Example:**
```groovy
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                sh 'pytest'
            }
        }
        stage('Build') {
            steps {
                sh 'docker build -t myapp .'
            }
        }
    }
}
```

### Build Tools (Weight: 1.5)

Language-specific build configurations.

**Python:**
- `pyproject.toml` with `[build-system]`
- `setup.py`
- `setup.cfg`

**JavaScript/TypeScript:**
- `package.json` with build scripts
- `tsconfig.json`
- `webpack.config.js`
- `vite.config.ts`
- `rollup.config.js`

**Go:**
- `Makefile` with build targets
- `go.mod`

**Rust:**
- `Cargo.toml`

**Java:**
- `pom.xml` (Maven)
- `build.gradle` (Gradle)

### Build Scripts (Weight: 1.2)

Custom build automation scripts.

**Files:**
- `build.sh`
- `scripts/build.sh`
- `build.py`
- `scripts/build.py`

**Example build.sh:**
```bash
#!/bin/bash
set -euo pipefail

echo "Building application..."

# Clean previous builds
rm -rf dist/ build/

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Build package
python -m build

# Build Docker image
docker build -t myapp:latest .

echo "Build complete!"
```

### Release Automation (Weight: 1.0)

Automated release processes.

**GitHub:**
- `.github/workflows/release.yml`
- `.github/workflows/publish.yml`

**Example release workflow:**
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
```

**Semantic Release:**
- `.releaserc`
- `release.config.js`

### Deployment Configurations (Weight: 1.0)

**Files:**
- `Procfile` (Heroku)
- `vercel.json` (Vercel)
- `netlify.toml` (Netlify)
- `fly.toml` (Fly.io)
- `railway.json` (Railway)

**Example Procfile:**
```
web: gunicorn app:app
worker: celery -A app.celery worker
```

**Example vercel.json:**
```json
{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    }
  ]
}
```

## Scoring Examples

### Example 1: No CI (Score: 0/100)

```
repo/
├── README.md
└── src/
```

**Score:** 0/100 | **Contribution:** 0

### Example 2: Basic GitHub Actions (Score: 50/100)

```
repo/
├── .github/
│   └── workflows/
│       └── ci.yml      # ✓ CI (2.0)
├── pyproject.toml      # ✓ Build config (1.5)
└── src/
```

**Score:** ~50/100 | **Contribution:** 5.0

### Example 3: Good CI/CD (Score: 80/100)

```
repo/
├── .github/workflows/
│   ├── ci.yml          # ✓ CI (2.0)
│   └── release.yml     # ✓ Release (1.0)
├── pyproject.toml      # ✓ Build (1.5)
├── Makefile            # ✓ Build scripts (1.2)
└── src/
```

**Score:** ~80/100 | **Contribution:** 8.0

### Example 4: Excellent Build System (Score: 95/100)

```
repo/
├── .github/workflows/
│   ├── ci.yml          # ✓ CI (2.0)
│   ├── release.yml     # ✓ Release (1.0)
│   └── deploy.yml      # ✓ Deploy automation
├── pyproject.toml      # ✓ Build (1.5)
├── Makefile            # ✓ Tasks (1.2)
├── scripts/build.sh    # ✓ Build script (1.2)
└── fly.toml            # ✓ Deploy config (1.0)
```

**Score:** 95/100 | **Contribution:** 9.5

## Improvement Roadmap

### Level 1: Basic CI (Target: 50/100)

```bash
mkdir -p .github/workflows
cat > .github/workflows/ci.yml << 'EOF'
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -e '.[dev]'
      - run: pytest
EOF
```

### Level 2: Multi-Job CI (Target: 70/100)

Add linting, type checking, multiple Python versions:

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    # ...

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: chartboost/ruff-action@v1

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: mypy src/
```

### Level 3: Release Automation (Target: 90/100)

Add automated releases on tags.

## Best Practices

### 1. Fast Feedback

```yaml
# Run fast checks first
jobs:
  lint:  # ~10 seconds
    runs-on: ubuntu-latest
    steps:
      - uses: chartboost/ruff-action@v1

  test:  # ~2 minutes
    needs: lint
    # ...
```

### 2. Cache Dependencies

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'

- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'
```

### 3. Matrix Testing

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python-version: ['3.10', '3.11', '3.12']
```

### 4. Required Status Checks

Configure branch protection to require CI passes before merge.

## Quick Wins

**30 minutes:**

1. Create `.github/workflows/ci.yml`
2. Add test job
3. Add lint job
4. Enable branch protection

**Result:** Score 0 → 60+

## Further Reading

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI Documentation](https://docs.gitlab.com/ee/ci/)
- [CircleCI Documentation](https://circleci.com/docs/)

## Next Steps

- Review [Observability](observability.md) category
- Set up [Dependencies](dependencies.md) management
- Learn about [extending](../extending.md) the scanner
