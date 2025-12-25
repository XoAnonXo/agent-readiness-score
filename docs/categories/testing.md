# Testing Category (20% Weight)

The Testing category measures the quality and comprehensiveness of your test infrastructure. Testing is the **highest-weighted category** because tests are the primary mechanism for AI agents to verify their changes work correctly.

## Why Testing Matters for Agents

AI coding agents rely heavily on tests to:

1. **Validate Changes** - Run tests to confirm new code works
2. **Prevent Regressions** - Ensure changes don't break existing functionality
3. **Understand Behavior** - Read tests to learn how code should behave
4. **Build Confidence** - Higher test coverage = more confident autonomous changes

**Without comprehensive testing, agents cannot safely modify code.**

## What This Category Checks

### Test Frameworks (Weight: 2.0)

Configuration files for test frameworks indicate a project takes testing seriously.

**Python:**
- `pytest.ini` - Pytest configuration
- `pyproject.toml` (with [tool.pytest] section)
- `setup.cfg` (with [tool:pytest] section)
- `tox.ini` - Multi-environment testing

**JavaScript/TypeScript:**
- `jest.config.js` / `jest.config.ts` - Jest configuration
- `vitest.config.ts` - Vitest configuration
- `karma.conf.js` - Karma configuration
- `mocha.opts` / `.mocharc.js` - Mocha configuration

**Go:**
- `*_test.go` files - Go's built-in testing
- `go.mod` with testing dependencies

**Rust:**
- `Cargo.toml` with [dev-dependencies]
- `tests/` directory

**Ruby:**
- `.rspec` - RSpec configuration
- `spec/spec_helper.rb`

**Java/Kotlin:**
- `build.gradle` with testing dependencies
- `pom.xml` with JUnit/TestNG

### Test Directories (Weight: 2.0)

Well-organized test directories show systematic testing approach.

**Common patterns:**
```
tests/              # Python convention
test/               # Many languages
spec/               # Ruby, JavaScript
__tests__/          # JavaScript/React
src/test/           # Java/Kotlin
src/**/test/        # Nested test directories
```

**Best practices:**
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── e2e/            # End-to-end tests
├── fixtures/       # Test data
├── conftest.py     # Pytest fixtures
└── utils/          # Test utilities
```

### Coverage Configuration (Weight: 1.5)

Coverage tracking helps agents understand which code is tested.

**Python:**
- `.coveragerc` - Coverage.py configuration
- `pyproject.toml` with [tool.coverage] section
- `coverage.xml` - Coverage report

**JavaScript/TypeScript:**
- `jest.config.js` with coverage settings
- `coverage/` directory
- `.nycrc` - NYC (Istanbul) configuration

**Go:**
- `go test -cover` usage in CI
- Coverage reports in CI

**Ruby:**
- `SimpleCov` configuration in `spec/spec_helper.rb`

**Coverage thresholds:**
```ini
# .coveragerc
[report]
fail_under = 80
show_missing = true
```

### Test Types

#### Unit Tests (Weight: 1.2)

Fast, isolated tests of individual functions/classes.

**Patterns:**
- `test_*.py` (Python)
- `*_test.go` (Go)
- `*.test.ts` (TypeScript)
- `*.spec.js` (JavaScript)
- `*_spec.rb` (Ruby)
- `*Test.java` (Java)

**Example:**
```python
# test_calculator.py
def test_add():
    assert add(2, 3) == 5

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

#### Integration Tests (Weight: 1.5)

Tests that verify multiple components work together.

**Directories:**
- `tests/integration/`
- `test/integration/`
- `tests/integrations/`

**Example:**
```python
# tests/integration/test_api.py
def test_user_registration_flow():
    # Tests database, API, and validation together
    response = client.post("/register", data=user_data)
    assert response.status_code == 201
    assert User.query.filter_by(email=user_data["email"]).first()
```

#### End-to-End Tests (Weight: 1.5)

Tests that simulate real user workflows.

**Frameworks:**
- Playwright (`playwright.config.ts`)
- Cypress (`cypress.json`, `cypress.config.ts`)
- Selenium (`selenium.config.js`)
- Puppeteer (`jest-puppeteer.config.js`)

**Directories:**
- `e2e/`
- `tests/e2e/`
- `cypress/`

**Example:**
```typescript
// e2e/auth.spec.ts
test('user can login', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name=email]', 'user@example.com');
  await page.fill('[name=password]', 'password');
  await page.click('button[type=submit]');
  await expect(page).toHaveURL('/dashboard');
});
```

### Test Fixtures and Utilities (Weight: 1.0)

Shared test data and helper functions.

**Python:**
- `conftest.py` - Pytest fixtures
- `tests/fixtures/` - Test data files

**JavaScript:**
- `__fixtures__/` - Jest fixtures
- `test/fixtures/` - Test data

**Example:**
```python
# conftest.py
import pytest

@pytest.fixture
def sample_user():
    return User(name="Test User", email="test@example.com")

@pytest.fixture
def db_session():
    session = create_test_session()
    yield session
    session.rollback()
```

