# Installation Guide

This guide covers all methods for installing Agent Readiness Score.

## System Requirements

- **Python**: 3.10 or higher
- **Operating Systems**: Linux, macOS, Windows
- **Dependencies**: typer, rich (automatically installed)

## Installation Methods

### 1. Install from PyPI (Recommended)

The easiest way to install for most users:

```bash
pip install agent-readiness-score
```

Verify installation:
```bash
agent-ready --version
```

**Upgrade to latest version:**
```bash
pip install --upgrade agent-readiness-score
```

### 2. Install with pipx (Isolated Environment)

[pipx](https://pypa.github.io/pipx/) installs the tool in an isolated environment, preventing dependency conflicts with other Python tools.

**Install pipx** (if not already installed):
```bash
# macOS
brew install pipx
pipx ensurepath

# Linux
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Windows
py -m pip install --user pipx
py -m pipx ensurepath
```

**Install agent-ready with pipx:**
```bash
pipx install agent-readiness-score
```

**Benefits of pipx:**
- Isolated environment (no dependency conflicts)
- Automatically added to PATH
- Easy upgrades: `pipx upgrade agent-readiness-score`
- Easy uninstall: `pipx uninstall agent-readiness-score`

### 3. Install from Source

For contributors or users who want the latest development version:

```bash
# Clone the repository
git clone https://github.com/yourusername/agent-readiness-score.git
cd agent-readiness-score

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

**Development dependencies include:**
- pytest - for running tests
- pytest-cov - for coverage reports
- ruff - for linting
- mypy - for type checking

Verify installation:
```bash
agent-ready --version
```

### 4. Install from GitHub Release

Download and install a specific release:

```bash
pip install https://github.com/yourusername/agent-readiness-score/archive/v0.1.0.tar.gz
```

### 5. Install in Virtual Environment

For project-specific installations:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install agent-ready
pip install agent-readiness-score
```

## Docker Installation

Run without installing Python locally:

```bash
# Create a Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.12-slim
RUN pip install agent-readiness-score
WORKDIR /repo
ENTRYPOINT ["agent-ready"]
EOF

# Build image
docker build -t agent-ready .

# Run on your repository
docker run --rm -v $(pwd):/repo agent-ready scan /repo
```

**Quick one-liner (no Dockerfile needed):**
```bash
docker run --rm -v $(pwd):/repo python:3.12-slim sh -c "pip install agent-readiness-score && agent-ready scan /repo"
```

## CI/CD Installation

### GitHub Actions

```yaml
steps:
  - uses: actions/checkout@v4

  - uses: actions/setup-python@v5
    with:
      python-version: '3.12'

  - name: Install agent-ready
    run: pip install agent-readiness-score

  - name: Run scan
    run: agent-ready scan .
```

### GitLab CI

```yaml
agent_readiness:
  image: python:3.12
  before_script:
    - pip install agent-readiness-score
  script:
    - agent-ready scan . --min-score 70
```

### CircleCI

```yaml
version: 2.1
jobs:
  scan:
    docker:
      - image: cimg/python:3.12
    steps:
      - checkout
      - run: pip install agent-readiness-score
      - run: agent-ready scan .
```

### Jenkins

```groovy
pipeline {
    agent {
        docker {
            image 'python:3.12'
        }
    }
    stages {
        stage('Scan') {
            steps {
                sh 'pip install agent-readiness-score'
                sh 'agent-ready scan .'
            }
        }
    }
}
```

## Verification

After installation, verify everything works:

```bash
# Check version
agent-ready --version

# Show help
agent-ready --help

# List categories
agent-ready categories

# Quick scan (should complete without errors)
agent-ready scan .
```

## Troubleshooting

### Command not found

If you get `command not found: agent-ready`:

**Fix 1: Check PATH**
```bash
# Find where pip installed it
python -m pip show agent-readiness-score

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
```

**Fix 2: Use python -m**
```bash
python -m agent_readiness_score.cli scan .
```

**Fix 3: Reinstall with --user**
```bash
pip install --user agent-readiness-score
```

### Permission denied

If you get permission errors during installation:

```bash
# Install for current user only
pip install --user agent-readiness-score

# Or use pipx (recommended)
pipx install agent-readiness-score
```

### Python version too old

Agent Readiness Score requires Python 3.10+. Check your version:

```bash
python --version
```

If too old, install a newer Python:

**macOS (using Homebrew):**
```bash
brew install python@3.12
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/)

### Dependency conflicts

If you get dependency conflicts:

**Solution 1: Use pipx (recommended)**
```bash
pipx install agent-readiness-score
```

**Solution 2: Use virtual environment**
```bash
python -m venv agent-ready-env
source agent-ready-env/bin/activate
pip install agent-readiness-score
```

**Solution 3: Upgrade pip**
```bash
pip install --upgrade pip
pip install agent-readiness-score
```

### Import errors

If you get `ModuleNotFoundError`:

```bash
# Reinstall with dependencies
pip install --force-reinstall agent-readiness-score

# Or install dependencies manually
pip install typer rich
```

## Updating

### Update from PyPI

```bash
pip install --upgrade agent-readiness-score
```

### Update pipx installation

```bash
pipx upgrade agent-readiness-score
```

### Update from source

```bash
cd agent-readiness-score
git pull origin main
pip install -e .
```

## Uninstalling

### Remove pip installation

```bash
pip uninstall agent-readiness-score
```

### Remove pipx installation

```bash
pipx uninstall agent-readiness-score
```

### Clean up completely

```bash
# Uninstall
pip uninstall agent-readiness-score

# Remove cache (optional)
rm -rf ~/.cache/agent-readiness-score
```

## Platform-Specific Notes

### macOS

**Using Homebrew Python:**
```bash
# If you use Homebrew Python
brew install python@3.12
pip3.12 install agent-readiness-score
```

**M1/M2 Macs:**
No special steps needed - the tool is pure Python with no native dependencies.

### Windows

**PowerShell:**
```powershell
# Install
pip install agent-readiness-score

# Run
agent-ready scan .
```

**Git Bash / WSL:**
```bash
pip install agent-readiness-score
agent-ready scan .
```

**Windows PATH:**
Add to PATH if needed:
```
C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python312\Scripts
```

### Linux

**Debian/Ubuntu:**
```bash
# System-wide installation (not recommended)
sudo pip install agent-readiness-score

# User installation (recommended)
pip install --user agent-readiness-score
```

**RHEL/CentOS/Fedora:**
```bash
# Install Python 3.10+ if needed
sudo dnf install python3.12

# Install agent-ready
pip3.12 install agent-readiness-score
```

**Arch Linux:**
```bash
# Python should be recent enough
pip install agent-readiness-score
```

## Development Installation

For contributors who want to modify the code:

```bash
# Clone repository
git clone https://github.com/yourusername/agent-readiness-score.git
cd agent-readiness-score

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy src/
```

## Next Steps

- [Usage Guide](usage.md) - Learn CLI commands
- [Scoring System](scoring-system.md) - Understand how scoring works
- [CI Integration](ci-integration.md) - Add to your pipeline

## Support

Having installation issues?

- Check [Troubleshooting](#troubleshooting) section above
- Open an [issue on GitHub](https://github.com/yourusername/agent-readiness-score/issues)
- Include your OS, Python version, and error message
