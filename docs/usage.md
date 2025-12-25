# Usage Guide

Complete reference for all Agent Readiness Score CLI commands and options.

## Command Overview

```bash
agent-ready [COMMAND] [OPTIONS]
```

**Available Commands:**
- `scan` - Scan a repository and calculate readiness score
- `categories` - List all scoring categories
- `--version` - Show version information
- `--help` - Show help message

## Scan Command

The primary command for analyzing repositories.

### Basic Usage

```bash
# Scan current directory
agent-ready scan .

# Scan specific path
agent-ready scan /path/to/repository

# Scan with absolute path
agent-ready scan ~/projects/my-app
```

### Output Formats

#### Default (Rich Console Output)

```bash
agent-ready scan .
```

Produces a formatted table with:
- Repository metadata
- Category scores with progress bars
- Weighted scores
- Final grade and interpretation

#### Verbose Mode

```bash
agent-ready scan . --verbose
```

Shows all detected indicators:
```
Testing (Score: 85/100)
  ✓ pytest.ini found (weight: 1.5)
  ✓ tests/ directory exists (weight: 1.0)
  ✓ .coveragerc found (weight: 1.2)
  ✗ playwright.config.ts not found
  ✗ cypress.json not found
  ...
```

#### JSON Output

```bash
# Print JSON to stdout
agent-ready scan . --output json

# Save to file
agent-ready scan . --json-file report.json

# Both console and JSON file
agent-ready scan . --verbose --json-file report.json
```

**JSON Schema:**
```json
{
  "repository": "/path/to/repo",
  "scanned_at": "2024-12-25T10:30:00",
  "duration_ms": 45.2,
  "languages": ["Python", "TypeScript"],
  "categories": [
    {
      "name": "Testing",
      "score": 85,
      "weight": 0.20,
      "weighted_score": 17.0,
      "found": 12,
      "total": 14,
      "indicators": [
        {
          "name": "pytest.ini",
          "found": true,
          "weight": 1.5,
          "paths": ["pytest.ini"]
        }
      ]
    }
  ],
  "final_score": 80.8,
  "grade": "B"
}
```

### Filtering Options

#### Minimum Score Threshold

Useful for CI/CD - exits with non-zero code if score is below threshold:

```bash
# Fail if score below 70
agent-ready scan . --min-score 70

# Fail if score below 80
agent-ready scan . --min-score 80

# Use in CI
agent-ready scan . --min-score 75 || exit 1
```

**Exit codes:**
- `0` - Score meets or exceeds threshold
- `1` - Score below threshold or scan error

#### Category Filtering

Focus on specific categories (planned feature):

```bash
# Scan only testing category
agent-ready scan . --categories testing

# Scan multiple categories
agent-ready scan . --categories testing,style,typing

# Exclude categories
agent-ready scan . --exclude dependencies,observability
```

### Path Options

#### Repository Path

```bash
# Current directory
agent-ready scan .

# Relative path
agent-ready scan ./my-project

# Absolute path
agent-ready scan /home/user/projects/my-app

# Home directory shorthand
agent-ready scan ~/projects/my-app
```

#### Ignore Patterns

Exclude directories from scanning:

```bash
# Ignore node_modules
agent-ready scan . --ignore "node_modules"

# Multiple patterns
agent-ready scan . --ignore "node_modules,dist,build"

# Gitignore-style patterns
agent-ready scan . --ignore "*.pyc,__pycache__,venv"
```

### Performance Options

#### Fast Mode

Skip expensive checks for faster scanning:

```bash
agent-ready scan . --fast
```

#### Timeout

Set maximum scan time:

```bash
# 30 second timeout
agent-ready scan . --timeout 30
```

## Categories Command

List all scoring categories with their weights.

```bash
agent-ready categories
```

**Output:**
```
Agent Readiness Categories

┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Category           ┃ Weight ┃ Description                ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Testing            │    20% │ Test frameworks, coverage  │
│ Style & Validation │    15% │ Linters, formatters        │
│ Dev Environments   │    15% │ DevContainers, Docker      │
│ Build Systems      │    10% │ CI/CD, build tools         │
│ Observability      │    10% │ Logging, monitoring        │
│ Dependencies       │    10% │ Lockfiles, security        │
│ Documentation      │    10% │ READMEs, docs              │
│ Static Typing      │    10% │ Type checkers, configs     │
└────────────────────┴────────┴────────────────────────────┘
```

