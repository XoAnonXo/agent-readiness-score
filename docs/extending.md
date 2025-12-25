# Extending Agent Readiness Score

This guide shows you how to create custom scanners to add organization-specific checks to Agent Readiness Score.

## Why Extend?

The built-in scanners cover common best practices, but your organization may have specific requirements:

- **Internal Tools** - Check for company-specific configurations
- **Compliance** - Ensure regulatory requirements are met
- **Custom Standards** - Enforce team conventions
- **Domain-Specific** - Add checks for your industry (finance, healthcare, etc.)

## Architecture Overview

Agent Readiness Score uses a plugin-based architecture:

```
Scanner Registry
    ↓
Base Scanner (Abstract)
    ↓
Category Scanners (Testing, Style, etc.)
    ↓
Custom Scanners (Your additions)
```

## Creating a Custom Scanner

### Step 1: Basic Scanner Structure

```python
# custom_scanners/security_scanner.py
from agent_readiness_score.core.scanner import BaseScanner
from agent_readiness_score.core.models import Category, Indicator
from agent_readiness_score.core.registry import ScannerRegistry

@ScannerRegistry.register
class SecurityScanner(BaseScanner):
    """Scanner for security-related checks."""

    @property
    def category(self) -> Category:
        """Return the category this scanner belongs to."""
        # You'll need to add SECURITY to the Category enum
        return Category.SECURITY

    @property
    def name(self) -> str:
        """Scanner display name."""
        return "Security"

    @property
    def weight(self) -> float:
        """Category weight (must sum to 1.0 with other categories)."""
        return 0.10  # 10%

    def get_checks(self, lang_stats: dict = None) -> list:
        """Return list of checks to perform.

        Args:
            lang_stats: Dictionary of language statistics (file counts)

        Returns:
            List of tuples: (name, patterns, weight, language_filter)
        """
        return [
            ("Security Policy", ["SECURITY.md", ".github/SECURITY.md"], 2.0, None),
            ("Dependabot", [".github/dependabot.yml"], 1.5, None),
            ("Secret Scanning", [".gitleaks.toml", ".secretlintrc.json"], 1.5, None),
            ("SAST Tool", [".bandit", "sonar-project.properties"], 1.2, None),
            ("Security Headers", ["security_headers.py", "helmet.js"], 1.0, ["python", "javascript"]),
        ]
```

### Step 2: Add to Category Enum

```python
# agent_readiness_score/core/models.py
from enum import Enum

class Category(Enum):
    TESTING = "testing"
    STYLE = "style"
    DEVENV = "devenv"
    BUILD = "build"
    OBSERVABILITY = "observability"
    DEPENDENCIES = "dependencies"
    DOCUMENTATION = "documentation"
    TYPING = "typing"
    SECURITY = "security"  # Your new category
```

### Step 3: Register and Use

```python
# my_project/scan_with_custom.py
from agent_readiness_score.scanner import scan_repository
from custom_scanners.security_scanner import SecurityScanner

# Scanner is automatically registered via decorator
result = scan_repository("/path/to/repo")

print(f"Security Score: {result['categories']['security']['score']}/100")
```

## Advanced: Language-Specific Checks

```python
@ScannerRegistry.register
class PythonSecurityScanner(BaseScanner):
    """Python-specific security scanner."""

    @property
    def category(self) -> Category:
        return Category.SECURITY

    @property
    def name(self) -> str:
        return "Python Security"

    def get_checks(self, lang_stats: dict = None) -> list:
        # Only run if Python is detected
        if not lang_stats or lang_stats.get("python", 0) == 0:
            return []

        return [
            ("Bandit config", [".bandit", "pyproject.toml"], 2.0, ["python"]),
            ("Safety check", ["safety-policy.yml"], 1.5, ["python"]),
            ("Pip audit", [".github/workflows/security.yml"], 1.0, ["python"]),
        ]
```

## Advanced: Dynamic Checks

```python
import os
from pathlib import Path

@ScannerRegistry.register
class ComplianceScanner(BaseScanner):
    """Check for compliance requirements."""

    @property
    def category(self) -> Category:
        return Category.COMPLIANCE

    def get_checks(self, lang_stats: dict = None) -> list:
        checks = [
            ("SOC2 Policy", ["docs/compliance/soc2.md"], 2.0, None),
            ("GDPR Compliance", ["docs/compliance/gdpr.md"], 2.0, None),
        ]

        # Add industry-specific checks
        if self._is_healthcare_project():
            checks.append(
                ("HIPAA Compliance", ["docs/compliance/hipaa.md"], 2.0, None)
            )

        if self._is_financial_project():
            checks.append(
                ("PCI-DSS Compliance", ["docs/compliance/pci-dss.md"], 2.0, None)
            )

        return checks

    def _is_healthcare_project(self) -> bool:
        """Detect if project is healthcare-related."""
        # Check for healthcare-specific files or configs
        return Path("healthcare.yml").exists()

    def _is_financial_project(self) -> bool:
        """Detect if project is finance-related."""
        return Path("financial.yml").exists()
```

