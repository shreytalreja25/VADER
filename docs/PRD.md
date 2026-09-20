# Product Requirement Document (PRD): Vader (Vibe-Coder)

## 1. Product Overview
**Vader** (portmanteau of *Vibe-Coder*) is an autonomous agentic development platform designed to turn intuitive developer intent into production-grade software. Vader bridges high-level architectural direction and low-level code execution by unifying an agent orchestration engine, a lightweight developer interface, and a persistent repository context harness.

Vader operates both as a command-line developer copilot (similar to Claude Code and OpenCode) and as an extensible orchestration platform with first-class support for local open-source models via Ollama and quantized weights (GGUF / llama.cpp / vLLM).

---

## 2. Vision & Problem Statement

### Vision
Enable developers to build at the speed of thought by pairing them with an autonomous agentic system that understands full-repo architecture, plans complex refactors, and delivers verified, tested code with zero manual glue work.

### Problem Statement
1. **Localized Context Blindness**: Existing code-assistant tools generally operate on active buffers or small snippet contexts, failing to anticipate cross-module side effects.
2. **Manual Glue Work**: Engineers spend excessive time coordinating multi-file changes, setting up boilerplate, running manual lint checks, and fixing broken imports.
3. **Context Drift**: Agentic tools frequently lose track of dependency graphs, API boundaries, and domain conventions across extended interactions.
4. **Cloud-Lockin & Privacy Concerns**: Enterprise and private developers cannot always send sensitive internal source code to third-party hosted cloud APIs.

---

## 3. Target Audience
- **Full-Stack Engineers & Builders**: Developers looking to offload boilerplate, multi-file feature additions, and repetitive integration logic.
- **Tech Leads & Core Maintainers**: Teams needing reliable, verified multi-file migrations and structural code modifications.
- **Rapid-Iteration Startups**: Small teams aiming for enterprise-grade execution speed without accruing architectural debt.
- **Privacy & Local-First Engineers**: Developers running local models (e.g. Qwen 2.5 Coder, DeepSeek-Coder, Llama 3) via Ollama or quantized weights on consumer GPUs.

---

## 4. Key Components & Architecture

```
                                  ┌────────────────────────┐
                                  │      Vader CLI         │
                                  │   (Terminal REPL)      │
                                  └───────────┬────────────┘
                                              │
                      ┌───────────────────────┴────────────────────────┐
                      ▼                                                ▼
       ┌─────────────────────────────┐                  ┌─────────────────────────────┐
       │   Agent Orchestration       │                  │  Repository Context Harness │
       │  • Architect Agent          │                  │  • Symbol & AST Indexer     │
       │  • Coder Agent              │◄─────────────────┤  • Git Diff / History Snap  │
       │  • Reviewer Agent           │                  │  • Token Budget Manager     │
       │  • Tester / Self-Heal       │                  └─────────────────────────────┘
       └──────────────┬──────────────┘
                      │
       ┌──────────────┴──────────────────────────────┐
       ▼                                             ▼
┌─────────────────────────────┐       ┌─────────────────────────────┐
│  Ollama & Local Model Engine│       │   Extensibility Engine      │
│  • Ollama Streaming API     │       │   • Custom Skills System    │
│  • GGUF Quantized Runners   │       │   • Declarative Workflows   │
│  • Q4 / Q8 Quantization     │       │   • Scheduled Cron Jobs     │
└─────────────────────────────┘       └─────────────────────────────┘
```

### 4.1 Vader Engine (Agent Orchestration Framework)
- **Autonomous Task Planning**: Deconstructs prompts into dependency-ordered execution graphs handled by specialized sub-agents:
  - **Architect**: High-level task decomposition and dependency mapping.
  - **Coder**: Multi-file code generation and structured patch formatting.
  - **Reviewer**: Guardrail enforcement, credential leak prevention, and interface safety.
  - **Tester**: Error traceback analysis and targeted fix diagnosis.
- **Multi-File Context Harness**: Generates and maintains a repository symbol graph, AST metadata, and Git history snapshots for accurate context retrieval.
- **Self-Healing Execution Loop**: Intercepts linter warnings, syntax errors, and test failures in a sandboxed local environment to self-correct before user handoff.

### 4.2 Local Model & Quantization Support
- **Ollama Native Provider**: Zero-config auto-discovery on `http://localhost:11434`, streaming completions, and model pulling (`qwen2.5-coder:7b`, `deepseek-coder:6.7b`, `llama3.2:3b`).
- **Plug-and-Play Quantized Weights**:
  - Direct compatibility with GGUF files and local OpenAI-compatible inference servers (`llama.cpp`, `vLLM`).
  - Support for 4-bit and 8-bit quantized weights (`Q4_K_M`, `Q5_K_M`, `Q8_0`), reducing VRAM requirements to allow local execution on laptops with 8GB-16GB RAM.
- **Cloud Fallback**: Optional hybrid provider for Claude 3.7 Sonnet, DeepSeek V2, and OpenAI GPT-4o.

### 4.3 Extensibility: Skills, Workflows, & Cron
- **Skills System**: Loadable domain instructions (`SKILL.md`) providing specialized heuristics (e.g. Clean Architecture, Test Generation, Security Auditing).
- **Workflows**: Multi-step agentic pipelines defined in YAML for CI/CD, migration passes, and automated documentation.
- **Cron Scheduler**: Background execution engine running periodic repository scans, automated dependency audits, and nightly self-healing test passes.

### 4.4 Workflow & Tooling Integration
- **Git-Native Lifecycle**: Automated local branch isolation, scoped commits with descriptive summaries, and pre-packaged PR generation.
- **Custom Guardrails**: User-defined rules prohibiting file mutations on protected paths (`.git`, `.env`, `node_modules`).
- **Interactive Configuration Wizard (`vader setup`)**: One-command guided setup for model providers, endpoints, and guardrails.

---

## 5. Non-Functional Requirements
- **Cross-Platform**: Operates identically on Windows, macOS, and Linux.
- **Latency**: Initial planning state returned within 1.5 seconds on local Ollama; local repo indexing runs non-blocking.
- **Data Security & Privacy**: Zero remote telemetry; all parsing, indexing, and model inferences remain on the local machine when using Ollama or quantized backends.
- **Determinism & Safe Revert**: Immediate one-command restoration (`git reset` / `vader diff`) to the last clean Git commit if an agent plan fails mid-execution.

---

## 6. Success Metrics & KPIs
- **Turnaround Speed**: 40%+ reduction in end-to-end task completion time for multi-file edits and feature scaffolds.
- **Acceptance Rate**: 70%+ of Vader-suggested patches merged without manual rework.
- **First-Pass Test Integrity**: 90%+ of generated code changes pass target unit tests on first automated validation.
- **Local Model Efficacy**: Full functional autonomy achievable using 7B-parameter Q4 quantized local models.
