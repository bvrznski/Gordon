# Gordon Subdomains

## Overview

Gordon's subdomains define the functional areas of the system. Each subdomain is associated with specific capabilities and components.

## Subdomain Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Gordon Subdomains                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────┬────────────┬────────────┬─────────┐      │
│  │ Architecture│ Capabilities│ Components│ Systems │     │
│  │   Layer    │   Layer    │   Layer   │ Layer   │      │
│  └────────────┴────────────┴────────────┴─────────┘      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Subdomain Details

### Architecture Subdomain

| Property | Value |
|----------|-------|
| Name | architecture |
| Layer | 0 (Architecture) |
| Owner | Architecture Team |
| Purpose | Structural definitions for the entire system |

**Components:**
- capability_map - Maps capabilities to implementations
- dependency_graph - Manages component dependencies
- ownership - Defines ownership boundaries
- topology - Network structure definitions

### Capabilities Subdomain

| Property | Value |
|----------|-------|
| Name | capabilities |
| Layer | 1 (Capabilities) |
| Owner | Capabilities Team |
| Purpose | Intelligent behaviors and actions |

**Components:**
- action, agency, cognition, creativity, evolution, knowledge, learning, motivation, personality

### Components Subdomain

| Property | Value |
|----------|-------|
| Name | components |
| Layer | 2 (Components) |
| Owner | Components Team |
| Purpose | Building blocks and infrastructure |

**Components:**
- core/engine, core/executor, core/manager

### Systems Subdomain

| Property | Value |
|----------|-------|
| Name | systems |
| Layer | 3 (Systems) |
| Owner | Systems Team |
| Purpose | System-level infrastructure |

**Components:**
- memory, perception

## Subdomain Boundaries

```
Architecture → Capabilities
Architecture → Components
Architecture → Systems

Capabilities → Components
Capabilities → Architecture (for definitions only)

Components → Systems
Components → Architecture (for definitions only)
```

## Subdomain Invariants

1. Each subdomain has a single, clear purpose
2. Subdomains are independent of each other
3. Dependencies flow downward through the layer hierarchy
4. No runtime code in architecture subdomain