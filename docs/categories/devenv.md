# Dev Environments Category (15% Weight)

The Dev Environments category measures how well your project supports reproducible development environments. This is critical for AI agents because they need consistent, predictable environments to work effectively.

## Why Dev Environments Matter for Agents

AI coding agents require reproducible environments because:

1. **Consistency** - Same behavior across different machines and CI
2. **Isolation** - Dependencies don't conflict with host system
3. **Onboarding** - Agents can spin up environments automatically
4. **Debugging** - "Works on my machine" problems eliminated
5. **Confidence** - Agents know changes will work in production

**Without reproducible environments:**
- Agents may write code that works locally but fails in CI
- Dependencies conflicts cause unpredictable behavior
- Environmental differences lead to bugs
- Time wasted debugging environment issues

## What This Category Checks

### DevContainers (Weight: 2.5)

VS Code DevContainers and GitHub Codespaces provide fully-configured development environments.

**Configuration files:**
- `.devcontainer/devcontainer.json` - DevContainer configuration
- `.devcontainer/Dockerfile` - Custom container image
- `.devcontainer/docker-compose.yml` - Multi-service setup

**Example .devcontainer/devcontainer.json:**
```json
{
  "name": "Python Development",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",

  "features": {
    "ghcr.io/devcontainers/features/node:1": {
      "version": "20"
    },
    "ghcr.io/devcontainers/features/git:1": {}
  },

  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "editor.formatOnSave": true
      }
    }
  },

  "postCreateCommand": "pip install -e '.[dev]' && pre-commit install",

  "remoteUser": "vscode"
}
```

**Benefits for agents:**
- One-command environment setup
- Identical environment for all developers and CI
- Pre-installed tools and extensions
- Automatic dependency installation

### Docker Compose (Weight: 2.0)

Multi-service development environments with databases, caches, etc.

**Configuration files:**
- `docker-compose.yml`
- `docker-compose.yaml`
- `compose.yml`
- `docker-compose.dev.yml`

**Example docker-compose.yml:**
```yaml
version: '3.8'

services:
  app:
    build: .
    volumes:
      - .:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgres://user:pass@db:5432/mydb
      REDIS_URL: redis://redis:6379
    depends_on:
      - db
      - redis
    command: npm run dev

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

**Usage:**
```bash
docker-compose up -d    # Start all services
docker-compose down     # Stop all services
docker-compose logs -f  # View logs
```

### Dockerfile (Weight: 1.5)

Container image definition for the application.

**Configuration files:**
- `Dockerfile`
- `Dockerfile.dev`
- `docker/Dockerfile`

**Example Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install package
RUN pip install -e .

CMD ["python", "-m", "myapp"]
```

**Multi-stage build example:**
```dockerfile
# Build stage
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:20-slim
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package.json ./
CMD ["node", "dist/index.js"]
```

### Nix (Weight: 2.0)

Purely functional package manager for reproducible builds.

**Configuration files:**
- `flake.nix` - Modern Nix configuration
- `shell.nix` - Development shell
- `default.nix` - Package definition

**Example flake.nix:**
```nix
{
  description = "My development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python312
            python312Packages.pip
            python312Packages.virtualenv
            nodejs_20
            postgresql
            redis
          ];

          shellHook = ''
            echo "Development environment loaded"
            python --version
            node --version
          '';
        };
      }
    );
}
```

**Usage:**
```bash
nix develop        # Enter development shell
nix flake check    # Verify configuration
```

### Vagrant (Weight: 1.0)

VM-based development environments.

**Configuration files:**
- `Vagrantfile`

**Example Vagrantfile:**
```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"

  config.vm.network "forwarded_port", guest: 3000, host: 3000

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
    vb.cpus = 2
  end

  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y python3-pip nodejs npm
    cd /vagrant
    pip3 install -r requirements.txt
  SHELL
end
```

### Environment Variable Templates (Weight: 1.0)

Templates for environment configuration.

**Files:**
- `.env.example` - Template with placeholder values
- `.env.template`
- `.env.sample`
- `env.example`

**Example .env.example:**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# API Keys (get from https://example.com/api)
API_KEY=your_api_key_here
SECRET_KEY=generate_with_openssl_rand_hex_32