**Verbose mode:**
```bash
agent-ready categories --verbose
```

Shows all indicators checked per category.

## Global Options

### Version

```bash
agent-ready --version
```

Output: `Agent Readiness Score v0.1.0`

### Help

```bash
# Global help
agent-ready --help

# Command-specific help
agent-ready scan --help
agent-ready categories --help
```

### No Color

Disable colored output:

```bash
agent-ready scan . --no-color
```

Useful for:
- CI/CD logs
- Redirecting to files
- Terminals without color support

### Quiet Mode

Suppress all output except errors:

```bash
agent-ready scan . --quiet
```

Use with `--json-file` for silent JSON generation:
```bash
agent-ready scan . --quiet --json-file report.json
```

## Common Usage Patterns

### 1. Quick Repository Check

```bash
agent-ready scan .
```

### 2. Detailed Analysis

```bash
agent-ready scan . --verbose > analysis.txt
```

### 3. CI/CD Quality Gate

```bash
agent-ready scan . --min-score 70 --output json
```

### 4. Generate JSON Report

```bash
agent-ready scan . --json-file report.json --verbose
```

### 5. Compare Before/After

```bash
# Before improvements
agent-ready scan . --json-file before.json

# Make changes...

# After improvements
agent-ready scan . --json-file after.json

# Compare
diff <(jq .final_score before.json) <(jq .final_score after.json)
```

### 6. Category-Specific Analysis

```bash
# See what's missing in testing
agent-ready scan . --verbose | grep -A 20 "Testing"
```

### 7. Multi-Repository Analysis

```bash
#!/bin/bash
for repo in ~/projects/*; do
    echo "Scanning $repo"
    agent-ready scan "$repo" --json-file "$(basename $repo).json"
done
```

### 8. Integration with jq

```bash
# Get final score
agent-ready scan . --output json | jq .final_score

# List failed checks
agent-ready scan . --output json | jq '.categories[].indicators[] | select(.found == false) | .name'

# Find lowest scoring category
agent-ready scan . --output json | jq '.categories | sort_by(.score) | .[0]'
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success (and score meets threshold if `--min-score` used) |
| `1` | Score below threshold or scan error |
| `2` | Invalid arguments or command |
| `130` | User interrupted (Ctrl+C) |

## Environment Variables

### AGENT_READY_CONFIG

Path to custom configuration file:

```bash
export AGENT_READY_CONFIG=~/.config/agent-ready.yaml
agent-ready scan .
```

### AGENT_READY_CACHE_DIR

Override cache directory:

```bash
export AGENT_READY_CACHE_DIR=/tmp/agent-ready-cache
agent-ready scan .
```

### NO_COLOR

Disable colored output (respects [no-color.org](https://no-color.org) standard):

```bash
NO_COLOR=1 agent-ready scan .
```

## Configuration File

Create `agent-ready.yaml` in repository root or `~/.config/agent-ready.yaml`:

```yaml
# Default minimum score
min_score: 70

# Output format
output: "console"  # console, json, or both

# Verbosity
verbose: false

# Categories to scan
categories:
  - testing
  - style
  - typing
  - documentation

# Custom weights (must sum to 1.0)
weights:
  testing: 0.25
  style: 0.20
  devenv: 0.15
  build: 0.10
  observability: 0.10
  dependencies: 0.10
  documentation: 0.05
  typing: 0.05

# Ignore patterns
ignore:
  - "node_modules"
  - "dist"
  - "build"
  - ".venv"
  - "venv"

# Custom checks
custom_checks:
  testing:
    - name: "Custom test runner"
      patterns: ["test.sh", "run-tests.sh"]
      weight: 1.0
```

## Shell Completion

### Bash

```bash
# Generate completion script
agent-ready --install-completion bash

