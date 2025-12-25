# Agent Readiness Score - Examples

This directory contains example files demonstrating how to use and integrate `agent-ready` in your projects.

## Files

### 1. `sample-output.json`

Example JSON output from scanning a well-configured Python/TypeScript repository with a score of 84.3/100 (Grade B).

**Features demonstrated:**
- Complete JSON report structure
- All 8 scoring categories with findings
- Mix of found and missing checks
- Multi-language detection (Python + TypeScript)
- Detailed findings with file paths

**Usage:**
```bash
# Generate similar output for your repo
agent-ready scan /path/to/your/repo --json-file report.json --output json
```

### 2. `github-action.yml`

Complete GitHub Actions workflow demonstrating various integration patterns.

**Features included:**

1. **Basic scan with minimum threshold**
   - Scans repository on push/PR
   - Fails if score is below 70
   - Uploads report as artifact

2. **PR comments with results**
   - Automatically comments on PRs with score breakdown
   - Shows category-by-category results
   - Includes helpful documentation

3. **Score regression detection**
   - Compares PR score against base branch
   - Fails if score drops significantly
   - Prevents quality degradation

4. **Advanced scanning**
   - Individual category threshold checks
   - Dynamic badge generation
   - Detailed reporting

**Installation:**

```bash
# Copy to your repository
cp examples/github-action.yml .github/workflows/agent-readiness.yml

# Customize thresholds
# Edit the --min-score value and category thresholds as needed

# Commit and push
git add .github/workflows/agent-readiness.yml
git commit -m "Add agent readiness checks"
git push
```

**Customization options:**

```yaml
# Adjust minimum score threshold
--min-score 70  # Change to 60, 80, 90, etc.

# Change when workflow runs
on:
  push:
    branches: [main, develop]  # Add or remove branches
  schedule:
    - cron: '0 0 * * 0'       # Run weekly

# Customize category thresholds
TESTING_SCORE >= 80           # Require high testing coverage
DOCS_SCORE >= 60              # Require minimum documentation
```

## Integration Examples

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: agent-readiness
        name: Check Agent Readiness Score
        entry: agent-ready scan . --min-score 70 --output table
        language: system
        pass_filenames: false
        always_run: true
```

### Makefile Integration

Add to your `Makefile`:

```makefile
.PHONY: check-readiness
check-readiness:
\tagent-ready scan . --verbose --min-score 75

.PHONY: readiness-report
readiness-report:
\tagent-ready scan . --json-file reports/agent-readiness.json
\t@echo "Report saved to reports/agent-readiness.json"

.PHONY: ci-check
ci-check: check-readiness
\t@echo "CI checks passed!"
```

### Package.json Scripts

Add to your `package.json`:

```json
{
  "scripts": {
    "check:readiness": "agent-ready scan . --min-score 70",
    "report:readiness": "agent-ready scan . --json-file agent-readiness.json",
    "pretest": "agent-ready scan . --min-score 60"
  }
}
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
agent-readiness:
  stage: test
  image: python:3.12
  script:
    - pip install agent-readiness-score
    - agent-ready scan . --min-score 70 --json-file report.json
  artifacts:
    reports:
      dotenv: report.json
    paths:
      - report.json
    expire_in: 30 days
```

### CircleCI

Add to `.circleci/config.yml`:

```yaml
jobs:
  agent-readiness:
    docker:
      - image: cimg/python:3.12
    steps:
      - checkout
      - run:
          name: Install agent-ready
          command: pip install agent-readiness-score
      - run:
          name: Check readiness score
          command: agent-ready scan . --min-score 70 --json-file report.json
      - store_artifacts:
          path: report.json
          destination: agent-readiness-report
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any

    stages {
        stage('Agent Readiness Check') {
            steps {
                sh 'pip install agent-readiness-score'
                sh 'agent-ready scan . --min-score 70 --json-file report.json'
                archiveArtifacts artifacts: 'report.json', fingerprint: true
            }
        }
    }
}
```

## Tips for Improving Your Score

### Quick Wins (Easy improvements)

1. **Add a README.md** if you don't have one (+10-15 points)
2. **Add a lockfile** (poetry.lock, package-lock.json, etc.) (+5-10 points)
3. **Add a .gitignore** and basic CI workflow (+5-10 points)
4. **Add a LICENSE file** (+2-5 points)

### Medium Effort

1. **Set up a linter** (Ruff, ESLint, etc.) (+10-15 points)
2. **Add test framework config** (pytest, Jest, etc.) (+10-20 points)
3. **Create a DevContainer** or Dockerfile (+10-15 points)
4. **Add type checking** (mypy, TypeScript) (+5-10 points)

### High Impact

1. **Comprehensive testing setup** with coverage (+20-30 points)
2. **Complete documentation** (README, CONTRIBUTING, docs/) (+15-25 points)
3. **Full CI/CD pipeline** with multiple checks (+15-20 points)
4. **Development environment** with reproducible setup (+15-20 points)

### Target Scores by Project Stage

- **Early prototype**: 30-50 (Grade F/D) - Basic structure
- **Active development**: 50-70 (Grade D/C) - Growing infrastructure
- **Production-ready**: 70-85 (Grade C/B) - Solid practices
- **Enterprise/Open-source**: 85-100 (Grade B/A) - Comprehensive setup

## Troubleshooting

### Score seems low?

Check individual categories with verbose mode:
```bash
agent-ready scan . --verbose
```

Look for easy wins in categories with 0 or low scores.

### Missing language-specific checks?

The scanner auto-detects languages. If checks aren't appearing:
- Ensure you have source files in that language
- Check that files aren't in excluded directories (node_modules, .venv, etc.)

### Want to exclude certain checks?

Currently, all checks are enabled. Future versions will support custom configurations.

## More Examples

See the [main README](../README.md) for:
- CLI usage examples
- Extension/customization guide
- Multi-language support details
- Contribution guidelines

## Questions?

Open an issue on GitHub or check the documentation at:
https://github.com/yourusername/agent-readiness-score