# Feature Flags
ENABLE_FEATURE_X=false
DEBUG=false

# External Services
REDIS_URL=redis://localhost:6379
SMTP_HOST=smtp.example.com
SMTP_PORT=587
```

### Virtual Environment Indicators (Weight: 0.5)

Evidence of Python virtual environment usage.

**Indicators:**
- `venv/` directory (in .gitignore)
- `.venv/` directory (in .gitignore)
- `virtualenv/` directory
- `requirements.txt` + instructions to create venv

### Makefile (Weight: 1.2)

Task automation for development workflows.

**Files:**
- `Makefile`
- `makefile`

**Example Makefile:**
```makefile
.PHONY: help install test lint format clean dev

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linters"
	@echo "  make dev      - Start development server"

install:
	pip install -e '.[dev]'
	pre-commit install

test:
	pytest tests/ -v --cov

lint:
	ruff check .
	mypy src/

format:
	ruff format .
	ruff check --fix .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov

dev:
	python -m myapp --reload

docker-dev:
	docker-compose up -d
	docker-compose logs -f app
```

**Usage:**
```bash
make help      # Show available commands
make install   # Set up environment
make dev       # Start development
```

### Task Runners (Weight: 1.0)

Alternative task automation tools.

**Files:**
- `Taskfile.yml` (Task)
- `justfile` (just)
- `package.json` with npm scripts

**Example Taskfile.yml:**
```yaml
version: '3'

tasks:
  install:
    desc: Install dependencies
    cmds:
      - pip install -e '.[dev]'
      - pre-commit install

  test:
    desc: Run tests
    cmds:
      - pytest tests/ -v --cov

  dev:
    desc: Start development server
    cmds:
      - python -m myapp --reload

  docker:dev:
    desc: Start Docker development environment
    cmds:
      - docker-compose up -d
```

**Example package.json scripts:**
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "test": "jest",
    "lint": "eslint . --ext .ts,.tsx",
    "format": "prettier --write .",
    "docker:up": "docker-compose up -d",
    "docker:down": "docker-compose down"
  }
}
```

## Scoring Examples

### Example 1: No Environment Management (Score: 0/100)

```
repo/
├── README.md
└── src/
    └── app.py
```

**Detected:** Nothing

**Score:** 0/100
**Contribution:** 0 × 0.15 = 0

### Example 2: Basic Docker (Score: 30/100)

```
repo/
├── Dockerfile          # ✓ Docker (1.5)
├── .env.example        # ✓ Env template (1.0)
└── src/
```

**Score:** ~30/100
**Contribution:** 30 × 0.15 = 4.5

### Example 3: Good Setup (Score: 70/100)

```
repo/
├── docker-compose.yml      # ✓ Compose (2.0)
├── Dockerfile              # ✓ Dockerfile (1.5)
├── .env.example            # ✓ Env vars (1.0)
├── Makefile                # ✓ Tasks (1.2)
└── src/
```

**Score:** ~70/100
**Contribution:** 70 × 0.15 = 10.5

### Example 4: Excellent Setup (Score: 95/100)

```
repo/
├── .devcontainer/
│   ├── devcontainer.json   # ✓ DevContainer (2.5)
│   └── docker-compose.yml  # ✓ Compose (2.0)
├── Dockerfile              # ✓ Docker (1.5)
├── .env.example            # ✓ Env vars (1.0)
├── Makefile                # ✓ Tasks (1.2)
├── flake.nix               # ✓ Nix (2.0)
└── src/
```

**Score:** 95/100
**Contribution:** 95 × 0.15 = 14.25

## Improvement Roadmap

### Level 1: Environment Variables (Target: 20/100)

**Step 1:** Create .env.example

```bash
cat > .env.example << 'EOF'
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
SECRET_KEY=change_me_in_production
DEBUG=true
EOF
```

**Step 2:** Document environment setup in README

```markdown
## Setup

1. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

2. Edit .env with your values

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
```

**Result:** Score ~20/100

### Level 2: Docker (Target: 40/100)

**Step 3:** Create Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

