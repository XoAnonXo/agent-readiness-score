# Scoring System

This document explains how Agent Readiness Score calculates the final score from 0-100.

## Overview

The Agent Readiness Score uses a **weighted scoring algorithm** that:

1. Scans for specific indicators in each category
2. Calculates a raw score per category (0-100)
3. Applies category weights to get weighted scores
4. Sums weighted scores to produce final score (0-100)
5. Converts to letter grade (A-F)

## Algorithm

### Step 1: Detect Indicators

For each category, the scanner looks for specific files, directories, or patterns.

**Example - Testing category:**
```
Indicators:
- pytest.ini (weight: 1.5)
- tests/ directory (weight: 1.0)
- .coveragerc (weight: 1.2)
- E2E tests (weight: 1.5)
- Integration tests (weight: 1.0)
...
```

Each indicator has:
- **Name**: What to look for
- **Patterns**: File/directory patterns to match
- **Weight**: Importance multiplier (higher = more important)
- **Language filter**: Optional - only check if language detected

### Step 2: Calculate Category Score

```python
# For each category
found_weight = sum(indicator.weight for indicator in found_indicators)
total_weight = sum(indicator.weight for indicator in all_indicators)

category_score = (found_weight / total_weight) * 100

# Clamp to 0-100
category_score = max(0, min(100, category_score))
```

**Example calculation:**
```
Testing Category:
- Total possible weight: 20.0
- Found weight: 15.5
- Score: (15.5 / 20.0) × 100 = 77.5
```

### Step 3: Apply Category Weights

Each category has a predefined weight that determines its contribution to the final score.

**Default weights:**
```python
CATEGORY_WEIGHTS = {
    "Testing": 0.20,           # 20%
    "Style & Validation": 0.15, # 15%
    "Dev Environments": 0.15,   # 15%
    "Build Systems": 0.10,      # 10%
    "Observability": 0.10,      # 10%
    "Dependencies": 0.10,       # 10%
    "Documentation": 0.10,      # 10%
    "Static Typing": 0.10,      # 10%
}
# Total: 1.00 (100%)
```

### Step 4: Calculate Final Score

```python
final_score = sum(
    category_score * category_weight
    for category in categories
)

# Round to one decimal place
final_score = round(final_score, 1)
```

**Example:**
```
Category Scores and Contributions:
Testing:            77.5 × 0.20 = 15.5
Style & Validation: 85.0 × 0.15 = 12.75
Dev Environments:   60.0 × 0.15 = 9.0
Build Systems:      90.0 × 0.10 = 9.0
Observability:      50.0 × 0.10 = 5.0
Dependencies:       95.0 × 0.10 = 9.5
Documentation:      70.0 × 0.10 = 7.0
Static Typing:      80.0 × 0.10 = 8.0
                    ─────────────────
Final Score:                    75.75 → 75.8/100
```

### Step 5: Assign Letter Grade

```python
def get_grade(score: float) -> str:
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"
```

| Grade | Range | Description |
|-------|-------|-------------|
| **A** | 90-100 | Excellent - Ready for autonomous development |
| **B** | 80-89 | Good - Minor improvements recommended |
| **C** | 70-79 | Moderate - Several areas need attention |
| **D** | 60-69 | Limited - Significant gaps exist |
| **F** | 0-59 | Poor - Major infrastructure missing |

## Category Weights Explained

### Why These Weights?

The weights reflect the **relative importance** of each category for AI agent success:

#### Testing (20%) - Highest Weight

**Why:** Tests are the primary mechanism for agents to verify their changes work correctly.

Without tests:
- Agents can't validate their code works
- Regressions go undetected
- Confidence in agent changes is low

**Impact:** Testing is weighted highest because it's the most critical safety net.

#### Style & Validation (15%) - High Weight

**Why:** Linters and formatters prevent agents from committing broken or non-compliant code.

Benefits:
- Catches syntax errors before commit
- Enforces consistent style
- Prevents common bugs
- Provides immediate feedback

**Impact:** High weight because validation is essential for code quality.

#### Dev Environments (15%) - High Weight

**Why:** Reproducible environments ensure agents work consistently across different machines.

Benefits:
- Docker/DevContainers guarantee consistent environment
- Eliminates "works on my machine" problems
- Simplifies onboarding
- Ensures agent sees same environment as CI

**Impact:** High weight because environmental consistency is crucial.

#### Build Systems (10%) - Medium Weight

**Why:** CI/CD automates validation and deployment.

Benefits:
- Automates testing and deployment
- Validates every change
- Provides fast feedback
- Enforces quality gates

