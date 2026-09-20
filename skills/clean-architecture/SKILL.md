---
name: clean-architecture
description: Refactors procedural code into modular Clean Architecture layers (Entities, Use Cases, Interfaces, Adapters)
version: 1.0.0
tags: [refactoring, design-patterns, clean-code]
---

# Clean Architecture Refactoring Skill

When this skill is activated:
1. Inspect the codebase for tight coupling between domain logic and database/framework drivers.
2. Isolate domain entities and business rules from frameworks (Express, FastAPI, Django, React).
3. Introduce Dependency Inversion: higher-level modules define interfaces that infrastructure layers implement.
4. Ensure all business use cases have corresponding deterministic unit tests with zero network dependencies.