### Performance/Benchmark Tests (Weight: 0.5)

Tests that measure code performance.

**Patterns:**
- `tests/performance/`
- `tests/bench/`
- `bench_*.py`
- `*_bench_test.go` (Go)

**Example:**
```python
# tests/performance/test_query_performance.py
def test_query_performance(benchmark):
    result = benchmark(expensive_query)
    assert result.duration < 1.0  # Should complete in < 1 second
```

### Visual Regression Tests (Weight: 0.5)

Tests that detect visual changes.

**Tools:**
- Percy
- Chromatic
- BackstopJS
- Playwright screenshots

**Directories:**
- `tests/visual/`
- `visual-regression/`

## Scoring Examples

### Example 1: Minimal Setup (Score: 25/100)

```
repo/
├── README.md
└── src/
    └── app.py
```

**Detected:**
- Nothing

**Missing:**
- Test framework config
- Test directory
- Any test files

**Score calculation:**
- Found weight: 0
- Total weight: ~20.0
- Score: 0/100 × 100 = 0

**Grade contribution:** 0 × 0.20 = 0

### Example 2: Basic Tests (Score: 50/100)

```
repo/
├── pytest.ini          # ✓ Framework config (2.0)
├── tests/              # ✓ Test directory (2.0)
│   └── test_app.py     # ✓ Unit tests (1.2)
└── src/
    └── app.py
```

**Detected:**
- pytest.ini (2.0)
- tests/ directory (2.0)
- test_*.py files (1.2)

**Missing:**
- Coverage config
- Integration tests
- E2E tests
- Test fixtures

**Score calculation:**
- Found weight: 5.2
- Total weight: ~20.0
- Score: 5.2/20.0 × 100 = 26

**Grade contribution:** 26 × 0.20 = 5.2

### Example 3: Good Testing (Score: 75/100)

```
repo/
├── pytest.ini              # ✓ Framework (2.0)
├── .coveragerc             # ✓ Coverage (1.5)
├── tests/                  # ✓ Test directory (2.0)
│   ├── conftest.py         # ✓ Fixtures (1.0)
│   ├── unit/               # ✓ Unit tests (1.2)
│   │   └── test_app.py
│   └── integration/        # ✓ Integration (1.5)
│       └── test_api.py
└── src/
```

**Detected:**
- pytest.ini (2.0)
- .coveragerc (1.5)
- tests/ (2.0)
- conftest.py (1.0)
- Unit tests (1.2)
- Integration tests (1.5)

**Missing:**
- E2E tests
- Performance tests

**Score calculation:**
- Found weight: 9.2
- Total weight: ~20.0
- Score: 9.2/20.0 × 100 = 46

**Grade contribution:** 46 × 0.20 = 9.2

### Example 4: Excellent Testing (Score: 95/100)

```
repo/
├── pytest.ini                  # ✓ Framework (2.0)
├── .coveragerc                 # ✓ Coverage (1.5)
├── playwright.config.ts        # ✓ E2E framework (1.5)
├── tests/
│   ├── conftest.py             # ✓ Fixtures (1.0)
│   ├── fixtures/               # ✓ Test data (1.0)
│   ├── unit/                   # ✓ Unit tests (1.2)
│   ├── integration/            # ✓ Integration (1.5)
│   ├── e2e/                    # ✓ E2E tests (1.5)
│   ├── performance/            # ✓ Performance (0.5)
│   └── utils/                  # ✓ Test utilities (1.0)
└── src/
```

**Detected:** Nearly everything

**Missing:** Visual regression tests (0.5)

**Score calculation:**
- Found weight: 11.7
- Total weight: 12.2
- Score: 11.7/12.2 × 100 = 95.9

**Grade contribution:** 95.9 × 0.20 = 19.2

## Improvement Roadmap

### Level 1: Basics (Target: 40/100)

**Priority 1:** Add test framework
```bash
# Python
pip install pytest
touch pytest.ini

# JavaScript
npm install --save-dev jest
touch jest.config.js

# Go
# Already built-in, just create tests
touch main_test.go
```

**Priority 2:** Create test directory
```bash
mkdir tests
# Or: mkdir test, spec, __tests__
```

**Priority 3:** Write first tests
```bash
# Python
cat > tests/test_main.py << 'EOF'
def test_example():
    assert 1 + 1 == 2
EOF

# JavaScript
cat > __tests__/main.test.js << 'EOF'
test('addition works', () => {
  expect(1 + 1).toBe(2);
});
EOF
```

**Result:** Score ~40, contribution 8.0

### Level 2: Coverage (Target: 60/100)

**Priority 4:** Add coverage tracking
```bash
# Python
cat > .coveragerc << 'EOF'
[run]
source = src
branch = true

[report]
fail_under = 80
show_missing = true
EOF

# JavaScript (in jest.config.js)
module.exports = {
  collectCoverage: true,
  coverageThreshold: {
    global: {
      lines: 80,
    },
  },
};
```