**Impact:** Medium weight - important but not as critical as testing.

#### Observability (10%) - Medium Weight

**Why:** Logging and monitoring help debug agent-generated code.

Benefits:
- Helps diagnose issues in production
- Provides visibility into system behavior
- Enables quick debugging
- Supports incident response

**Impact:** Medium weight - valuable but not essential for basic agent work.

#### Dependencies (10%) - Medium Weight

**Why:** Lockfiles ensure reproducible builds.

Benefits:
- Guarantees same dependencies everywhere
- Prevents "works on my machine" due to version mismatch
- Enables security scanning
- Supports automated updates

**Impact:** Medium weight - important for reliability but not core to agent workflow.

#### Documentation (10%) - Medium Weight

**Why:** Documentation provides context for agents.

Benefits:
- Helps agents understand project structure
- Provides API documentation
- Explains architecture decisions
- Guides contribution process

**Impact:** Medium weight - helpful but modern agents can infer a lot from code.

#### Static Typing (10%) - Medium Weight

**Why:** Type hints help agents understand interfaces and prevent type errors.

Benefits:
- Provides clear interface contracts
- Catches type errors before runtime
- Improves IDE/agent autocomplete
- Serves as documentation

**Impact:** Medium weight - very helpful in typed languages, less relevant in dynamic languages.

## Indicator Weights

Within each category, individual indicators also have weights that reflect their importance.

### Weight Scale

- **0.5** - Nice to have
- **1.0** - Standard indicator
- **1.2** - Important indicator
- **1.5** - Very important indicator
- **2.0** - Critical indicator

### Example: Testing Category Weights

```python
TESTING_INDICATORS = [
    # Critical indicators
    ("Test framework config", ["pytest.ini", "jest.config.js"], 2.0),
    ("Test directory", ["tests/", "test/", "spec/"], 2.0),

    # Very important
    ("Coverage config", [".coveragerc", "coverage.xml"], 1.5),
    ("E2E tests", ["e2e/", "tests/e2e/"], 1.5),

    # Important
    ("Integration tests", ["tests/integration/", "test/integration/"], 1.2),
    ("Test files", ["test_*.py", "*_test.go", "*.test.ts"], 1.2),

    # Standard
    ("Test fixtures", ["tests/fixtures/", "tests/conftest.py"], 1.0),
    ("Test utilities", ["tests/utils/", "tests/helpers/"], 1.0),

    # Nice to have
    ("Performance tests", ["tests/performance/", "tests/bench/"], 0.5),
    ("Visual regression tests", ["tests/visual/"], 0.5),
]
```

### Rationale for Indicator Weights

**High weights (1.5-2.0):**
- Core infrastructure (test frameworks, CI configs)
- Essential for basic functionality
- Hard requirements for agent success

**Medium weights (1.0-1.2):**
- Important but not critical
- Enhance agent capabilities
- Best practices

**Low weights (0.5):**
- Nice to have features
- Advanced capabilities
- Specialized use cases

## Language-Aware Scoring

The scoring system is **language-aware** - it only checks indicators relevant to detected languages.

### Example: Python Project

```python
# Detected languages: ["Python"]

# Python-specific indicators checked:
- pytest.ini ✓
- mypy.ini ✓
- pyproject.toml ✓
- poetry.lock ✓

# TypeScript indicators skipped:
- tsconfig.json (skipped)
- jest.config.ts (skipped)
- package-lock.json (skipped)
```

### Language Detection

```python
# Analyze file extensions
file_counts = {
    ".py": 45,
    ".ts": 3,
    ".js": 8,
}

# Primary language: Python (45 files)
# Secondary: JavaScript/TypeScript (11 files)

# Apply weights:
# - Python indicators: 100% weight
# - TypeScript indicators: 25% weight (11/45)
```

This ensures fair scoring across different language ecosystems.

## Customizing Weights

You can customize category weights via config file:

```yaml
# agent-ready.yaml
weights:
  testing: 0.25        # Increase testing importance
  style: 0.20          # Increase style importance
  devenv: 0.15
  build: 0.10
  observability: 0.05  # Decrease observability
  dependencies: 0.10
  documentation: 0.10
  typing: 0.05         # Decrease typing

# Must sum to 1.0!
```

**When to customize:**
- Your organization has different priorities
- You're working in a specific domain (e.g., embedded systems need less observability)
- You want to emphasize certain practices

## Score Interpretation

### Score Ranges

