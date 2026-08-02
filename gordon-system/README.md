# Gordon System

Canonical intelligent agent system scaffold for the Gordon monorepo.

## Overview

Gordon is a canonical intelligent agent system built on a layered architecture with three main components:

### Architecture Layer (`src/agent/architecture/`)

- **capability_map** - Maps capabilities to their implementations
- **dependency_graph** - Manages dependencies between components  
- **ownership** - Manages component ownership and responsibility
- **topology** - Defines network topology and structure

### Capabilities Layer (`src/agent/capabilities/`)

- **action, agency, cognition, creativity, evolution**
- **knowledge, learning, memory, motivation, perception, personality**

### Components Layer (`src/agent/components/`)

- **Core**: engine, executor, manager
- **Networks**: cognitive, communication, data

## Installation

```bash
cd gordon-system
pip install -e .
```

## Project Structure

```
gordon-system/
├── src/
│   └── agent/
│       ├── __init__.py      # Package initialization
│       ├── __meta__.py      # Metadata declarations  
│       ├── __tree__.py      # Structural tree definitions (shared Node class)
│       ├── architecture/    # Architecture layer packages
│       ├── capabilities/    # Capabilities layer packages
│       └── components/      # Components layer packages
├── docs/
│   └── index.md            # Documentation
├── pyproject.toml          # Build and configuration
└── README.md              # This file
```

## Development

### Running Tests

```bash
pytest
```

### Type Checking

```bash
mypy src/agent
```

### Code Formatting

```bash
black src/agent
isort src/agent
```

## Version

v0.0.1

## License

MIT