**Priority 5:** Organize tests by type
```bash
mkdir -p tests/{unit,integration}
mv tests/test_*.py tests/unit/
```

**Result:** Score ~60, contribution 12.0

### Level 3: Comprehensive (Target: 80/100)

**Priority 6:** Add integration tests
```bash
mkdir tests/integration
# Write tests that verify component interaction
```

**Priority 7:** Add E2E tests
```bash
# Install Playwright
npm init playwright@latest

# Or Cypress
npm install --save-dev cypress
npx cypress open
```

**Priority 8:** Add test fixtures
```bash
# Python
cat > tests/conftest.py << 'EOF'
import pytest

@pytest.fixture
def sample_data():
    return {"key": "value"}
EOF

mkdir tests/fixtures
```

**Result:** Score ~80, contribution 16.0

### Level 4: Excellence (Target: 90+/100)

**Priority 9:** Add performance tests
```bash
pip install pytest-benchmark
mkdir tests/performance
```

**Priority 10:** Add visual regression tests
```bash
npm install --save-dev @playwright/test
# Configure screenshot comparison
```

**Priority 11:** Enhance CI integration
```yaml
# .github/workflows/test.yml
- name: Run all test suites
  run: |
    pytest tests/unit
    pytest tests/integration
    pytest tests/e2e
    pytest tests/performance
```

**Result:** Score 90+, contribution 18+

## Best Practices

### 1. Test Organization

**DO:**
```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Component interaction tests
├── e2e/            # Full workflow tests
└── fixtures/       # Shared test data
```

**DON'T:**
```
tests/
└── test_everything.py  # 5000 lines, all mixed together
```

### 2. Test Naming

**DO:**
```python
def test_user_registration_creates_database_record():
    """Clear, descriptive name"""
    pass

def test_login_fails_with_invalid_password():
    """Describes what's being tested and expected outcome"""
    pass
```

**DON'T:**
```python
def test1():
    """Unclear what this tests"""
    pass

def test_stuff():
    """Too vague"""
    pass
```

### 3. Test Independence

**DO:**
```python
@pytest.fixture
def clean_database():
    """Each test gets fresh database"""
    db.create_all()
    yield db
    db.drop_all()

def test_user_creation(clean_database):
    user = User.create(name="Test")
    assert user.id is not None
```

**DON'T:**
```python
# Tests depend on execution order
def test_create_user():
    global user
    user = User.create(name="Test")

def test_user_exists():
    assert user is not None  # Depends on previous test!
```

### 4. Coverage Goals

**Recommended thresholds:**
- **90%+** - Critical business logic
- **80%+** - General application code
- **70%+** - Minimum for new code
- **50%+** - Legacy code being refactored

**Configure in .coveragerc:**
```ini
[report]
fail_under = 80
skip_covered = false
show_missing = true

[html]
directory = htmlcov
```

### 5. Test Speed

**Keep unit tests fast:**
```python
# Fast unit test (< 10ms)
def test_add():
    assert add(2, 3) == 5

# Slow integration test - mark accordingly
@pytest.mark.slow
def test_full_workflow():
    # Database, API, external services
    pass
```

**Run fast tests frequently:**
```bash
# Quick check during development
pytest tests/unit -v

# Full test suite before commit
pytest tests/
```

## Common Pitfalls

### Pitfall 1: Tests Exist But Don't Run in CI

**Problem:** Tests exist locally but aren't in CI pipeline.

**Solution:**
```yaml
# .github/workflows/test.yml
- name: Run tests
  run: pytest tests/ --cov --cov-report=xml
```

### Pitfall 2: Low Coverage

**Problem:** Tests exist but cover only 20% of code.

**Solution:** Set coverage requirements:
```ini
# .coveragerc
[report]
fail_under = 70  # Start here, increase gradually
```

### Pitfall 3: Only Happy Path Testing

**Problem:** Tests only verify things work, not failure cases.

**Solution:** Test error conditions:
```python
def test_divide_by_zero_raises_error():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_invalid_input_returns_400():
    response = client.post("/api/users", data={"invalid": "data"})
    assert response.status_code == 400
```

### Pitfall 4: Flaky Tests

**Problem:** Tests pass/fail randomly.

**Solution:**
- Remove timing dependencies
- Mock external services
- Use fixtures for consistent state
- Avoid global state

## Integration with CI

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run unit tests
        run: pytest tests/unit -v

      - name: Run integration tests
        run: pytest tests/integration -v

      - name: Run E2E tests
        run: pytest tests/e2e -v

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## Quick Wins

**Easiest improvements (30 minutes):**

1. Add `pytest.ini` or `jest.config.js`
2. Create `tests/` directory
3. Write 3-5 basic tests
4. Add `.coveragerc` with 70% threshold

**Result:** Score increases from 0 → ~40

## Further Reading

- [Pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/)
- [Testing Best Practices](https://testingjavascript.com/)
- [Test-Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)

## Next Steps

- Review [Style & Validation](style.md) category
- Set up [CI Integration](../ci-integration.md)
- Check [Scoring System](../scoring-system.md) for calculation details