| Range | Interpretation | Typical Gaps |
|-------|----------------|--------------|
| **90-100** | Excellent - comprehensive infrastructure | Minor missing indicators (e.g., no visual regression tests) |
| **80-89** | Good - most practices in place | Missing 1-2 categories (e.g., no DevContainer) |
| **70-79** | Moderate - core infrastructure exists | Multiple gaps across categories |
| **60-69** | Limited - significant gaps | Missing critical indicators (e.g., no CI, no tests) |
| **50-59** | Poor - minimal infrastructure | Major categories missing entirely |
| **0-49** | Very poor - unsuitable for agents | Fundamental infrastructure absent |

### What Each Grade Means

#### Grade A (90-100): Excellent

**What you have:**
- Comprehensive test suite with coverage tracking
- Linters and formatters configured
- DevContainer or Docker setup
- CI/CD pipeline
- Lockfiles and dependency management
- Good documentation
- Type checking (if applicable)
- Observability basics

**Agent capability:**
- Agents can work autonomously with high confidence
- Changes are validated automatically
- Environment is reproducible
- Minimal human intervention needed

**Recommendation:** Maintain current standards. Consider advanced features (visual testing, performance testing).

#### Grade B (80-89): Good

**What you have:**
- Core testing infrastructure
- Basic linting/formatting
- Some environment reproducibility
- CI pipeline
- Dependency management

**What you might be missing:**
- DevContainer
- Comprehensive coverage config
- Pre-commit hooks
- Advanced observability
- Complete type coverage

**Agent capability:**
- Agents can work effectively with occasional supervision
- Most changes validated automatically
- Environment mostly reproducible

**Recommendation:** Address 1-2 key gaps to reach Grade A.

#### Grade C (70-79): Moderate

**What you have:**
- Basic tests
- Some linting
- CI basics
- README

**What you're missing:**
- Comprehensive test coverage
- Formatter configuration
- DevContainer/Docker
- Dependency lockfiles
- Type checking

**Agent capability:**
- Agents need more supervision
- Manual validation often required
- Environment setup not trivial

**Recommendation:** Focus on testing and dev environment first.

#### Grade D (60-69): Limited

**What you have:**
- Minimal testing
- Maybe some CI
- Basic README

**What you're missing:**
- Most categories incomplete
- Critical infrastructure gaps
- Limited automation

**Agent capability:**
- Agents struggle to work effectively
- High risk of breaking changes
- Significant human oversight required

**Recommendation:** Start with testing, CI, and linting as priorities.

#### Grade F (0-59): Poor

**What you have:**
- Repository exists
- Some code files

**What you're missing:**
- Most infrastructure
- Testing, CI, linting absent
- No reproducibility

**Agent capability:**
- Agents cannot work effectively
- Unsuitable for autonomous development
- Requires complete infrastructure buildout

**Recommendation:** Treat this as a greenfield - start with fundamental infrastructure (tests, CI, linting).

## Mathematical Properties

### Score Bounds

The algorithm guarantees:
```
0 ≤ category_score ≤ 100
0 ≤ final_score ≤ 100
```

### Monotonicity

Adding indicators always increases or maintains the score (never decreases):
```
score(indicators₁ ∪ indicators₂) ≥ max(score(indicators₁), score(indicators₂))
```

### Composability

Final score is a linear combination of category scores:
```
final_score = Σ(category_score_i × weight_i)
```

This means improving any category directly improves the final score proportionally.

## Common Questions

### Q: Why is my score low despite having tests?

**A:** The Testing category checks for multiple indicators, not just test existence. You might be missing:
- Test framework configuration
- Coverage tracking
- E2E/integration tests
- Test organization

### Q: Can I get 100/100?

**A:** Yes, but it requires comprehensive infrastructure across all categories. Very few repositories score 100 - it's an ideal target, not a requirement.

### Q: Why does adding one file change my score so much?

**A:** Some files have high weights (e.g., CI config = 2.0). Adding a critical indicator can boost a category significantly.

### Q: My project doesn't need DevContainers. Does this hurt my score?

**A:** Yes, but you can customize weights to reflect your priorities. See [Customizing Weights](#customizing-weights).

### Q: How often should I check my score?

**A:**
- **Weekly**: During active development
- **Monthly**: For stable projects
- **Every commit**: In CI (with min-score threshold)

### Q: Should I aim for 100?

**A:** Not necessarily. Aim for:
- **90+** for projects with autonomous agents
- **80+** for agent-assisted development
- **70+** for basic agent capability

## Next Steps

- [Categories Overview](categories/) - Understand each category
- [Improving Your Score](#) - Practical guide to score improvement
- [CI Integration](ci-integration.md) - Enforce scores in your pipeline