**Step 4:** Create docker-compose.yml

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - .:/app
```

**Result:** Score ~40/100

### Level 3: DevContainer (Target: 75/100)

**Step 5:** Create .devcontainer/devcontainer.json

```bash
mkdir .devcontainer
cat > .devcontainer/devcontainer.json << 'EOF'
{
  "name": "My Project",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "postCreateCommand": "pip install -e '.[dev]'",
  "customizations": {
    "vscode": {
      "extensions": ["ms-python.python"]
    }
  }
}
EOF
```

**Result:** Score ~75/100

### Level 4: Task Automation (Target: 90/100)

**Step 6:** Create Makefile

```makefile
.PHONY: install dev test

install:
	pip install -e '.[dev]'

dev:
	docker-compose up

test:
	pytest
```

**Result:** Score 90+/100

## Best Practices

### 1. One-Command Setup

**Good:**
```bash
make install && make dev
# or
docker-compose up
# or
nix develop
```

**Bad:**
```bash
# 15 manual steps in README
sudo apt-get install ...
pip install ...
export DATABASE_URL=...
createdb ...
# etc.
```

### 2. Document Prerequisites

```markdown
## Prerequisites

- Docker Desktop
- Make (optional, but recommended)

## Quick Start

```bash
# Clone and start
git clone https://github.com/org/repo.git
cd repo
docker-compose up
```

Visit http://localhost:3000
```

### 3. Ignore Generated Directories

```gitignore
# .gitignore

# Virtual environments
venv/
.venv/
virtualenv/

# Docker volumes
.docker/

# Environment variables (keep .env.example)
.env
.env.local
```

### 4. Multi-Stage Dockerfiles

```dockerfile
# Development
FROM node:20 AS development
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npm", "run", "dev"]

# Production
FROM node:20-slim AS production
WORKDIR /app
COPY --from=development /app/dist ./dist
COPY --from=development /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

Build for development:
```bash
docker build --target development -t myapp:dev .
```

Build for production:
```bash
docker build --target production -t myapp:prod .
```

## Common Pitfalls

### Pitfall 1: Secrets in Version Control

**Problem:** `.env` file committed with real secrets.

**Solution:**
```gitignore
# .gitignore
.env
.env.local
.env.*.local

# Keep templates
!.env.example
```

### Pitfall 2: Platform-Specific Instructions

**Problem:** README says "On Mac, do X. On Linux, do Y."

**Solution:** Use Docker or DevContainers for platform independence.

### Pitfall 3: Outdated Dependencies

**Problem:** Docker image uses old dependencies.

**Solution:** Pin versions and rebuild regularly:
```dockerfile
FROM python:3.12.1-slim  # Pinned version
RUN pip install --no-cache-dir \
    flask==3.0.0 \
    sqlalchemy==2.0.23
```

### Pitfall 4: Missing Service Dependencies

**Problem:** App needs Redis but it's not documented.

**Solution:** Include all services in docker-compose.yml:
```yaml
services:
  app:
    # ...
  redis:
    image: redis:7-alpine
  postgres:
    image: postgres:15
```

## Integration with CI

```yaml
# .github/workflows/test.yml
jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s

    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t myapp .

      - name: Run tests in container
        run: docker-compose run --rm app pytest
```

## Quick Wins

**1 hour setup:**

1. Create `.env.example` (5 minutes)
2. Create `Dockerfile` (15 minutes)
3. Create `docker-compose.yml` (20 minutes)
4. Create `.devcontainer/devcontainer.json` (20 minutes)

**Result:** Score increases from 0 → 70+

## Tool Recommendations

### For Small Projects
- **DevContainer** + **docker-compose.yml**
- Simple, widely supported

### For Large Projects
- **DevContainer** + **Nix flake**
- Maximum reproducibility

### For Teams
- **DevContainer** mandatory
- **Makefile** for common tasks
- **.env.example** with all required vars

## Further Reading

- [DevContainers Specification](https://containers.dev/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nix Flakes](https://nixos.wiki/wiki/Flakes)
- [12-Factor App Methodology](https://12factor.net/)

## Next Steps

- Review [Build Systems](build.md) category
- Set up [CI Integration](../ci-integration.md)
- Learn about [Dependencies](dependencies.md)
