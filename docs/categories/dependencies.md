# Dependencies Category (10% Weight)

The Dependencies category measures how well your project manages external dependencies. Lockfiles and dependency scanning ensure reproducible builds and security.

## Why Dependencies Matter for Agents

AI agents need reliable dependency management because:

1. **Reproducibility** - Same dependencies everywhere
2. **Security** - Detect vulnerable packages
3. **Stability** - Prevent version conflicts
4. **Automation** - Automated dependency updates
5. **Predictability** - Known dependency behavior

**Without lockfiles, "works on my machine" problems plague agent development.**

## What This Category Checks

### Lockfiles (Weight: 2.5)

Lockfiles pin exact dependency versions.

**Python:**
- `poetry.lock` (Poetry)
- `Pipfile.lock` (Pipenv)
- `requirements.txt` with pinned versions (e.g., `flask==3.0.0`)
- `pdm.lock` (PDM)
- `uv.lock` (uv)

**Example requirements.txt:**
```txt
# Pinned versions
flask==3.0.0
sqlalchemy==2.0.23
requests==2.31.0
pytest==7.4.3
```

**JavaScript/TypeScript:**
- `package-lock.json` (npm)
- `yarn.lock` (Yarn)
- `pnpm-lock.yaml` (pnpm)
- `bun.lockb` (Bun)

**Go:**
- `go.sum` (automatically generated with go.mod)

**Rust:**
- `Cargo.lock`

**Ruby:**
- `Gemfile.lock`

**PHP:**
- `composer.lock`

**.NET:**
- `packages.lock.json`

**Swift:**
- `Package.resolved`

### Dependency Update Automation (Weight: 2.0)

Automated dependency update tools.

**Dependabot:**
- `.github/dependabot.yml`

**Example .github/dependabot.yml:**
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
      - "python"

  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    versioning-strategy: increase

  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
```

**Renovate:**
- `renovate.json`
- `.github/renovate.json`

**Example renovate.json:**
```json
{
  "extends": ["config:base"],
  "packageRules": [
    {
      "matchUpdateTypes": ["minor", "patch"],
      "automerge": true
    }
  ],
  "schedule": ["before 3am on Monday"],
  "labels": ["dependencies"]
}
```

### Security Scanning (Weight: 2.0)

Vulnerability scanning for dependencies.

**Python:**
- `safety` - `.safety-policy.yml`
- `pip-audit`

**JavaScript:**
- `npm audit`
- `yarn audit`
- Snyk configuration

**GitHub:**
- `.github/workflows/security.yml` with dependency scanning

**Example security workflow:**
```yaml
name: Security Scan

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Snyk
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

      - name: Run pip-audit
        run: |
          pip install pip-audit
          pip-audit
```

**Snyk:**
- `.snyk` configuration file

**Example .snyk:**
```yaml
version: v1.22.0
ignore:
  'SNYK-PYTHON-FLASK-123456':
    - '*':
        reason: 'Not affected by this vulnerability'
        expires: '2024-12-31'
```

### Version Constraints (Weight: 1.5)

Clear dependency version specifications.

**Python pyproject.toml:**
```toml
[project]
dependencies = [
    "flask>=3.0.0,<4.0.0",
    "sqlalchemy>=2.0.0,<3.0.0",
    "requests>=2.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "ruff>=0.1.0",
]
```

**JavaScript package.json:**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "~1.6.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

**Go go.mod:**
```go
module github.com/myorg/myapp

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    gorm.io/gorm v1.25.5
)
```

### Dependency Pinning in CI (Weight: 1.0)

**GitHub Actions:**
Using exact versions or hash pinning:

```yaml
steps:
  - uses: actions/checkout@v4.1.1  # Pinned version
  # or
  - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # SHA hash
