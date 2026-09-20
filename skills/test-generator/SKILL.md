---
name: test-generator
description: Generates comprehensive unit, edge-case, and mock integration tests
version: 1.0.0
tags: [testing, pytest, jest, vitest]
---

# Test Generator Skill

When this skill is activated:
1. Detect repository test frameworks (pytest, unittest, vitest, jest).
2. For each target module, analyze public functions, arguments, return types, and potential exceptions.
3. Generate tests covering:
   - Happy path behaviors.
   - Boundary & edge cases (empty collections, invalid inputs, timeouts).
   - Mocking of external services and network I/O.
4. Verify tests pass in the sandboxed execution environment.
