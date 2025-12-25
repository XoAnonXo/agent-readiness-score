"""Testing scanner with multi-language support."""

from agent_readiness_score.core.scanner import BaseScanner, Check, universal, py, js, ts, go, rust, ruby, java, swift, csharp, cpp, php, elixir, dart
from agent_readiness_score.core.models import Category
from agent_readiness_score.core.registry import ScannerRegistry
from agent_readiness_score.core.language import Language, LanguageStats


@ScannerRegistry.register
class TestingScanner(BaseScanner):
    """Scans for test configurations and test directories across all languages."""

    @property
    def category(self) -> Category:
        return Category.TESTING

    @property
    def name(self) -> str:
        return "Testing"

    @property
    def description(self) -> str:
        return "Checks for test frameworks, coverage, and test directories"

    def get_checks(self, lang_stats: LanguageStats | None = None) -> list[Check]:
        return [
            # ===== Universal Test Directories =====
            universal("tests/", "test/", "__tests__/", "spec/", name="Test directory", weight=2.0),
            universal("e2e/", "integration/", "tests/e2e/", "tests/integration/", name="E2E/Integration tests", weight=1.2),

            # ===== Universal Coverage =====
            universal(".codecov.yml", "codecov.yml", name="Codecov config", weight=1.0),
            universal(".coveralls.yml", name="Coveralls config", weight=0.8),
            universal("sonar-project.properties", name="SonarQube", weight=1.0),

            # ===== Python =====
            py("pytest.ini", "pyproject.toml", "setup.cfg", "conftest.py", name="pytest", weight=1.5),
            py("tox.ini", name="Tox", weight=1.0),
            py("noxfile.py", name="Nox", weight=1.0),
            py(".coveragerc", "pyproject.toml", name="Coverage.py", weight=1.5),
            py("tests/conftest.py", "conftest.py", name="pytest fixtures", weight=1.0),
            py(".hypothesis/*", "conftest.py", name="Hypothesis", weight=1.0),

            # ===== JavaScript/TypeScript =====
            js("jest.config.*", "jest.setup.*", name="Jest", weight=1.5),
            js("vitest.config.*", name="Vitest", weight=1.5),
            js(".mocharc.*", "mocha.opts", name="Mocha", weight=1.0),
            js("karma.conf.js", name="Karma", weight=0.8),
            js("ava.config.*", name="AVA", weight=1.0),
            js("cypress.config.*", "cypress.json", name="Cypress", weight=1.2),
            js("playwright.config.*", name="Playwright", weight=1.5),
            js("nightwatch.conf.js", name="Nightwatch", weight=1.0),
            js("wdio.conf.js", name="WebdriverIO", weight=1.0),
            js(".nycrc*", "nyc.config.js", name="NYC coverage", weight=1.2),
            js("c8.config.*", name="c8 coverage", weight=1.0),
            js("puppeteer.config.*", name="Puppeteer", weight=1.0),
            js("storybook/*", ".storybook/*", name="Storybook", weight=1.0),

            # ===== Go =====
            go("*_test.go", name="Go tests", weight=1.5),
            go("testdata/", name="Go testdata", weight=1.0),
            go(".golangci.yml", name="Go linting", weight=1.0),
            go("go.mod", name="Go modules", weight=0.8),

            # ===== Rust =====
            rust("tests/", name="Rust tests dir", weight=1.5),
            rust("benches/", name="Rust benchmarks", weight=1.0),
            rust("examples/", name="Rust examples", weight=0.8),
            rust("Cargo.toml", name="Cargo test config", weight=0.8),
            rust("proptest-regressions/", name="Proptest", weight=1.0),

            # ===== Ruby =====
            ruby("spec/", name="RSpec specs", weight=1.5),
            ruby(".rspec", name="RSpec config", weight=1.2),
            ruby("spec/spec_helper.rb", "spec/rails_helper.rb", name="RSpec helpers", weight=1.0),
            ruby("test/", name="Minitest", weight=1.2),
            ruby("test/test_helper.rb", name="Minitest helper", weight=1.0),
            ruby("features/", name="Cucumber features", weight=1.0),
            ruby("cucumber.yml", name="Cucumber config", weight=1.0),
            ruby(".simplecov", name="SimpleCov", weight=1.2),
            ruby("Guardfile", name="Guard", weight=0.8),

            # ===== Java/Kotlin =====
            java("src/test/", name="Maven/Gradle test dir", weight=1.5),
            java("src/test/java/", "src/test/kotlin/", name="Test sources", weight=1.2),
            java("src/test/resources/", name="Test resources", weight=1.0),
            java("junit-platform.properties", name="JUnit config", weight=1.0),
            java("testng.xml", name="TestNG", weight=1.0),
            java("jacoco.exec", "jacoco/", name="JaCoCo coverage", weight=1.2),
            java("**/src/test/**/*Test.java", "**/src/test/**/*Test.kt", name="Test files", weight=1.0),
            java("mockito-extensions/", name="Mockito", weight=0.8),

            # ===== Swift =====
            swift("Tests/", name="Swift tests dir", weight=1.5),
            swift("*Tests/", "*Tests.swift", name="XCTest", weight=1.2),
            swift("UITests/", name="UI Tests", weight=1.0),
            swift("*.xctestplan", name="Test plan", weight=1.0),
            swift("Snapshots/", "__Snapshots__/", name="Snapshot tests", weight=1.0),

            # ===== C# =====
            csharp("*.Tests/", "*.Test/", name="Test project", weight=1.5),
            csharp("*.Tests.csproj", "*.Test.csproj", name="Test csproj", weight=1.2),
            csharp("xunit.runner.json", name="xUnit config", weight=1.0),
            csharp("*.UnitTests/", name="Unit tests", weight=1.0),
            csharp("*.IntegrationTests/", name="Integration tests", weight=1.0),
            csharp("coverlet.runsettings", name="Coverlet coverage", weight=1.0),

            # ===== C/C++ =====
            cpp("test/", "tests/", name="C++ tests dir", weight=1.5),
            cpp("*_test.cpp", "*_test.cc", name="Test files", weight=1.0),
            cpp("googletest/", "gtest/", name="Google Test", weight=1.2),
            cpp("catch2/", "catch.hpp", name="Catch2", weight=1.2),
            cpp("doctest/", name="doctest", weight=1.0),
            cpp("CTestTestfile.cmake", name="CTest", weight=1.0),
            cpp("Makefile.test", name="Test makefile", weight=0.8),

            # ===== PHP =====
            php("phpunit.xml", "phpunit.xml.dist", name="PHPUnit", weight=1.5),
            php("tests/", "test/", name="PHP tests dir", weight=1.2),
            php("codeception.yml", name="Codeception", weight=1.2),
            php("behat.yml", name="Behat", weight=1.0),
            php("pest.php", name="Pest", weight=1.2),
            php("phpspec.yml", name="PHPSpec", weight=1.0),

            # ===== Elixir =====
            elixir("test/", name="Elixir test dir", weight=1.5),
            elixir("test/test_helper.exs", name="Test helper", weight=1.0),
            elixir("test/support/", name="Test support", weight=0.8),
            elixir(".formatter.exs", name="Formatter config", weight=0.8),

            # ===== Dart/Flutter =====
            dart("test/", name="Dart test dir", weight=1.5),
            dart("integration_test/", name="Integration tests", weight=1.2),
            dart("*_test.dart", name="Test files", weight=1.0),
            dart("test_driver/", name="Flutter driver tests", weight=1.0),
            dart("coverage/", name="Dart coverage", weight=1.0),

            # ===== Performance/Load Testing =====
            universal("k6.js", "k6/*.js", name="k6 load testing", weight=1.0),
            universal("locustfile.py", name="Locust", weight=1.0),
            universal("artillery.yml", name="Artillery", weight=1.0),
            universal("jmeter/*.jmx", name="JMeter", weight=0.8),
            universal("gatling/", name="Gatling", weight=1.0),
        ]
