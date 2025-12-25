# CI/CD Integration Guide

This guide shows you how to integrate Agent Readiness Score into your CI/CD pipelines and development workflows.

## Why Integrate with CI/CD?

Integrating Agent Readiness Score into CI/CD ensures:

1. **Automated Checks** - Every commit is validated
2. **Quality Gates** - Enforce minimum scores before merge
3. **Trend Tracking** - Monitor score changes over time
4. **Early Detection** - Catch infrastructure gaps immediately
5. **Team Accountability** - Make readiness visible to everyone

## GitHub Actions

### Basic CI Check

```yaml
# .github/workflows/agent-readiness.yml
name: Agent Readiness

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  readiness-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install agent-ready
        run: pip install agent-readiness-score

      - name: Run readiness scan
        run: agent-ready scan . --verbose
```

### With Minimum Score Requirement

```yaml
# .github/workflows/agent-readiness.yml
name: Agent Readiness

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  readiness-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install agent-ready
        run: pip install agent-readiness-score

      - name: Check minimum readiness score
        run: |
          agent-ready scan . --min-score 70 --json-file readiness-report.json

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: readiness-report
          path: readiness-report.json
```

### With Score Comparison (PR Comments)

```yaml
# .github/workflows/agent-readiness.yml
name: Agent Readiness

on:
  pull_request:
    branches: [main]

jobs:
  readiness-check:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      contents: read

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Need full history for comparison

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install agent-ready
        run: pip install agent-readiness-score

      # Scan PR branch
      - name: Scan PR branch
        run: agent-ready scan . --json-file pr-score.json

      # Scan base branch
      - name: Scan base branch
        run: |
          git checkout ${{ github.base_ref }}
          agent-ready scan . --json-file base-score.json
          git checkout -

      # Compare scores
      - name: Compare scores
        id: compare
        run: |
          PR_SCORE=$(jq -r '.final_score' pr-score.json)
          BASE_SCORE=$(jq -r '.final_score' base-score.json)
          DIFF=$(echo "$PR_SCORE - $BASE_SCORE" | bc)

          echo "pr_score=$PR_SCORE" >> $GITHUB_OUTPUT
          echo "base_score=$BASE_SCORE" >> $GITHUB_OUTPUT
          echo "diff=$DIFF" >> $GITHUB_OUTPUT

      # Comment on PR
      - name: Comment PR
        uses: actions/github-script@v7
        with:
          script: |
            const prScore = '${{ steps.compare.outputs.pr_score }}';
            const baseScore = '${{ steps.compare.outputs.base_score }}';
            const diff = '${{ steps.compare.outputs.diff }}';

            const emoji = parseFloat(diff) >= 0 ? '📈' : '📉';
            const change = parseFloat(diff) >= 0 ? 'increased' : 'decreased';

            const comment = `## ${emoji} Agent Readiness Score

            - **PR Score**: ${prScore}/100
            - **Base Score**: ${baseScore}/100
            - **Change**: ${change} by ${Math.abs(diff)} points

            ${parseFloat(diff) < 0 ? '⚠️ Score decreased. Please review infrastructure changes.' : '✅ Score improved or maintained!'}
            `;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### Advanced: Badge Generation

```yaml
# .github/workflows/agent-readiness.yml
name: Agent Readiness Badge

on:
  push:
    branches: [main]

jobs:
  update-badge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install agent-ready
        run: pip install agent-readiness-score

      - name: Generate score
        id: score
        run: |
          SCORE=$(agent-ready scan . --output json | jq -r '.final_score')
          echo "score=$SCORE" >> $GITHUB_OUTPUT

      - name: Create badge
        uses: schneegans/dynamic-badges-action@v1.7.0
        with:
          auth: ${{ secrets.GIST_SECRET }}
          gistID: your-gist-id
          filename: agent-readiness.json
          label: Agent Ready
          message: ${{ steps.score.outputs.score }}/100
          color: ${{ steps.score.outputs.score >= 80 && 'green' || steps.score.outputs.score >= 60 && 'yellow' || 'red' }}
```

Add to README.md:
```markdown
![Agent Readiness](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/yourusername/your-gist-id/raw/agent-readiness.json)
```

## GitLab CI

### Basic Pipeline

```yaml
# .gitlab-ci.yml
stages:
  - test
  - quality

agent-readiness:
  stage: quality
  image: python:3.12
  before_script:
    - pip install agent-readiness-score
  script:
    - agent-ready scan . --verbose
  only:
    - merge_requests
    - main