## Advanced: Custom Scoring Logic

```python
@ScannerRegistry.register
class TestCoverageScanner(BaseScanner):
    """Scanner that checks actual coverage percentage."""

    @property
    def category(self) -> Category:
        return Category.TESTING

    def scan(self, repo_path: Path) -> dict:
        """Custom scan implementation.

        Override this method for complex scoring logic.
        """
        # Read coverage report
        coverage_file = repo_path / "coverage.xml"
        if not coverage_file.exists():
            return {"score": 0, "details": "No coverage report found"}

        # Parse coverage percentage
        coverage_pct = self._parse_coverage(coverage_file)

        # Score based on coverage
        if coverage_pct >= 90:
            score = 100
        elif coverage_pct >= 80:
            score = 90
        elif coverage_pct >= 70:
            score = 75
        elif coverage_pct >= 60:
            score = 60
        else:
            score = int(coverage_pct)

        return {
            "score": score,
            "details": f"Coverage: {coverage_pct}%",
            "coverage_percentage": coverage_pct,
        }

    def _parse_coverage(self, coverage_file: Path) -> float:
        """Parse coverage percentage from XML."""
        import xml.etree.ElementTree as ET
        tree = ET.parse(coverage_file)
        root = tree.getroot()
        # Extract coverage from XML
        return float(root.attrib.get("line-rate", 0)) * 100
```

## Configuration File Support

```python
# custom_scanners/configurable_scanner.py
import yaml
from pathlib import Path

@ScannerRegistry.register
class ConfigurableScanner(BaseScanner):
    """Scanner that loads checks from configuration."""

    def __init__(self, config_path: str = "agent-ready-custom.yml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            return {"checks": []}

        with open(self.config_path) as f:
            return yaml.safe_load(f)

    @property
    def category(self) -> Category:
        return Category(self.config.get("category", "custom"))

    @property
    def name(self) -> str:
        return self.config.get("name", "Custom Checks")

    def get_checks(self, lang_stats: dict = None) -> list:
        """Load checks from config file."""
        return [
            (
                check["name"],
                check["patterns"],
                check.get("weight", 1.0),
                check.get("languages"),
            )
            for check in self.config.get("checks", [])
        ]
```

**Example configuration file:**
```yaml
# agent-ready-custom.yml
category: security
name: Security Checks
weight: 0.10

checks:
  - name: Security Policy
    patterns:
      - SECURITY.md
      - .github/SECURITY.md
    weight: 2.0

  - name: Internal Security Tool
    patterns:
      - .company-security.yml
    weight: 1.5

  - name: Encryption Config
    patterns:
      - config/encryption.yml
    weight: 1.2
    languages:
      - python
      - javascript
```

## Example: Infrastructure Scanner

```python
@ScannerRegistry.register
class InfrastructureScanner(BaseScanner):
    """Scanner for infrastructure-as-code."""

    @property
    def category(self) -> Category:
        return Category.INFRASTRUCTURE

    @property
    def name(self) -> str:
        return "Infrastructure"

    @property
    def weight(self) -> float:
        return 0.10

    def get_checks(self, lang_stats: dict = None) -> list:
        return [
            # Terraform
            ("Terraform Config", ["*.tf", "main.tf"], 2.0, None),
            ("Terraform Lockfile", [".terraform.lock.hcl"], 1.5, None),
            ("Terraform Docs", ["terraform-docs.yml"], 1.0, None),

            # Kubernetes
            ("K8s Manifests", ["k8s/", "kubernetes/"], 2.0, None),
            ("Helm Charts", ["charts/", "helm/"], 1.5, None),
            ("Kustomize", ["kustomization.yaml"], 1.5, None),

            # AWS
            ("CloudFormation", ["*.template.yaml", "cloudformation/"], 1.5, None),
            ("CDK", ["cdk.json"], 1.5, None),

            # Pulumi
            ("Pulumi Config", ["Pulumi.yaml"], 1.5, None),

            # Ansible
            ("Ansible Playbooks", ["playbook.yml", "ansible/"], 1.5, None),
        ]
```

## Testing Custom Scanners