```

### Package Metadata (Weight: 1.0)

Complete package configuration files.

**Python:**
- `pyproject.toml` with complete metadata
- `setup.py` with version, author, description

**Example pyproject.toml:**
```toml
[project]
name = "myapp"
version = "1.0.0"
description = "My application"
authors = [
    {name = "Your Name", email = "you@example.com"}
]
dependencies = [
    "flask>=3.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**JavaScript package.json:**
```json
{
  "name": "myapp",
  "version": "1.0.0",
  "description": "My application",
  "main": "index.js",
  "author": "Your Name",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/myorg/myapp"
  }
}
```

### Private Package Registry (Weight: 0.5)

Configuration for private registries.

**Python:**
- `.pypirc`
- `pip.conf`

**JavaScript:**
- `.npmrc`

**Example .npmrc:**
```
registry=https://registry.npmjs.org/
@myorg:registry=https://npm.pkg.github.com/
//npm.pkg.github.com/:_authToken=${NPM_TOKEN}
```

## Scoring Examples

### Example 1: No Dependency Management (Score: 0/100)

```
repo/
└── src/
    └── app.py  # No requirements, no lockfile
```

**Score:** 0/100 | **Contribution:** 0

### Example 2: Basic Requirements (Score: 30/100)

```
repo/
├── requirements.txt    # Unpinned versions
└── src/
```

**Score:** ~30/100 | **Contribution:** 3.0

### Example 3: Lockfile (Score: 60/100)

```
repo/
├── pyproject.toml      # ✓ Package metadata (1.0)
├── poetry.lock         # ✓ Lockfile (2.5)
└── src/
```

**Score:** ~60/100 | **Contribution:** 6.0

### Example 4: Good Dependency Management (Score: 80/100)

```
repo/
├── pyproject.toml              # ✓ Metadata (1.0)
├── poetry.lock                 # ✓ Lockfile (2.5)
├── .github/dependabot.yml      # ✓ Auto-updates (2.0)
└── src/
```

**Score:** ~80/100 | **Contribution:** 8.0

### Example 5: Excellent (Score: 95/100)

```
repo/
├── pyproject.toml              # ✓ Metadata (1.0)
├── poetry.lock                 # ✓ Lockfile (2.5)
├── .github/
│   ├── dependabot.yml          # ✓ Updates (2.0)
│   └── workflows/
│       └── security.yml        # ✓ Scanning (2.0)
└── src/
```

**Score:** 95/100 | **Contribution:** 9.5

## Improvement Roadmap

### Level 1: Pin Dependencies (Target: 40/100)

```bash
# Python - pin exact versions
pip freeze > requirements.txt

# Or use Poetry
poetry init
poetry add flask sqlalchemy
# Creates poetry.lock automatically
```

### Level 2: Add Lockfile (Target: 60/100)

```bash
# Python with Poetry
poetry install  # Creates poetry.lock

# JavaScript
npm install     # Creates package-lock.json

# Go
go mod tidy     # Creates/updates go.sum
```

### Level 3: Automated Updates (Target: 80/100)

```bash
mkdir -p .github
cat > .github/dependabot.yml << 'EOF'
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
EOF
```

### Level 4: Security Scanning (Target: 95/100)

```bash
# Add security scanning workflow
cat > .github/workflows/security.yml << 'EOF'
name: Security
on: [push, schedule]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install pip-audit
      - run: pip-audit
EOF
```

## Best Practices

### 1. Always Commit Lockfiles

```gitignore
# .gitignore

# DON'T ignore lockfiles!
# poetry.lock
# package-lock.json
# go.sum
# Cargo.lock

# DO ignore virtual environments
venv/
node_modules/
```

### 2. Use Version Ranges Wisely

```toml
# pyproject.toml

# Good: Allow patch updates
flask = ">=3.0.0,<3.1.0"

# Better: Semantic versioning
flask = "^3.0.0"  # Allows 3.x.x, not 4.x.x

# Risky: No upper bound
flask = ">=3.0.0"

# Too strict: Blocks all updates
flask = "==3.0.0"
```

### 3. Separate Dev Dependencies

```toml
[project]
dependencies = [
    "flask",
    "sqlalchemy",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "ruff",
    "mypy",
]
```

### 4. Regular Updates

```bash
# Weekly: Check for security updates
pip-audit

# Monthly: Update dependencies
poetry update

# Review Dependabot PRs promptly
```

### 5. Test Before Merging Updates

```yaml
# Dependabot will trigger CI
# Make sure tests pass before merging
```

## Common Pitfalls

### Pitfall 1: Ignoring Lockfiles

**Problem:** Lockfile in .gitignore

**Solution:** Commit lockfiles to git

### Pitfall 2: Outdated Dependencies

**Problem:** Dependencies not updated in months/years

**Solution:** Enable Dependabot or Renovate

### Pitfall 3: Wide Version Ranges

**Problem:** `requests>=2.0.0` allows breaking changes

**Solution:** Use semantic versioning: `requests>=2.28.0,<3.0.0`

### Pitfall 4: Mixing Package Managers

**Problem:** Both `requirements.txt` and `poetry.lock`

**Solution:** Choose one and stick with it

## Integration with CI

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    steps:
      - uses: actions/checkout@v4

      # Install from lockfile
      - name: Install dependencies
        run: poetry install --no-root

      # Verify lockfile is up to date
      - name: Check lockfile
        run: poetry check --lock

      # Security audit
      - name: Security scan
        run: poetry run pip-audit
```

## Quick Wins

**20 minutes:**

1. Generate lockfile (poetry lock or npm install)
2. Add .github/dependabot.yml
3. Commit lockfile to git
4. Enable Dependabot on GitHub

**Result:** Score 0 → 70+

## Tool Recommendations

### Python
- **Poetry** - Modern, best-in-class
- **PDM** - Fast alternative
- **pip-tools** - Lightweight

### JavaScript
- **npm** with package-lock.json - Standard
- **pnpm** - Fast, efficient
- **Yarn** - Stable alternative

### Automation
- **Dependabot** - Free, built into GitHub
- **Renovate** - More features, self-hosted option

## Further Reading

- [Poetry Documentation](https://python-poetry.org/)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [Semantic Versioning](https://semver.org/)
- [pip-audit](https://github.com/pypa/pip-audit)

## Next Steps

- Review [Documentation](documentation.md) category
- Learn about [Static Typing](typing.md)
- Check [Extending](../extending.md) guide