```

### With Score Requirement

```yaml
# .gitlab-ci.yml
agent-readiness:
  stage: quality
  image: python:3.12
  before_script:
    - pip install agent-readiness-score
  script:
    - agent-ready scan . --min-score 70 --json-file readiness-report.json
  artifacts:
    reports:
      dotenv: readiness-report.json
    paths:
      - readiness-report.json
    expire_in: 30 days
  allow_failure: false
```

### With MR Comments

```yaml
# .gitlab-ci.yml
agent-readiness:
  stage: quality
  image: python:3.12
  before_script:
    - pip install agent-readiness-score
  script:
    - SCORE=$(agent-ready scan . --output json | jq -r '.final_score')
    - echo "Agent Readiness Score: $SCORE/100"
    - |
      if [ "$SCORE" -lt 70 ]; then
        echo "❌ Score below threshold (70)"
        exit 1
      else
        echo "✅ Score meets requirements"
      fi
  only:
    - merge_requests
```

## CircleCI

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  agent-readiness:
    docker:
      - image: cimg/python:3.12
    steps:
      - checkout

      - restore_cache:
          keys:
            - v1-dependencies-{{ checksum "requirements.txt" }}

      - run:
          name: Install agent-ready
          command: pip install agent-readiness-score

      - run:
          name: Run readiness scan
          command: |
            agent-ready scan . --json-file readiness-report.json
            agent-ready scan . --min-score 70

      - store_artifacts:
          path: readiness-report.json

workflows:
  version: 2
  build-and-check:
    jobs:
      - agent-readiness:
          filters:
            branches:
              only:
                - main
                - develop
```

## Jenkins