```python
# tests/test_custom_scanner.py
import pytest
from pathlib import Path
from custom_scanners.security_scanner import SecurityScanner

def test_security_scanner_finds_policy(tmp_path):
    """Test that scanner finds SECURITY.md."""
    # Create test repository
    security_file = tmp_path / "SECURITY.md"
    security_file.write_text("# Security Policy")

    # Run scanner
    scanner = SecurityScanner()
    result = scanner.scan(tmp_path)

    # Assert
    assert result["score"] > 0
    assert "Security Policy" in result["found_indicators"]

def test_security_scanner_without_policy(tmp_path):
    """Test scanner when no security files present."""
    scanner = SecurityScanner()
    result = scanner.scan(tmp_path)

    assert result["score"] == 0
```

## Deployment

### Option 1: Python Package

```python
# setup.py or pyproject.toml
[project]
name = "agent-ready-custom-scanners"
version = "1.0.0"
dependencies = [
    "agent-readiness-score>=0.1.0",
]

[project.entry-points."agent_ready.scanners"]
security = "custom_scanners.security_scanner:SecurityScanner"
infrastructure = "custom_scanners.infrastructure_scanner:InfrastructureScanner"
```

Install and use:
```bash
pip install agent-ready-custom-scanners
agent-ready scan .  # Automatically includes custom scanners
```

### Option 2: Local Plugin Directory

```python
# ~/.config/agent-ready/plugins/my_scanner.py
from agent_readiness_score.core.scanner import BaseScanner
from agent_readiness_score.core.registry import ScannerRegistry

@ScannerRegistry.register
class MyScanner(BaseScanner):
    # Implementation
    pass
```

Configure to load plugins:
```yaml
# ~/.config/agent-ready.yml
plugins:
  - ~/.config/agent-ready/plugins/my_scanner.py
```

### Option 3: Environment Variable

```bash
export AGENT_READY_PLUGINS=/path/to/plugins

# Plugins directory structure:
# /path/to/plugins/
#   ├── __init__.py
#   ├── security.py
#   └── compliance.py
```

## Best Practices

### 1. Start Simple

Begin with file-based checks, add complexity later:
```python
def get_checks(self, lang_stats: dict = None) -> list:
    return [
        ("Config File", ["myconfig.yml"], 1.0, None),
    ]
```

### 2. Use Appropriate Weights

```python
# Critical checks: 2.0
("Critical Config", ["critical.yml"], 2.0, None),

# Important checks: 1.5
("Important Config", ["important.yml"], 1.5, None),

# Standard checks: 1.0
("Standard Config", ["standard.yml"], 1.0, None),

# Nice-to-have: 0.5
("Optional Config", ["optional.yml"], 0.5, None),
```

### 3. Document Your Scanners

```python
@ScannerRegistry.register
class MyScanner(BaseScanner):
    """Scanner for X.

    This scanner checks for:
    - Configuration files
    - Security policies
    - Compliance documents

    Weight: 10% of total score
    Category: Security
    """
    pass
```

### 4. Handle Errors Gracefully

```python
def scan(self, repo_path: Path) -> dict:
    try:
        # Scanning logic
        return {"score": score, "details": details}
    except Exception as e:
        # Log error but don't crash
        return {
            "score": 0,
            "error": str(e),
            "details": "Scanner failed",
        }
```

### 5. Test Thoroughly

```python
def test_scanner_comprehensive():
    """Test scanner with various scenarios."""
    # Test with all files present
    # Test with some files missing
    # Test with invalid files
    # Test edge cases
    pass
```

## Example: Complete Custom Scanner Package

```
my-custom-scanners/
├── pyproject.toml
├── README.md
├── src/
│   └── my_scanners/
│       ├── __init__.py
│       ├── security.py
│       ├── compliance.py
│       └── infrastructure.py
├── tests/
│   ├── test_security.py
│   ├── test_compliance.py
│   └── test_infrastructure.py
└── examples/
    └── usage.py
```

## FAQs

### Q: How do I add a completely new category?

A: Extend the `Category` enum and create a scanner for it. Ensure all category weights sum to 1.0.

### Q: Can I modify existing scanners?

A: Yes, either extend them or create a new scanner that overrides the default behavior.

### Q: How do I contribute scanners back to the main project?

A: Open a pull request at [github.com/yourusername/agent-readiness-score](https://github.com/yourusername/agent-readiness-score).

### Q: Can scanners be language-specific?

A: Yes! Use the `lang_stats` parameter to detect languages and return appropriate checks.

## Further Reading

- [Core Scanner API Documentation](api/scanners.md)
- [Plugin System Architecture](architecture.md)
- [Contributing Guidelines](../CONTRIBUTING.md)

## Support

- Open an [issue](https://github.com/yourusername/agent-readiness-score/issues) for bugs
- Start a [discussion](https://github.com/yourusername/agent-readiness-score/discussions) for questions
- Submit [pull requests](https://github.com/yourusername/agent-readiness-score/pulls) for contributions
