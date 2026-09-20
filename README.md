# VADER: Autonomous Agentic Development Platform (Vibe-Coder)

<div align="center">

```
██╗   ██╗ █████╗ ██████╗ ███████╗██████╗ 
██║   ██║██╔══██╗██╔══██╗██╔════╝██╔══██╗
██║   ██║███████║██║  ██║█████╗  ██████╔╝
╚██╗ ██╔╝██╔══██║██║  ██║██╔══╝  ██╔══██╗
 ╚████╔╝ ██║  ██║██████╔╝███████╗██║  ██║
  ╚═══╝  ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
```

**Turn intuitive developer intent into production-grade software.**  
*Terminal-first vibe-coding with native Ollama, quantized GGUF models, multi-agent orchestration, skills, and self-healing execution loops.*

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-orange.svg)](#)
[![Ollama](https://img.shields.io/badge/Ollama-Native-purple.svg)](https://ollama.com)
[![Quantization](https://img.shields.io/badge/Quantization-GGUF%20%2F%20Q4--Q8-yellow.svg)](#)

</div>

---

## 🚀 Quickstart

### 1. Installation

Install Vader globally via pip:

```bash
# Clone the repository
git clone https://github.com/shreytalreja25/VADER.git
cd VADER

# Install in editable/global mode
pip install -e .
```

Once installed, the `vader` command is globally available in your terminal on both **Windows** and **macOS/Linux**!

### 2. Configure Vader (`vader setup`)

Run the interactive setup wizard to configure your preferred LLM provider:

```bash
vader setup
```

The wizard guides you through:
1. **Ollama** (Default local streaming on `http://localhost:11434`, e.g., `qwen2.5-coder:7b`)
2. **Quantized GGUF / llama.cpp** (Plug-and-play local quantized models)
3. **Cloud Fallback** (DeepSeek, Claude 3.7 Sonnet, OpenAI)
4. Guardrails & protected path configuration

### 3. Start Vibe-Coding!

```bash
# Interactive REPL mode (Claude Code / OpenCode style)
vader

# Or execute a one-shot task directly
vader "Refactor the authentication middleware to use JWT with RS256 signatures and write tests"
```

---

## 🧠 Key Features

- **Autonomous Multi-Agent Orchestration**:
  - 📐 **Architect Agent**: Decomposes prompts into dependency-ordered execution graphs.
  - 💻 **Coder Agent**: Generates granular, multi-file code modifications.
  - 🛡️ **Reviewer Agent**: Enforces guardrails, catches secret leaks, and prevents API drift.
  - 🧪 **Tester & Self-Healing Loop**: Intercepts linter warnings and test failures to self-correct code in a sandboxed execution loop.
- **Local & Quantized Models First**:
  - Direct connection to **Ollama** (`qwen2.5-coder`, `deepseek-coder`, `llama3.2`).
  - Plug-and-play **GGUF quantization** (`Q4_K_M`, `Q8_0`) with minimal VRAM requirements.
- **Extensible Skills System**:
  - Install specialized domain skills from markdown instruction sets (`SKILL.md`).
  - Built-in skills for Clean Architecture, Test Generation, and Security Auditing.
- **Declarative Workflows**:
  - Multi-step YAML pipelines chaining agents, bash commands, and validations.
- **Cron Task Scheduler**:
  - Schedule background repo health audits, test sweeps, and automated updates.

---

## 💻 CLI Command Reference

| Command | Description |
|---|---|
| `vader` | Launch interactive terminal REPL |
| `vader "task description"` | Execute a single vibe-coding task |
| `vader setup` | Interactive model & provider configuration wizard |
| `vader doctor` | Diagnose environment, Ollama connectivity, & active models |
| `vader diff` | Display colored git diff of changes made by Vader |
| `vader skill list` | List all installed developer skills |
| `vader skill install <path>` | Install a new skill from a local folder |
| `vader workflow list` | List available YAML workflows |
| `vader workflow run <path>` | Execute an agentic workflow pipeline |
| `vader cron list` | View scheduled background cron jobs |
| `vader cron add --schedule "expr" <payload>` | Schedule an automated cron job |

---

## 🛠️ Extensibility: Skills & Workflows

### Creating a Custom Skill
Create a folder inside `.vader/skills/<skill-name>/` with a `SKILL.md` file:

```markdown
---
name: my-custom-skill
description: Custom pattern or framework rules
---

# Instructions for the agent
Enforce our team's coding conventions whenever writing API endpoints...
```

Install it with:
```bash
vader skill install .vader/skills/my-custom-skill
```

### Running Workflows
Define an automated pipeline in `workflows/audit.yaml`:

```yaml
name: repository-audit
steps:
  - id: scan
    name: Security Scan
    type: agent
    prompt: "Scan repo for secret leaks and unsafe imports"
  - id: tests
    name: Run Pytest
    type: command
    run: pytest -q
```

Run it with:
```bash
vader workflow run workflows/audit.yaml
```

---

## 🌐 Landing Page

Vader includes a modern React + Vite web dashboard and landing page located in `web/`:

```bash
cd web
npm install
npm run dev
```

---

## 📄 License & PRD

- For detailed product requirements, see [docs/PRD.md](docs/PRD.md).
- Licensed under the MIT License.
