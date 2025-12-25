"""Observability scanner with multi-language support."""

from agent_readiness_score.core.scanner import BaseScanner, Check, universal, py, js, go, rust, ruby, java, swift, csharp, cpp, php, elixir, dart
from agent_readiness_score.core.models import Category
from agent_readiness_score.core.registry import ScannerRegistry
from agent_readiness_score.core.language import Language, LanguageStats


@ScannerRegistry.register
class ObservabilityScanner(BaseScanner):
    """Scans for logging, monitoring, and APM configurations across all languages."""

    @property
    def category(self) -> Category:
        return Category.OBSERVABILITY

    @property
    def name(self) -> str:
        return "Observability"

    @property
    def description(self) -> str:
        return "Checks for logging, monitoring, APM, and error tracking"

    def get_checks(self, lang_stats: LanguageStats | None = None) -> list[Check]:
        return [
            # ===== Universal Monitoring & APM =====
            universal("otel-config.yaml", "otel-collector-config.yaml", "opentelemetry.yaml", name="OpenTelemetry", weight=1.5),
            universal(".sentryclirc", "sentry.properties", "sentry.yaml", name="Sentry config", weight=1.2),
            universal("datadog.yaml", "dd-trace.yaml", "datadog-agent.yaml", name="Datadog", weight=1.2),
            universal("prometheus.yml", "prometheus.yaml", name="Prometheus", weight=1.0),
            universal("grafana/", "dashboards/*.json", name="Grafana dashboards", weight=1.0),
            universal("newrelic.yml", "newrelic.yaml", name="New Relic", weight=1.0),
            universal("elastic-apm-node.js", "elastic-apm.yaml", name="Elastic APM", weight=1.0),
            universal("honeycomb.yaml", ".honeycomb.yaml", name="Honeycomb", weight=1.0),

            # ===== Health Checks (Universal) =====
            universal("**/health*.py", "**/health*.go", "**/health*.ts", "**/health*.js", name="Health endpoint", weight=1.0),
            universal("**/healthcheck*", "**/liveness*", "**/readiness*", name="K8s probes", weight=1.0),

            # ===== Log Management (Universal) =====
            universal("fluent.conf", "fluent-bit.conf", "fluentd.conf", name="Fluentd/Fluent Bit", weight=1.0),
            universal("logstash.conf", "logstash/*.conf", name="Logstash", weight=1.0),
            universal("vector.toml", "vector.yaml", name="Vector", weight=1.0),
            universal("loki-config.yaml", "loki.yaml", name="Loki", weight=1.0),

            # ===== Python =====
            py("logging.conf", "logging.ini", "logging.yaml", name="Python logging config", weight=1.2),
            py("**/logging*.py", "**/logger*.py", name="structlog/loguru", weight=0.8),
            py("sentry_sdk", name="Sentry Python SDK", weight=1.0),
            py("ddtrace", name="Datadog Python", weight=1.0),
            py("opentelemetry-*", name="OpenTelemetry Python", weight=1.0),

            # ===== JavaScript/TypeScript =====
            js("winston.config.*", "**/winston*.js", "**/winston*.ts", name="Winston logger", weight=1.0),
            js("pino.config.*", "**/pino*.js", "**/pino*.ts", name="Pino logger", weight=1.0),
            js("bunyan.config.*", name="Bunyan logger", weight=0.8),
            js("log4js.config.*", "**/log4js*.js", name="Log4js", weight=0.8),
            js("**/sentry.config.*", "sentry.client.config.*", "sentry.server.config.*", name="Sentry JS", weight=1.2),
            js("**/datadog*.js", "**/datadog*.ts", name="Datadog JS", weight=1.0),
            js("**/tracing*.js", "**/tracing*.ts", name="OpenTelemetry JS", weight=1.0),

            # ===== Go =====
            go("**/zap*.go", name="Zap logger", weight=1.0),
            go("**/logrus*.go", name="Logrus logger", weight=1.0),
            go("**/zerolog*.go", name="Zerolog", weight=1.0),
            go("**/log*.go", name="Go logging", weight=0.8),
            go("**/tracing*.go", "**/otel*.go", name="OpenTelemetry Go", weight=1.0),
            go("**/metrics*.go", "**/prometheus*.go", name="Prometheus Go", weight=1.0),

            # ===== Rust =====
            rust("**/tracing*.rs", name="tracing crate", weight=1.2),
            rust("**/log*.rs", name="log crate", weight=0.8),
            rust("**/env_logger*.rs", name="env_logger", weight=0.8),
            rust("**/slog*.rs", name="slog crate", weight=1.0),
            rust("**/opentelemetry*.rs", name="OpenTelemetry Rust", weight=1.0),
            rust("**/metrics*.rs", name="metrics crate", weight=1.0),

            # ===== Ruby =====
            ruby("**/lograge*.rb", "config/initializers/lograge.rb", name="Lograge", weight=1.0),
            ruby("**/semantic_logger*.rb", name="Semantic Logger", weight=1.0),
            ruby("config/initializers/sentry.rb", name="Sentry Ruby", weight=1.0),
            ruby("config/initializers/datadog*.rb", name="Datadog Ruby", weight=1.0),
            ruby("config/initializers/newrelic.rb", name="New Relic Ruby", weight=1.0),
            ruby("**/logging.rb", "**/logger.rb", name="Ruby logger", weight=0.8),
            ruby("lib/tasks/healthcheck*", name="Rails health check", weight=1.0),

            # ===== Java/Kotlin =====
            java("logback.xml", "logback-spring.xml", name="Logback", weight=1.2),
            java("log4j2.xml", "log4j2.yaml", "log4j2.properties", name="Log4j2", weight=1.2),
            java("log4j.xml", "log4j.properties", name="Log4j (legacy)", weight=0.8),
            java("**/logging*.java", "**/Logger*.java", name="Java logging", weight=0.8),
            java("**/Tracing*.java", "**/OpenTelemetry*.java", name="OpenTelemetry Java", weight=1.0),
            java("**/Metrics*.java", "**/Micrometer*.java", name="Micrometer metrics", weight=1.0),
            java("application-monitoring.yml", "application-metrics.yml", name="Spring Boot Actuator", weight=1.0),
            java("**/actuator/*", name="Spring Boot health", weight=1.0),

            # ===== Swift =====
            swift("**/Logging*.swift", "**/Logger*.swift", name="Swift logging", weight=1.0),
            swift("**/OSLog*.swift", name="OSLog (Apple)", weight=0.8),
            swift("**/Analytics*.swift", "**/Tracking*.swift", name="Analytics", weight=1.0),
            swift("**/Crashlytics*.swift", "**/Firebase*.swift", name="Crashlytics", weight=1.0),
            swift("**/Sentry*.swift", name="Sentry Swift", weight=1.0),

            # ===== C# =====
            csharp("**/Serilog*.cs", "serilog.json", name="Serilog", weight=1.2),
            csharp("**/NLog*.cs", "NLog.config", name="NLog", weight=1.0),
            csharp("**/log4net*.cs", "log4net.config", name="log4net", weight=0.8),
            csharp("**/ApplicationInsights*.cs", "ApplicationInsights.config", name="Azure App Insights", weight=1.2),
            csharp("**/OpenTelemetry*.cs", name="OpenTelemetry .NET", weight=1.0),
            csharp("**/HealthCheck*.cs", name=".NET health checks", weight=1.0),

            # ===== C/C++ =====
            cpp("**/spdlog*", name="spdlog", weight=1.0),
            cpp("**/glog*", "**/logging*.cpp", name="Google glog", weight=1.0),
            cpp("**/log4cxx*", name="log4cxx", weight=0.8),
            cpp("**/boost/log*", name="Boost.Log", weight=0.8),

            # ===== PHP =====
            php("**/monolog*.php", "config/logging.php", name="Monolog", weight=1.2),
            php("**/Logger*.php", "**/Logging*.php", name="PHP logging", weight=0.8),
            php("config/sentry.php", name="Sentry Laravel", weight=1.0),
            php("config/datadog.php", name="Datadog Laravel", weight=1.0),
            php("routes/health.php", "**/HealthCheck*.php", name="Laravel health", weight=1.0),

            # ===== Elixir =====
            elixir("**/logger*.ex", "config/logger.exs", name="Elixir Logger", weight=1.0),
            elixir("**/telemetry*.ex", "lib/**/telemetry.ex", name="Telemetry", weight=1.2),
            elixir("config/sentry.exs", "**/Sentry*.ex", name="Sentry Elixir", weight=1.0),
            elixir("lib/**/health*.ex", name="Phoenix health", weight=1.0),

            # ===== Dart/Flutter =====
            dart("**/logger*.dart", "**/logging*.dart", name="Dart logging", weight=1.0),
            dart("**/firebase_crashlytics*", name="Firebase Crashlytics", weight=1.0),
            dart("**/sentry*.dart", name="Sentry Dart", weight=1.0),
            dart("**/analytics*.dart", name="Analytics", weight=0.8),

            # ===== Error Tracking (Universal) =====
            universal("bugsnag.json", ".bugsnag", name="Bugsnag", weight=1.0),
            universal("rollbar.json", ".rollbar", name="Rollbar", weight=1.0),
            universal("raygun.json", name="Raygun", weight=0.8),
            universal("airbrake.yaml", ".airbrake.yml", name="Airbrake", weight=0.8),

            # ===== Feature Flags (Universal) =====
            universal("launchdarkly.yaml", ".launchdarkly/*", name="LaunchDarkly", weight=0.8),
            universal("flagsmith/*", name="Flagsmith", weight=0.8),
            universal("unleash/*", name="Unleash", weight=0.8),
            universal("split.yaml", name="Split.io", weight=0.8),
        ]
