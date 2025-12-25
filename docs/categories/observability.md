# Observability Category (10% Weight)

The Observability category measures your project's logging, monitoring, and debugging infrastructure. Good observability helps AI agents understand system behavior and debug issues.

## Why Observability Matters for Agents

AI agents benefit from observability because:

1. **Debugging** - Logs help diagnose what went wrong
2. **Understanding Behavior** - See how system actually works
3. **Error Detection** - Catch issues quickly
4. **Performance Insights** - Identify bottlenecks
5. **Production Monitoring** - Track real-world usage

**Without observability, agents work blind - unable to understand failures or behavior.**

## What This Category Checks

### Logging Configuration (Weight: 2.0)

**Python:**
- `logging.conf`
- `logging.ini`
- Python files with logging setup
- `structlog` configuration

**Example logging.ini:**
```ini
[loggers]
keys=root,myapp

[handlers]
keys=console,file

[formatters]
keys=detailed,simple

[logger_root]
level=INFO
handlers=console

[logger_myapp]
level=DEBUG
handlers=console,file
qualname=myapp
propagate=0

[handler_console]
class=StreamHandler
level=DEBUG
formatter=simple
args=(sys.stdout,)

[handler_file]
class=handlers.RotatingFileHandler
level=INFO
formatter=detailed
args=('logs/app.log', 'a', 10485760, 5)

[formatter_simple]
format=%(levelname)s - %(message)s

[formatter_detailed]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

**JavaScript/TypeScript:**
- Winston, Pino, Bunyan configurations
- `logger.ts` / `logger.js`

**Example logger.ts:**
```typescript
import winston from 'winston';

export const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'user-service' },
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple(),
  }));
}
```

### APM Integration (Weight: 1.5)

Application Performance Monitoring tools.

**Configuration files:**
- `newrelic.ini` - New Relic
- `.ddtrace.yml` - Datadog
- `elastic-apm.js` - Elastic APM
- `sentry.properties` - Sentry
- `honeycomb.yml` - Honeycomb

**Example Sentry setup (Python):**
```python
# app.py
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)
```

**Example Sentry config file:**
```properties
# sentry.properties
defaults.url=https://sentry.io/
defaults.org=my-org
defaults.project=my-project
```

### Metrics Collection (Weight: 1.5)

**Prometheus:**
- `prometheus.yml`
- Application exposes `/metrics` endpoint

**Example prometheus.yml:**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'myapp'
    static_configs:
      - targets: ['localhost:8000']
```

**StatsD/Graphite:**
- Configuration in application code
- `statsd.conf`

**OpenTelemetry:**
- `otel-collector-config.yml`
- OpenTelemetry instrumentation

**Example otel-collector-config.yml:**
```yaml
receivers:
  otlp:
    protocols:
      grpc:
      http:

processors:
  batch:

exporters:
  logging:
    loglevel: debug
  otlp:
    endpoint: otelcol:4317

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [logging, otlp]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [logging, otlp]
```

### Error Tracking (Weight: 1.5)

**Sentry:**
- Python: `sentry_sdk` initialization
- JavaScript: `@sentry/node`, `@sentry/react`

**Rollbar:**
- `rollbar` package configuration

**Bugsnag:**
- `bugsnag.yml`

### Health Check Endpoints (Weight: 1.0)

**Files indicating health checks:**
- `health.py` / `health.ts`
- `healthcheck.py` / `healthcheck.ts`
- Routes at `/health`, `/healthz`, `/ready`

**Example health check:**
```python
# health.py
from flask import jsonify

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'database': check_database(),
        'redis': check_redis(),
    })

@app.route('/ready')
def ready():
    return jsonify({'status': 'ready'})
```

### Monitoring Dashboards (Weight: 1.0)

**Grafana:**
- `grafana/` directory with dashboards
- `grafana.ini`
- JSON dashboard files

**Kibana:**
- `kibana.yml`
- Dashboard configurations

### Distributed Tracing (Weight: 1.2)

**Jaeger:**
- `jaeger.yml`
- Jaeger client configuration

**Zipkin:**
- `zipkin.properties`

**OpenTelemetry:**
- Tracing configuration in otel-collector-config.yml