### Declarative Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent {
        docker {
            image 'python:3.12'
        }
    }

    stages {
        stage('Setup') {
            steps {
                sh 'pip install agent-readiness-score'
            }
        }

        stage('Agent Readiness Check') {
            steps {
                sh 'agent-ready scan . --json-file readiness-report.json'

                script {
                    def report = readJSON file: 'readiness-report.json'
                    def score = report.final_score

                    echo "Agent Readiness Score: ${score}/100"

                    if (score < 70) {
                        error("Score ${score} is below minimum threshold of 70")
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'readiness-report.json', fingerprint: true
        }
    }
}
```

### Scripted Pipeline

```groovy
// Jenkinsfile
node {
    docker.image('python:3.12').inside {
        stage('Checkout') {
            checkout scm
        }

        stage('Install') {
            sh 'pip install agent-readiness-score'
        }

        stage('Scan') {
            sh 'agent-ready scan . --json-file readiness-report.json'

            def report = readJSON file: 'readiness-report.json'
            def score = report.final_score

            if (score < 70) {
                error("Agent Readiness Score ${score} below threshold")
            }

            currentBuild.description = "Score: ${score}/100"
        }
    }
}
```

## Travis CI

```yaml
# .travis.yml
language: python
python:
  - "3.12"

install:
  - pip install agent-readiness-score

script:
  - agent-ready scan . --min-score 70 --json-file readiness-report.json

after_success:
  - cat readiness-report.json

deploy:
  provider: releases
  file: readiness-report.json
  skip_cleanup: true
  on:
    tags: true
```

## Pre-commit Hook

### Local Git Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "Running Agent Readiness Check..."

# Run scan
agent-ready scan . --min-score 70

if [ $? -ne 0 ]; then
    echo "❌ Agent Readiness Score below minimum threshold"
    echo "Run 'agent-ready scan . --verbose' to see details"
    exit 1
fi

echo "✅ Agent Readiness Check passed"
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### Pre-commit Framework

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: agent-readiness
        name: Agent Readiness Check
        entry: agent-ready scan . --min-score 70
        language: system
        pass_filenames: false
        always_run: true
        stages: [commit]
```

Install hook:
```bash
pip install pre-commit
pre-commit install
```

## Azure Pipelines

```yaml
# azure-pipelines.yml
trigger:
  - main
  - develop

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.12'

  - script: |
      pip install agent-readiness-score
    displayName: 'Install agent-ready'

  - script: |
      agent-ready scan . --json-file $(Build.ArtifactStagingDirectory)/readiness-report.json
    displayName: 'Run readiness scan'

  - script: |
      SCORE=$(jq -r '.final_score' $(Build.ArtifactStagingDirectory)/readiness-report.json)
      echo "Score: $SCORE/100"
      if [ $(echo "$SCORE < 70" | bc) -eq 1 ]; then
        echo "##vso[task.logissue type=error]Score below threshold"
        exit 1
      fi
    displayName: 'Check minimum score'

  - task: PublishBuildArtifacts@1
    inputs:
      pathToPublish: '$(Build.ArtifactStagingDirectory)'
      artifactName: 'readiness-report'
```

## Bitbucket Pipelines

```yaml
# bitbucket-pipelines.yml
image: python:3.12

pipelines:
  default:
    - step:
        name: Agent Readiness Check
        caches:
          - pip
        script:
          - pip install agent-readiness-score
          - agent-ready scan . --json-file readiness-report.json
          - agent-ready scan . --min-score 70
        artifacts:
          - readiness-report.json

  pull-requests:
    '**':
      - step:
          name: Agent Readiness Check
          script:
            - pip install agent-readiness-score
            - agent-ready scan . --min-score 70 --verbose
```

## Docker Integration

### Dockerfile for CI

```dockerfile
FROM python:3.12-slim

RUN pip install agent-readiness-score

WORKDIR /repo

ENTRYPOINT ["agent-ready", "scan", "/repo"]
CMD ["--verbose"]
```

Build and use:
```bash
docker build -t agent-ready-ci .
docker run --rm -v $(pwd):/repo agent-ready-ci --min-score 70
```

## Monitoring and Tracking

### Track Score Over Time

```bash
#!/bin/bash
# track-score.sh

DATE=$(date +%Y-%m-%d)
SCORE=$(agent-ready scan . --output json | jq -r '.final_score')

# Append to CSV
echo "$DATE,$SCORE" >> .agent-ready-history.csv

# Commit to git
git add .agent-ready-history.csv
git commit -m "Track readiness score: $SCORE on $DATE"
```

### GitHub Actions with History

```yaml
# .github/workflows/track-score.yml
name: Track Readiness Score

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  track:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install agent-ready
        run: pip install agent-readiness-score

      - name: Track score
        run: |
          DATE=$(date +%Y-%m-%d)
          SCORE=$(agent-ready scan . --output json | jq -r '.final_score')
          echo "$DATE,$SCORE" >> .agent-ready-history.csv

      - name: Commit history
        run: |
          git config user.name "Agent Ready Bot"
          git config user.email "bot@example.com"
          git add .agent-ready-history.csv
          git commit -m "Track readiness score" || echo "No changes"
          git push
```

## Best Practices

### 1. Set Realistic Thresholds

```yaml
# Start low, increase gradually
- agent-ready scan . --min-score 50  # Initial
# After improvements
- agent-ready scan . --min-score 70  # Intermediate
# Eventually
- agent-ready scan . --min-score 80  # Target
```

### 2. Cache Dependencies

```yaml
# GitHub Actions
- uses: actions/setup-python@v5
  with:
    cache: 'pip'

# GitLab CI
cache:
  paths:
    - .cache/pip
```

### 3. Fail Fast

```yaml
# Run readiness check early in pipeline
stages:
  - validate
  - test
  - build
  - deploy

readiness:
  stage: validate  # Before expensive tests
```

### 4. Provide Actionable Feedback

```yaml
- name: Readiness check
  run: |
    if ! agent-ready scan . --min-score 70; then
      echo "❌ Score below threshold"
      echo "Run locally: agent-ready scan . --verbose"
      echo "See docs: https://docs.example.com/readiness"
      exit 1
    fi
```

### 5. Don't Block on Day 1

```yaml
# Allow failures initially
- agent-ready scan . --min-score 70
  continue-on-error: true

# After team is aware, make blocking
- agent-ready scan . --min-score 70
  # No continue-on-error
```

## Troubleshooting

### Issue: CI times out

**Solution:** Use `--fast` mode or increase timeout:
```yaml
timeout-minutes: 10
script:
  - agent-ready scan . --fast
```

### Issue: Different scores locally vs CI

**Solution:** Ensure same files are scanned:
```yaml
# Don't use shallow clones
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

### Issue: Score varies between runs

**Solution:** Ensure deterministic scanning (no time-based checks).

## Further Reading

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI Documentation](https://docs.gitlab.com/ee/ci/)
- [Pre-commit Framework](https://pre-commit.com/)

## Next Steps

- Review [Usage Guide](usage.md) for CLI options
- Learn about [Extending](extending.md) for custom checks
- Check [Scoring System](scoring-system.md) for algorithm details
