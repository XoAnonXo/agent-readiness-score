"""Build systems scanner with multi-language support."""

from agent_readiness_score.core.scanner import BaseScanner, Check, universal, py, js, go, rust, ruby, java, swift, csharp, cpp, php, elixir, dart
from agent_readiness_score.core.models import Category
from agent_readiness_score.core.registry import ScannerRegistry
from agent_readiness_score.core.language import Language, LanguageStats


@ScannerRegistry.register
class BuildScanner(BaseScanner):
    """Scans for build system configurations across all languages."""

    @property
    def category(self) -> Category:
        return Category.BUILD

    @property
    def name(self) -> str:
        return "Build Systems"

    @property
    def description(self) -> str:
        return "Checks for build tools, CI/CD configs, and automation"

    def get_checks(self, lang_stats: LanguageStats | None = None) -> list[Check]:
        return [
            # ===== Universal Build Tools =====
            universal("Makefile", "makefile", "GNUmakefile", name="Makefile", weight=1.2),
            universal("justfile", "Justfile", ".justfile", name="Just", weight=1.0),
            universal("Taskfile.yml", "Taskfile.yaml", name="Task", weight=1.0),
            universal("build.sh", "scripts/build.sh", name="Build script", weight=0.8),

            # ===== CI/CD (Universal) =====
            universal(".github/workflows/*.yml", ".github/workflows/*.yaml", name="GitHub Actions", weight=1.5),
            universal(".gitlab-ci.yml", ".gitlab-ci.yaml", name="GitLab CI", weight=1.5),
            universal(".circleci/config.yml", name="CircleCI", weight=1.2),
            universal("Jenkinsfile", name="Jenkins", weight=1.0),
            universal(".travis.yml", name="Travis CI", weight=0.8),
            universal("azure-pipelines.yml", name="Azure Pipelines", weight=1.0),
            universal("bitbucket-pipelines.yml", name="Bitbucket Pipelines", weight=1.0),
            universal(".drone.yml", name="Drone CI", weight=1.0),
            universal("buildkite.yml", ".buildkite/*", name="Buildkite", weight=1.0),
            universal("cloudbuild.yaml", name="Google Cloud Build", weight=1.0),
            universal("appveyor.yml", name="AppVeyor", weight=0.8),
            universal(".woodpecker.yml", name="Woodpecker CI", weight=1.0),

            # ===== Containers (Universal) =====
            universal("Dockerfile", "*.dockerfile", "Dockerfile.*", name="Dockerfile", weight=1.2),
            universal("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml", name="Docker Compose", weight=1.0),
            universal("docker-bake.hcl", name="Docker Bake", weight=0.8),
            universal("Containerfile", name="Podman/Buildah", weight=1.0),

            # ===== Python =====
            py("pyproject.toml", name="pyproject.toml", weight=1.5),
            py("setup.py", name="setup.py", weight=0.8),
            py("setup.cfg", name="setup.cfg", weight=0.8),
            py("tox.ini", name="Tox", weight=1.0),
            py("noxfile.py", name="Nox", weight=1.0),
            py("hatch.toml", name="Hatch", weight=1.0),

            # ===== JavaScript/TypeScript =====
            js("package.json", name="package.json", weight=1.5),
            js("webpack.config.*", name="Webpack", weight=1.0),
            js("vite.config.*", name="Vite", weight=1.2),
            js("rollup.config.*", name="Rollup", weight=1.0),
            js("esbuild.config.*", "esbuild.mjs", name="esbuild", weight=1.0),
            js("turbo.json", name="Turborepo", weight=1.2),
            js("nx.json", name="Nx", weight=1.2),
            js("lerna.json", name="Lerna", weight=0.8),
            js("tsup.config.*", name="tsup", weight=1.0),

            # ===== Go =====
            go("go.mod", name="Go modules", weight=1.5),
            go("Makefile", "magefile.go", name="Go build", weight=1.0),
            go("goreleaser.yml", ".goreleaser.yaml", name="GoReleaser", weight=1.2),
            go("mage.go", "magefile.go", name="Mage", weight=1.0),

            # ===== Rust =====
            rust("Cargo.toml", name="Cargo.toml", weight=1.5),
            rust("build.rs", name="build.rs", weight=1.0),
            rust(".cargo/config.toml", name="Cargo config", weight=0.8),
            rust("Cross.toml", name="Cross (cross-compile)", weight=1.0),

            # ===== Ruby =====
            ruby("Gemfile", name="Gemfile", weight=1.5),
            ruby("Rakefile", name="Rake", weight=1.2),
            ruby("*.gemspec", name="Gemspec", weight=1.0),

            # ===== Java/Kotlin =====
            java("pom.xml", name="Maven", weight=1.5),
            java("build.gradle", "build.gradle.kts", name="Gradle", weight=1.5),
            java("settings.gradle", "settings.gradle.kts", name="Gradle settings", weight=0.8),
            java("gradlew", name="Gradle wrapper", weight=1.0),
            java("mvnw", name="Maven wrapper", weight=1.0),
            java("build.sbt", name="SBT (Scala)", weight=1.2),
            java("build.xml", name="Ant", weight=0.5),

            # ===== Swift =====
            swift("Package.swift", name="Swift Package", weight=1.5),
            swift("*.xcodeproj", "*.xcworkspace", name="Xcode project", weight=1.2),
            swift("Podfile", name="CocoaPods", weight=1.0),
            swift("Cartfile", name="Carthage", weight=0.8),
            swift("project.pbxproj", name="Xcode project file", weight=1.0),
            swift("Fastfile", "fastlane/*", name="Fastlane", weight=1.2),

            # ===== C# =====
            csharp("*.sln", name="Visual Studio Solution", weight=1.5),
            csharp("*.csproj", name="C# Project", weight=1.5),
            csharp("Directory.Build.props", name="MSBuild props", weight=1.0),
            csharp("global.json", name=".NET global.json", weight=0.8),
            csharp("nuget.config", name="NuGet config", weight=0.8),

            # ===== C/C++ =====
            cpp("CMakeLists.txt", name="CMake", weight=1.5),
            cpp("meson.build", name="Meson", weight=1.2),
            cpp("configure.ac", "configure", name="Autoconf", weight=1.0),
            cpp("conanfile.txt", "conanfile.py", name="Conan", weight=1.0),
            cpp("vcpkg.json", name="vcpkg", weight=1.0),
            cpp("premake5.lua", name="Premake", weight=1.0),
            cpp("xmake.lua", name="xmake", weight=1.0),
            cpp("WORKSPACE", "BUILD", name="Bazel", weight=1.2),

            # ===== PHP =====
            php("composer.json", name="Composer", weight=1.5),
            php("artisan", name="Laravel Artisan", weight=1.0),
            php("bin/console", name="Symfony Console", weight=1.0),

            # ===== Elixir =====
            elixir("mix.exs", name="Mix", weight=1.5),
            elixir("rebar.config", name="Rebar3", weight=1.0),

            # ===== Dart/Flutter =====
            dart("pubspec.yaml", name="Dart pubspec", weight=1.5),
            dart("build.yaml", name="Dart build", weight=1.0),

            # ===== Infrastructure =====
            universal("terraform/*.tf", "*.tf", name="Terraform", weight=1.0),
            universal("pulumi/*", "Pulumi.yaml", name="Pulumi", weight=1.0),
            universal("ansible.cfg", "playbook.yml", name="Ansible", weight=0.8),
            universal("serverless.yml", name="Serverless Framework", weight=1.0),
        ]
