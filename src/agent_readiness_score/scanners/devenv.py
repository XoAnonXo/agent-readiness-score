"""Development environment scanner with multi-language support."""

from agent_readiness_score.core.scanner import BaseScanner, Check, universal, py, js, go, rust, ruby, java, swift, csharp, cpp, php, elixir, dart
from agent_readiness_score.core.models import Category
from agent_readiness_score.core.registry import ScannerRegistry
from agent_readiness_score.core.language import Language, LanguageStats


@ScannerRegistry.register
class DevEnvScanner(BaseScanner):
    """Scans for development environment configurations across all languages."""

    @property
    def category(self) -> Category:
        return Category.DEVENV

    @property
    def name(self) -> str:
        return "Dev Environments"

    @property
    def description(self) -> str:
        return "Checks for containerization, devcontainers, and reproducible environments"

    def get_checks(self, lang_stats: LanguageStats | None = None) -> list[Check]:
        return [
            # ===== Dev Containers (Universal) =====
            universal(".devcontainer/devcontainer.json", ".devcontainer.json", name="DevContainer config", weight=2.0),
            universal(".devcontainer/Dockerfile", name="DevContainer Dockerfile", weight=1.5),
            universal(".gitpod.yml", name="Gitpod config", weight=1.5),
            universal(".github/codespaces/*", name="GitHub Codespaces", weight=1.5),

            # ===== Nix (Universal) =====
            universal("flake.nix", name="Nix flake", weight=1.5),
            universal("shell.nix", "default.nix", name="Nix shell", weight=1.2),
            universal(".envrc", name="direnv config", weight=1.0),

            # ===== Docker (Universal) =====
            universal("docker-compose.dev.yml", "docker-compose.override.yml", name="Docker Compose (dev)", weight=1.2),
            universal("Dockerfile.dev", "dev.Dockerfile", name="Dev Dockerfile", weight=1.0),

            # ===== Environment Templates (Universal) =====
            universal(".env.example", ".env.template", ".env.sample", ".env.local.example", name="Env template", weight=1.0),

            # ===== IDE Configs (Universal) =====
            universal(".vscode/settings.json", name="VS Code settings", weight=0.8),
            universal(".vscode/extensions.json", name="VS Code extensions", weight=0.8),
            universal(".vscode/launch.json", name="VS Code launch config", weight=0.8),
            universal(".vscode/tasks.json", name="VS Code tasks", weight=0.5),
            universal(".idea/", "*.iml", name="IntelliJ IDEA config", weight=0.8),
            universal(".editorconfig", name="EditorConfig", weight=0.8),

            # ===== Version Managers (Universal) =====
            universal(".tool-versions", name="asdf versions", weight=1.2),
            universal(".mise.toml", "mise.toml", name="mise config", weight=1.2),
            universal(".rtx.toml", name="rtx config", weight=1.0),

            # ===== Python =====
            py(".python-version", name="Python version (pyenv)", weight=1.0),
            py("Pipfile", name="Pipenv", weight=1.0),
            py("poetry.toml", "poetry.lock", name="Poetry", weight=1.0),
            py("pdm.lock", "pdm.toml", name="PDM", weight=1.0),
            py(".venv/", "venv/", name="Virtual environment", weight=0.8),
            py("requirements-dev.txt", "requirements/dev.txt", name="Dev requirements", weight=0.8),
            py("pyenv.cfg", name="venv config", weight=0.5),
            py("hatch.toml", "[tool.hatch]", name="Hatch config", weight=1.0),

            # ===== JavaScript/TypeScript =====
            js(".nvmrc", ".node-version", name="Node version", weight=1.0),
            js(".npmrc", name="npm config", weight=0.8),
            js(".yarnrc", ".yarnrc.yml", name="Yarn config", weight=0.8),
            js(".pnpmrc", name="pnpm config", weight=0.8),
            js(".browserslistrc", "browserslist", name="Browserslist", weight=0.8),
            js("volta.json", name="Volta config", weight=1.0),

            # ===== Go =====
            go("go.work", name="Go workspace", weight=1.0),
            go(".go-version", name="Go version", weight=0.8),
            go("tools.go", "tools/tools.go", name="Go tools file", weight=1.0),

            # ===== Rust =====
            rust("rust-toolchain.toml", "rust-toolchain", name="Rust toolchain", weight=1.5),
            rust(".cargo/config.toml", name="Cargo config", weight=1.0),

            # ===== Ruby =====
            ruby(".ruby-version", name="Ruby version", weight=1.0),
            ruby(".ruby-gemset", name="RVM gemset", weight=0.8),
            ruby(".rvmrc", name="RVM config", weight=0.5),
            ruby(".rbenv-vars", name="rbenv vars", weight=0.5),
            ruby("Brewfile", name="Homebrew deps", weight=1.0),
            ruby("bin/setup", "bin/dev", name="Setup scripts", weight=1.2),
            ruby("Procfile.dev", name="Foreman dev", weight=1.0),

            # ===== Java/Kotlin =====
            java(".sdkmanrc", name="SDKMAN config", weight=1.2),
            java(".java-version", name="Java version", weight=1.0),
            java("gradle.properties", name="Gradle properties", weight=0.8),
            java(".mvn/jvm.config", name="Maven JVM config", weight=0.8),

            # ===== Swift =====
            swift(".swift-version", name="Swift version", weight=1.0),
            swift("Mintfile", name="Mint packages", weight=1.0),

            # ===== C# =====
            csharp("global.json", name=".NET global.json", weight=1.2),
            csharp("omnisharp.json", name="OmniSharp config", weight=0.8),
            csharp("Directory.Build.props", name="MSBuild props", weight=0.8),
            csharp(".config/dotnet-tools.json", name=".NET tools", weight=1.0),

            # ===== C/C++ =====
            cpp("CMakePresets.json", name="CMake presets", weight=1.2),
            cpp(".clangd", name="clangd config", weight=0.8),
            cpp("compile_commands.json", name="Compile commands", weight=1.0),
            cpp(".ccls", "ccls.json", name="ccls config", weight=0.8),

            # ===== PHP =====
            php(".php-version", name="PHP version", weight=1.0),
            php("Homestead.yaml", name="Laravel Homestead", weight=1.0),
            php("docker-compose.yml", name="Docker (Laravel)", weight=0.8),
            php("sail", "docker-compose.yml", name="Laravel Sail", weight=1.0),

            # ===== Elixir =====
            elixir(".elixir-version", ".erlang-version", name="Elixir/Erlang version", weight=1.0),
            elixir(".iex.exs", name="IEx config", weight=0.5),

            # ===== Dart/Flutter =====
            dart(".fvm/", "fvm_config.json", name="Flutter version", weight=1.0),
            dart("android/", "ios/", name="Flutter platforms", weight=0.8),

            # ===== Vagrant (Universal) =====
            universal("Vagrantfile", name="Vagrant", weight=1.0),
            universal(".vagrant/", name="Vagrant data", weight=0.5),

            # ===== Kubernetes (Universal) =====
            universal("skaffold.yaml", name="Skaffold config", weight=1.2),
            universal("tilt.yaml", "Tiltfile", name="Tilt config", weight=1.2),
            universal("telepresence.yaml", name="Telepresence", weight=1.0),
            universal("k8s/", "kubernetes/", "charts/", name="K8s manifests", weight=1.0),
        ]
