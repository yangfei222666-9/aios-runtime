<p align="center">
  <h1 align="center">AIOS — AI Agent Operating System</h1>
  <p align="center">An observable, self-healing runtime for autonomous AI agents.</p>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/AI-Agents-brightgreen.svg" alt="AI Agents">
  <img src="https://img.shields.io/badge/Evolution%20Score-99.5-orange.svg" alt="Evolution Score">
</p>

<p align="center">
  AIOS provides task routing, adversarial debate validation, failure recovery, and system telemetry — making AI agents reliable in production.
</p>

---

## Demo

```bash
$ python run_aios.py "analyze dataset"

┌──────────────────────────────────────────┐
│  AIOS — AI Agent Operating System v3.4   │
│  Observable · Self-Healing · Autonomous   │
└──────────────────────────────────────────┘

──────────────────────────────────────────────────
Task: "analyze dataset"
──────────────────────────────────────────────────
  Router:     Fast (Quick Execution)
  Debate:     No
  Hexagram:   坤 (Stable, 92% confidence)
  Evolution:  94.9/100
  Result:     ✓ Success
```

---

## Why AIOS?

Most AI agent frameworks focus on **task execution**. But they lack **runtime observability** and **self-healing** capabilities.

AIOS focuses on the **runtime layer**:

- **Observability** — Know what your agents are doing, in real time
- **Self-Healing** — Failed tasks automatically recover through bootstrapped regeneration
- **Policy-Driven Decisions** — I Ching hexagram state engine guides system behavior
- **Evolution Monitoring** — Track how your agent system improves over time

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Task Router** | Automatically routes tasks to Fast or Slow models based on complexity |
| **Hexagram State Engine** | 64 I Ching hexagrams as a state machine for system-level decision making |
| **Evolution Score** | Real-time health metric (0–100) tracking system maturity |
| **Self-Healing Agents** | LowSuccess Agent + LanceDB experience library for failure recovery |
| **Adversarial Validation** | Bull vs Bear debate system for high-risk decisions |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  AIOS v3.4                      │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌───────────┐  ┌───────────┐  ┌────────────┐  │
│  │ Task Queue │  │  Router   │  │  Executor  │  │
│  └─────┬─────┘  └─────┬─────┘  └─────┬──────┘  │
│        │              │              │          │
│        └──────────────┼──────────────┘          │
│                       │                         │
│              ┌────────▼────────┐                │
│              │  Policy Layer   │                │
│              │  (64 Hexagrams) │                │
│              └────────┬────────┘                │
│                       │                         │
│        ┌──────────────┼──────────────┐          │
│        │              │              │          │
│  ┌─────▼─────┐  ┌─────▼─────┐  ┌────▼───────┐  │
│  │ Evolution  │  │ Self-Heal │  │ Adversarial│  │
│  │  Score     │  │  Agent    │  │ Validation │  │
│  └───────────┘  └───────────┘  └────────────┘  │
│                       │                         │
│              ┌────────▼────────┐                │
│              │   Dashboard     │                │
│              │ localhost:8888  │                │
│              └─────────────────┘                │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Quick Start

```bash
git clone https://github.com/yangfei222666-9/AIOS.git
cd AIOS
pip install -r requirements.txt
python run_aios.py
```

Open the dashboard:

```bash
python dashboard/AIOS-Dashboard-v3.4/server.py
# Visit http://127.0.0.1:8888
```

Submit a task:

```python
from core.task_submitter import submit_task

submit_task("analyze error logs", task_type="analysis", priority="high")
```

---

## How It Works

### 1. Task Routing

Every task goes through the **Router**, which decides:
- **Fast Model** — Simple tasks (analysis, monitoring, classification)
- **Slow Model** — Complex tasks (refactoring, architecture design, planning)

### 2. Hexagram State Engine

The system state is represented as one of **64 I Ching hexagrams**:

```
坤 (Stable)  → Normal operations, execute freely
乾 (Creative) → High performance, push boundaries
屯 (Difficult) → Problems detected, proceed carefully
大过 (Crisis)  → Critical failure, activate emergency protocols
```

The hexagram drives policy decisions: retry limits, debate thresholds, resource allocation.

### 3. Evolution Score

A real-time health metric combining:
- Task success rate (40%)
- Auto-correction rate (30%)
- System uptime (20%)
- Learning speed (10%)

### 4. Self-Healing

When tasks fail, the **LowSuccess Agent** kicks in:

```
Failure detected → Pattern analysis → Generate fix strategy
    → Bootstrapped regeneration → Retry → Save to experience library
```

Success strategies are stored in **LanceDB** for future reference.

### 5. Adversarial Validation

High-risk decisions trigger a **Bull vs Bear debate**:
- **Bull Agent** argues in favor
- **Bear Agent** challenges with risks
- **Judge** synthesizes a final decision (requires >80% confidence)

---

## Project Structure

```
AIOS/
├── run_aios.py              # Entry point & demo
├── requirements.txt
├── LICENSE
│
├── core/                    # Core runtime
│   ├── task_submitter.py    # Task submission API
│   ├── task_executor.py     # Task execution engine
│   ├── model_router.py      # Smart model routing
│   ├── orchestrator.py      # Task orchestration
│   └── evolution.py         # Evolution tracking
│
├── policy/                  # Policy layer
│   ├── iching_engine.py     # I Ching hexagram engine
│   ├── hexagram_detector.py # Hexagram detection
│   └── trigram_detector.py  # Trigram analysis
│
├── agent_system/            # Agent management
│   ├── heartbeat_v5.py      # Heartbeat monitor
│   ├── evolution_fusion.py  # Score fusion
│   ├── task_router.py       # Task routing
│   └── agents.json          # Agent registry
│
├── dashboard/               # Web dashboard
│   └── AIOS-Dashboard-v3.4/ # Dashboard v3.4
│
├── scripts/                 # Utility scripts
├── docs/                    # Documentation
└── tests/                   # Test suite
```

---

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — System design and component overview
- [Changelog](CHANGELOG.md) — Version history
- [Contributing](CONTRIBUTING.md) — How to contribute

---

## Roadmap

- [x] Task Queue System with Heartbeat v5.0
- [x] 64 Hexagram State Engine
- [x] Evolution Score with confidence fusion
- [x] LowSuccess Agent + LanceDB experience library
- [x] Adversarial Validation (Bull vs Bear)
- [x] Web Dashboard v3.4
- [ ] Multi-model support (OpenAI / Gemini / Ollama)
- [ ] Distributed scheduling
- [ ] Agent Marketplace (remote)
- [ ] Mobile dashboard

---

## License

[MIT](LICENSE) — Use it, fork it, build on it.

---

## Contact

- GitHub: [@yangfei222666-9](https://github.com/yangfei222666-9)
- Telegram: [@shh7799](https://t.me/shh7799)

---

<p align="center">
  <b>AIOS v3.4</b> — Observable · Self-Healing · Autonomous
  <br>
  <sub>Built with ❤️ by 小九 + 珊瑚海</sub>
</p>