# Add to ~/.bashrc
eval "$(_AGENT_READY_COMPLETE=bash_source agent-ready)"
```

### Zsh

```bash
# Generate completion script
agent-ready --install-completion zsh

# Add to ~/.zshrc
eval "$(_AGENT_READY_COMPLETE=zsh_source agent-ready)"
```

### Fish

```bash
# Generate completion script
agent-ready --install-completion fish

# Completions auto-loaded from ~/.config/fish/completions/
```

## Examples

### Example 1: First-Time Scan

```bash
$ agent-ready scan ~/my-project

╭──────────────────── Agent Readiness Scan ────────────────────╮
│ Repository: /home/user/my-project                            │
│ Languages: Python                                            │
│ Scanned: 2024-12-25 10:30:00                                │
│ Duration: 23.4ms                                             │
╰──────────────────────────────────────────────────────────────╯

              Category Scores
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Category           ┃  Score ┃ Weight ┃ Weighted ┃ Progress   ┃  Found   ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Testing            │     45 │    20% │      9.0 │ ████░░░░░░ │     5/14 │
│ Style Validation   │     30 │    15% │      4.5 │ ███░░░░░░░ │     3/11 │
│ Dev Environments   │     15 │    15% │      2.3 │ █░░░░░░░░░ │     2/12 │
│ Build Systems      │     50 │    10% │      5.0 │ █████░░░░░ │     6/11 │
│ Observability      │     10 │    10% │      1.0 │ █░░░░░░░░░ │     1/9  │
│ Dependencies       │     60 │    10% │      6.0 │ ██████░░░░ │     7/11 │
│ Documentation      │     40 │    10% │      4.0 │ ████░░░░░░ │     5/11 │
│ Static Typing      │     25 │    10% │      2.5 │ ██░░░░░░░░ │     3/13 │
└────────────────────┴────────┴────────┴──────────┴────────────┴──────────┘

╭────────────────── Agent Readiness Score ──────────────────╮
│                                                           │
│ Final Score: 34.3/100  Grade: F                          │
│ Poor - Major infrastructure missing                       │
╰───────────────────────────────────────────────────────────╯
```

### Example 2: Verbose Scan

```bash
$ agent-ready scan . --verbose

Testing (Score: 45/100, Weight: 20%)
  ✓ tests/ directory exists (weight: 1.0)
  ✓ pytest.ini found (weight: 1.5)
  ✓ test_*.py files found (weight: 1.0)
  ✗ .coveragerc not found
  ✗ coverage.py config not found
  ✗ E2E tests not detected
  ✗ integration tests not detected
  ...

Style & Validation (Score: 30/100, Weight: 15%)
  ✓ .ruff.toml found (weight: 1.2)
  ✗ .pre-commit-config.yaml not found
  ✗ .editorconfig not found
  ...
```

### Example 3: CI Integration

```bash
$ agent-ready scan . --min-score 80 --output json
{"final_score": 75.5, ...}
Error: Score 75.5 is below minimum threshold of 80
$ echo $?
1
```

## Tips & Tricks

### Tip 1: Quick Score Check

```bash
alias ars='agent-ready scan .'
ars
```

### Tip 2: Watch Score Improve

```bash
watch -n 5 'agent-ready scan . | grep "Final Score"'
```

### Tip 3: Compare Branches

```bash
# Main branch
git checkout main
agent-ready scan . --json-file main.json

# Feature branch
git checkout feature
agent-ready scan . --json-file feature.json

# Compare
jq -s '.[0].final_score - .[1].final_score' feature.json main.json
```

### Tip 4: Find Quick Wins

```bash
agent-ready scan . --verbose | grep "✗" | head -10
```

Shows the first 10 missing indicators - often easy to add.

### Tip 5: Export to CSV

```bash
agent-ready scan . --output json | jq -r '.categories[] | [.name, .score, .weight, .weighted_score] | @csv' > report.csv
```

## Next Steps

- [Scoring System](scoring-system.md) - Understand how scores are calculated
- [Categories](categories/) - Learn what each category measures
- [CI Integration](ci-integration.md) - Add to your pipeline
- [Extending](extending.md) - Create custom scanners