**Example tracing (Python):**
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name='localhost',
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("process_request"):
    # Your code here
    pass
```

### Alerting (Weight: 0.8)

**Configuration files:**
- `alertmanager.yml` (Prometheus Alertmanager)
- PagerDuty integration configs
- `.opsgenie.yml`

**Example alertmanager.yml:**
```yaml
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'team-pager'

receivers:
  - name: 'team-pager'
    pagerduty_configs:
      - service_key: '<pagerduty_service_key>'
```

## Scoring Examples

### Example 1: No Observability (Score: 0/100)

```
repo/
└── src/
    └── app.py  # No logging, no monitoring
```

**Score:** 0/100 | **Contribution:** 0

### Example 2: Basic Logging (Score: 30/100)

```
repo/
├── logging.conf        # ✓ Logging config (2.0)
└── src/
    └── app.py
```

**Score:** ~30/100 | **Contribution:** 3.0

### Example 3: Good Observability (Score: 70/100)

```
repo/
├── logging.conf        # ✓ Logging (2.0)
├── sentry.properties   # ✓ Error tracking (1.5)
├── prometheus.yml      # ✓ Metrics (1.5)
└── src/
    └── health.py       # ✓ Health checks (1.0)
```

**Score:** ~70/100 | **Contribution:** 7.0

### Example 4: Excellent Observability (Score: 95/100)

```
repo/
├── logging.conf                # ✓ Logging (2.0)
├── sentry.properties           # ✓ Sentry (1.5)
├── prometheus.yml              # ✓ Metrics (1.5)
├── otel-collector-config.yml   # ✓ Tracing (1.2)
├── grafana/                    # ✓ Dashboards (1.0)
├── alertmanager.yml            # ✓ Alerts (0.8)
└── src/
    └── health.py               # ✓ Health (1.0)
```

**Score:** 95/100 | **Contribution:** 9.5

## Improvement Roadmap

### Level 1: Basic Logging (Target: 30/100)

```python
# logging_config.py
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'filename': 'app.log',
            'maxBytes': 10485760,
            'backupCount': 5,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file'],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### Level 2: Error Tracking (Target: 50/100)

```bash
# Install Sentry
pip install sentry-sdk

# Add to app.py
import sentry_sdk
sentry_sdk.init(dsn="YOUR_DSN")
```

### Level 3: Metrics (Target: 70/100)

```python
# Install prometheus client
pip install prometheus-client

# Add to app.py
from prometheus_client import Counter, Histogram
from flask import Flask

app = Flask(__name__)
REQUEST_COUNT = Counter('app_requests_total', 'Total requests')
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Request latency')

@app.before_request
def before_request():
    REQUEST_COUNT.inc()
```

### Level 4: Full Observability (Target: 90/100)

Add distributed tracing, health checks, and dashboards.

## Best Practices

### 1. Structured Logging

```python
import structlog

logger = structlog.get_logger()
logger.info("user_login", user_id=123, ip="192.168.1.1")
```

Output:
```json
{"event": "user_login", "user_id": 123, "ip": "192.168.1.1", "timestamp": "2024-12-25T10:30:00Z"}
```

### 2. Log Levels

- **DEBUG**: Detailed diagnostic info
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical issues

### 3. Avoid Logging Secrets

```python
# BAD
logger.info(f"API key: {api_key}")

# GOOD
logger.info("API key configured", key_length=len(api_key))
```

### 4. Health Check Response

```json
{
  "status": "healthy",
  "version": "1.2.3",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "external_api": "degraded"
  },
  "timestamp": "2024-12-25T10:30:00Z"
}
```

## Quick Wins

**30 minutes:**

1. Add logging configuration
2. Set up Sentry (free tier)
3. Add `/health` endpoint
4. Add basic metrics

**Result:** Score 0 → 60+

## Further Reading

- [The 12-Factor App: Logs](https://12factor.net/logs)
- [OpenTelemetry Documentation](https://opentelemetry.io/)
- [Sentry Documentation](https://docs.sentry.io/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)

## Next Steps

- Review [Dependencies](dependencies.md) category
- Learn about [Documentation](documentation.md)
- Check [Typing](typing.md) setup
