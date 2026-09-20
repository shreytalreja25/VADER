import React, { useState } from 'react'

export default function App() {
  const [copied, setCopied] = useState(false)
  const [activeTab, setActiveTab] = useState('ollama')
  const [terminalStep, setTerminalStep] = useState(3)

  const copyCommand = (cmd) => {
    navigator.clipboard.writeText(cmd)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const installCmd = "pip install -e ."
  const runCmd = "vader setup"

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '24px 48px', borderBottom: '1px solid rgba(255,255,255,0.06)', backdropFilter: 'blur(10px)', position: 'sticky', top: 0, zIndex: 50, background: 'rgba(9,13,22,0.85)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'linear-gradient(135deg, #00f2fe, #4facfe)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '800', color: '#000', fontSize: '20px' }}>
            ⚡
          </div>
          <span style={{ fontSize: '22px', fontWeight: '800', letterSpacing: '-0.5px' }}>VADER</span>
          <span style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '1px', background: 'rgba(56,189,248,0.15)', color: '#38bdf8', padding: '2px 8px', borderRadius: '4px', fontWeight: '600' }}>v0.1.0</span>
        </div>

        <div style={{ display: 'flex', gap: '28px', fontSize: '14px', fontWeight: '500', color: 'var(--text-secondary)' }}>
          <a href="#features" style={{ color: 'inherit', textDecoration: 'none' }}>Features</a>
          <a href="#models" style={{ color: 'inherit', textDecoration: 'none' }}>Ollama & Quantization</a>
          <a href="#architecture" style={{ color: 'inherit', textDecoration: 'none' }}>Architecture</a>
          <a href="#skills" style={{ color: 'inherit', textDecoration: 'none' }}>Skills & Workflows</a>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <a href="https://github.com/shreytalreja25/VADER" target="_blank" rel="noreferrer" className="btn-secondary">
            GitHub Repo
          </a>
        </div>
      </nav>

      {/* Hero Section */}
      <header style={{ maxWidth: '1200px', margin: '60px auto 40px auto', padding: '0 24px', textAlign: 'center' }}>
        <div className="badge-glow" style={{ marginBottom: '24px' }}>
          ✨ The Autonomous Agentic Development Platform (Vibe-Coder)
        </div>

        <h1 style={{ fontSize: '64px', fontWeight: '800', letterSpacing: '-2px', lineHeight: 1.1, marginBottom: '24px' }}>
          Code at the Speed of Thought with <span className="text-gradient">Vader</span>
        </h1>

        <p style={{ fontSize: '20px', color: 'var(--text-secondary)', maxWidth: '780px', margin: '0 auto 40px auto', lineHeight: 1.6 }}>
          Turn high-level developer intent into verified production code. Native support for <strong>Ollama</strong>, <strong>Q4/Q8 quantized GGUF models</strong>, multi-file context harness, and sandboxed self-healing loops.
        </p>

        {/* Install box */}
        <div style={{ display: 'inline-flex', alignItems: 'center', background: 'rgba(15,23,42,0.9)', border: '1px solid rgba(56,189,248,0.3)', borderRadius: '12px', padding: '8px 12px 8px 20px', gap: '16px', boxShadow: '0 8px 30px rgba(0,0,0,0.5)', marginBottom: '32px' }}>
          <code style={{ fontSize: '15px', color: '#38bdf8' }}>
            <span style={{ color: '#94a3b8' }}>$ </span>git clone https://github.com/shreytalreja25/VADER.git &amp;&amp; pip install -e .
          </code>
          <button 
            onClick={() => copyCommand("git clone https://github.com/shreytalreja25/VADER.git && cd VADER && pip install -e .")} 
            className="btn-primary" 
            style={{ padding: '8px 18px', fontSize: '13px' }}
          >
            {copied ? "Copied! ✔" : "Copy Install"}
          </button>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px' }}>
          <a href="#terminal-demo" className="btn-primary">
            Explore Terminal Demo
          </a>
          <button onClick={() => copyCommand("vader setup")} className="btn-secondary">
            Run Setup: <code>vader setup</code>
          </button>
        </div>
      </header>

      {/* Interactive Terminal Demo */}
      <section id="terminal-demo" style={{ maxWidth: '1000px', margin: '60px auto', padding: '0 24px' }}>
        <div className="glass-panel" style={{ borderRadius: '16px', overflow: 'hidden', border: '1px solid rgba(56,189,248,0.25)' }}>
          {/* Terminal Window Header */}
          <div style={{ background: '#0b1120', padding: '12px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <div style={{ display: 'flex', gap: '8px' }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#ef4444' }}></div>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#f59e0b' }}></div>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#10b981' }}></div>
            </div>
            <div style={{ fontSize: '13px', color: 'var(--text-dim)', fontFamily: 'Fira Code' }}>
              vader — qwen2.5-coder:7b (Ollama Local • 0.2s latency)
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <span style={{ fontSize: '11px', background: 'rgba(16,185,129,0.15)', color: '#10b981', padding: '2px 8px', borderRadius: '4px' }}>OLLAMA CONNECTED</span>
            </div>
          </div>

          {/* Terminal Body */}
          <div style={{ padding: '28px', background: '#070b14', minHeight: '380px', fontFamily: 'Fira Code', fontSize: '14px', lineHeight: '1.7' }}>
            <div style={{ color: '#00f2fe', fontWeight: '700', marginBottom: '8px' }}>
              ██╗   ██╗ █████╗ ██████╗ ███████╗██████╗<br/>
              ██║   ██║██╔══██╗██╔══██╗██╔════╝██╔══██╗<br/>
              ██║   ██║███████║██║  ██║█████╗  ██████╔╝<br/>
              ╚██╗ ██╔╝██╔══██║██║  ██║██╔══╝  ██╔══██╗<br/>
               ╚████╔╝ ██║  ██║██████╔╝███████╗██║  ██║<br/>
                ╚═══╝  ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
            </div>
            <div style={{ color: '#64748b', marginBottom: '16px' }}>
              Vader v0.1.0 | Mode: Multi-Agent Orchestration | Guardrails: ACTIVE
            </div>

            <div style={{ color: '#e2e8f0', marginBottom: '16px' }}>
              <span style={{ color: '#38bdf8', fontWeight: 'bold' }}>vader &gt; </span>
              "Refactor payments module to support Stripe webhook idempotency and self-heal failing unit tests"
            </div>

            {/* Agent Phase Pipeline */}
            <div style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', padding: '16px', marginBottom: '16px' }}>
              <div style={{ color: '#38bdf8', marginBottom: '8px' }}>
                ▶ [Context Harness] Indexed 42 files (Symbol graph + AST extracted)
              </div>
              <div style={{ color: '#60a5fa', marginBottom: '8px' }}>
                📐 [Architect Agent] Dependency graph generated: 3 files (idempotency.py, handler.py, test_payments.py)
              </div>
              <div style={{ color: '#34d399', marginBottom: '8px' }}>
                💻 [Coder Agent] Generated atomic patch with cryptographic replay detection
              </div>
              <div style={{ color: '#fbbf24', marginBottom: '8px' }}>
                ⚡ [Self-Healing Sandbox] Linter detected missing imports in test_payments.py. Intercepting and auto-repairing...
              </div>
              <div style={{ color: '#4ade80', fontWeight: 'bold' }}>
                ✔ [Tester Agent] All 14 tests passing. Reviewer verified zero credential leaks.
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#10b981' }}>
              <span>✔ Task complete in 1.42s (zero cloud telemetry, 100% local Ollama inference)</span>
            </div>
          </div>
        </div>
      </section>

      {/* Model & Quantization Matrix */}
      <section id="models" style={{ maxWidth: '1100px', margin: '80px auto', padding: '0 24px' }}>
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h2 style={{ fontSize: '36px', fontWeight: '800', marginBottom: '12px' }}>
            Local-First: Ollama &amp; Quantized GGUF Weights
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '18px' }}>
            Run state-of-the-art coding models on your laptop without sending code to cloud servers.
          </p>
        </div>

        {/* Tab selector */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '12px', marginBottom: '32px' }}>
          <button 
            onClick={() => setActiveTab('ollama')} 
            className={activeTab === 'ollama' ? 'btn-primary' : 'btn-secondary'}
          >
            Ollama Native
          </button>
          <button 
            onClick={() => setActiveTab('quantized')} 
            className={activeTab === 'quantized' ? 'btn-primary' : 'btn-secondary'}
          >
            Quantized GGUF (llama.cpp)
          </button>
          <button 
            onClick={() => setActiveTab('cloud')} 
            className={activeTab === 'cloud' ? 'btn-primary' : 'btn-secondary'}
          >
            Frontier Cloud Fallback
          </button>
        </div>

        {/* Tab Content */}
        <div className="glass-panel" style={{ padding: '32px' }}>
          {activeTab === 'ollama' && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '20px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ fontSize: '18px', fontWeight: '700', color: '#38bdf8', marginBottom: '8px' }}>Qwen 2.5 Coder 7B</div>
                <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '12px' }}>Recommended for most developers. Incredible vibe-coding speed and multi-file logic.</div>
                <div style={{ fontSize: '12px', fontFamily: 'Fira Code', background: '#090d16', padding: '8px', borderRadius: '6px', color: '#10b981' }}>ollama run qwen2.5-coder:7b</div>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '20px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ fontSize: '18px', fontWeight: '700', color: '#a855f7', marginBottom: '8px' }}>DeepSeek-Coder V2 6.7B</div>
                <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '12px' }}>Specialized code completion and complex algorithmic reasoning.</div>
                <div style={{ fontSize: '12px', fontFamily: 'Fira Code', background: '#090d16', padding: '8px', borderRadius: '6px', color: '#10b981' }}>ollama run deepseek-coder:6.7b</div>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '20px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ fontSize: '18px', fontWeight: '700', color: '#10b981', marginBottom: '8px' }}>Llama 3.2 3B</div>
                <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '12px' }}>Ultra-lightweight. Runs smoothly on 8GB RAM laptops with zero battery drain.</div>
                <div style={{ fontSize: '12px', fontFamily: 'Fira Code', background: '#090d16', padding: '8px', borderRadius: '6px', color: '#10b981' }}>ollama run llama3.2:3b</div>
              </div>
            </div>
          )}

          {activeTab === 'quantized' && (
            <div>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>
                Drop any <code>.gguf</code> file into <code>~/.vader/models/</code>. Vader auto-detects quantization levels and manages VRAM budgets seamlessly:
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
                <div style={{ background: 'rgba(255,255,255,0.02)', padding: '20px', borderRadius: '12px' }}>
                  <span style={{ background: 'rgba(56,189,248,0.15)', color: '#38bdf8', padding: '3px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold' }}>Q4_K_M PRESET</span>
                  <h4 style={{ margin: '12px 0 6px 0', fontSize: '16px' }}>4-Bit Quantization</h4>
                  <p style={{ fontSize: '13px', color: '#94a3b8' }}>~4.5 GB VRAM requirement. 98% quality retention of full FP16 weights.</p>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.02)', padding: '20px', borderRadius: '12px' }}>
                  <span style={{ background: 'rgba(168,85,247,0.15)', color: '#a855f7', padding: '3px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold' }}>Q8_0 PRESET</span>
                  <h4 style={{ margin: '12px 0 6px 0', fontSize: '16px' }}>8-Bit Quantization</h4>
                  <p style={{ fontSize: '13px', color: '#94a3b8' }}>Near lossless precision for enterprise codebases requiring strict type safety.</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'cloud' && (
            <div>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>
                Optional hybrid execution: switch to Claude 3.7 Sonnet, DeepSeek V2, or OpenAI GPT-4o for mega-repo migrations.
              </p>
              <div style={{ fontFamily: 'Fira Code', fontSize: '13px', background: '#090d16', padding: '16px', borderRadius: '8px', color: '#38bdf8' }}>
                $ vader setup --provider cloud<br/>
                $ export ANTHROPIC_API_KEY=your_key_here
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Key Pillars */}
      <section id="features" style={{ maxWidth: '1100px', margin: '80px auto', padding: '0 24px' }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <h2 style={{ fontSize: '36px', fontWeight: '800', marginBottom: '12px' }}>
            Engineered for Autonomous Vibe-Coding
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '18px' }}>
            Built to overcome localized context blindness, manual glue work, and context drift.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
          <div className="glass-panel" style={{ padding: '28px' }}>
            <div style={{ fontSize: '28px', marginBottom: '12px' }}>📐</div>
            <h3 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '8px' }}>Autonomous Task Planning</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              Deconstructs prompts into dependency-ordered execution graphs handled by specialized sub-agents: Architect, Coder, Reviewer, and Tester.
            </p>
          </div>

          <div className="glass-panel" style={{ padding: '28px' }}>
            <div style={{ fontSize: '28px', marginBottom: '12px' }}>⚡</div>
            <h3 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '8px' }}>Self-Healing Sandbox Loop</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              Intercepts linter warnings, syntax bugs, and test failures in a sandboxed local environment to self-correct before user handoff.
            </p>
          </div>

          <div className="glass-panel" style={{ padding: '28px' }}>
            <div style={{ fontSize: '28px', marginBottom: '12px' }}>🌐</div>
            <h3 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '8px' }}>Multi-File Context Harness</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              Maintains a repository symbol graph, AST definitions, and Git history snapshots for pinpoint accuracy across modular boundaries.
            </p>
          </div>

          <div className="glass-panel" style={{ padding: '28px' }}>
            <div style={{ fontSize: '28px', marginBottom: '12px' }}>🧩</div>
            <h3 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '8px' }}>Custom Skills System</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              Install specialized domain skills (Clean Architecture, Test Generation, Security Auditing) to enforce your team's exact standards.
            </p>
          </div>

          <div className="glass-panel" style={{ padding: '28px' }}>
            <div style={{ fontSize: '28px', marginBottom: '12px' }}>⏱️</div>
            <h3 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '8px' }}>Scheduled Cron Tasks</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              Run automated background repository audits, security checks, and nightly self-healing sweeps with standard cron expressions.
            </p>
          </div>

          <div className="glass-panel" style={{ padding: '28px' }}>
            <div style={{ fontSize: '28px', marginBottom: '12px' }}>🛡️</div>
            <h3 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '8px' }}>Git-Native Safety &amp; Guardrails</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              Protected paths prevent mutations to credentials or git history. Immediate one-command rollback to clean state if desired.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid rgba(255,255,255,0.06)', padding: '48px 24px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '14px' }}>
        <div style={{ marginBottom: '16px' }}>
          <span style={{ fontWeight: '700', color: 'var(--text-primary)' }}>VADER (Vibe-Coder)</span> — Autonomous Agentic Development Platform
        </div>
        <div>
          Licensed under MIT. Open Source on <a href="https://github.com/shreytalreja25/VADER" style={{ color: '#38bdf8' }}>GitHub</a>.
        </div>
      </footer>
    </div>
  )
}
