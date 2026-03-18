# canvas_v1

> Python + FastAPI project scaffolded with claude-code-forge

## Architecture

This project follows a **6-layer architecture** where dependencies flow strictly forward:

```
Types(0) -> Config(1) -> Repo(2) -> Service(3) -> Runtime(4) -> UI(5)
```

| Layer | Path | Purpose |
|-------|------|---------|
| Types | `src/types/` | Data models, enums, type definitions |
| Config | `src/config/` | Settings, env vars, feature flags |
| Repo | `src/repo/` | Data access, external API clients |
| Service | `src/service/` | Business logic, orchestration |
| Runtime | `src/runtime/` | App bootstrap, middleware, scheduling |
| UI | `src/ui/` | FastAPI routes, request/response handling |

## Getting Started

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -e ".[dev]"

# Run tests
make test

# Run linters
make lint

# Start dev server
make run
```

## Project Structure

```
src/
  types/       # Layer 0: Data models
  config/      # Layer 1: Configuration
  repo/        # Layer 2: Data access
  service/     # Layer 3: Business logic
  runtime/     # Layer 4: App bootstrap
  ui/          # Layer 5: API routes
tests/         # Mirror of src/ structure
specs/
  features/    # Feature specifications
  stories/     # User stories
  design/      # Design documents
  tests/       # Test specifications
  plans/       # Implementation plans
```

## Forge Commands

| Command | Description |
|---------|-------------|
| `/build` | Full pipeline: spec -> design -> implement -> test |
| `/just-do-it` | Quick TDD build without spec ceremony |
| `/scaffold` | Scaffold a new project (already done) |

## Quality Gates

- **Layer linter**: `python .claude/linters/layer_deps.py` - enforces dependency direction
- **File size linter**: `python .claude/linters/file_size.py` - 300 lines/file, 50 lines/function
- **Tests**: `pytest tests/ --cov=src --cov-fail-under=80`
