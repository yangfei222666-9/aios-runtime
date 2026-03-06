# AIOS Runtime Control Architecture

> An autonomous AI operating system with closed-loop control, adversarial validation, and symbolic policy engine.

---

## 图1: AIOS Runtime Control Architecture（四层架构）

```mermaid
graph TB
    subgraph USER["🧑 User / Workload Layer"]
        CLI["CLI / API"]
        TG["Task Generator"]
        SCHED["Scheduler"]
        HB["Heartbeat"]
    end

    subgraph CONTROL["🧠 Control Plane"]
        direction TB
        ROUTER["Router<br/><i>Fast/Slow Model Selection</i>"]
        ADV["Adversarial Debate<br/><i>Bull vs Bear Validation</i>"]
        HEX["Hexagram Policy Engine<br/><i>64卦 Symbolic Strategy</i>"]
        EVO["Evolution Score<br/><i>Confidence Fusion</i>"]
        OBS["Observer / Telemetry<br/><i>Metrics · Entropy · Timeline</i>"]
        FTAX["Failure Taxonomy<br/><i>Root Cause Classification</i>"]
        HEAL["Self-Healing<br/><i>LowSuccess Regeneration</i>"]
    end

    subgraph DATA["⚙️ Data Plane"]
        direction TB
        QUEUE["Task Queue<br/><i>Priority Dispatch</i>"]
        POOL["Agent Pool (45+)<br/><i>coder · analyst · monitor · learning</i>"]
        EXEC["Executors<br/><i>sessions_spawn · local</i>"]
        DISP["Dispatchers<br/><i>coder · analyst · monitor</i>"]
    end

    subgraph RESOURCE["🔧 Tool & Resource Layer"]
        LLM["LLM APIs<br/><i>Claude · GPT · Ollama</i>"]
        TOOLS["Python Tools<br/><i>Code · Analysis · Search</i>"]
        FS["Filesystem<br/><i>Events · Logs · Memory</i>"]
        EXT["External APIs<br/><i>GitHub · Web · Telegram</i>"]
        LANCE["LanceDB<br/><i>Experience Vectors</i>"]
    end

    %% User → Control
    CLI --> ROUTER
    TG --> QUEUE
    SCHED --> QUEUE
    HB --> OBS

    %% Control internal flow
    ROUTER --> ADV
    ADV --> HEX
    HEX --> ROUTER
    OBS --> EVO
    EVO --> HEX
    FTAX --> HEAL
    OBS --> FTAX

    %% Control → Data
    ROUTER --> QUEUE
    QUEUE --> DISP
    DISP --> POOL
    POOL --> EXEC

    %% Data → Resource
    EXEC --> LLM
    EXEC --> TOOLS
    EXEC --> FS
    EXEC --> EXT
    HEAL --> LANCE

    %% Feedback loops (Data → Control)
    EXEC -.->|results| OBS
    POOL -.->|agent state| OBS
    HEAL -.->|regenerated tasks| QUEUE

    %% Styling
    style USER fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style CONTROL fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style DATA fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style RESOURCE fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px

    style ADV fill:#ffcdd2,stroke:#c62828,stroke-width:2px
    style HEX fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style HEAL fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
```

---

## 图2: AIOS Runtime Control Loop（闭环控制）

```mermaid
flowchart TD
    A["📋 Workload<br/><i>User Tasks / Generated Tasks</i>"]
    B["📦 Task Queue<br/><i>Priority Scheduling</i>"]
    C["🔀 Router<br/><i>Fast Model (Sonnet) / Slow Model (Opus)</i>"]
    D["🤖 Agent Selection<br/><i>45+ Specialized Agents</i>"]
    E{"⚔️ High Risk?"}
    F["🐂🐻 Adversarial Debate<br/><i>Bull vs Bear Validation</i>"]
    G["☯️ 64 Hexagram Mediation<br/><i>Symbolic Policy Adjustment</i>"]
    H["⚡ Execution<br/><i>sessions_spawn / Local</i>"]
    I["📊 Observer<br/><i>Metrics · State · Timeline</i>"]
    J["🔬 Failure Taxonomy<br/><i>code_exception · api_failure<br/>bad_plan · timeout</i>"]
    K["📈 Evolution Score<br/><i>Confidence Fusion (99.5%)</i>"]
    L["🔄 Policy Adjustment<br/><i>Threshold · Strategy · Model</i>"]
    M{"❌ Failed?"}
    N["🔁 Self-Healing<br/><i>Bootstrapped Regeneration<br/>LanceDB Experience Retrieval</i>"]

    A --> B
    B --> C
    C --> D
    D --> E
    E -->|Yes| F
    E -->|No| H
    F --> G
    G --> H
    H --> I
    I --> J
    I --> K
    J --> M
    K --> L
    L -->|"tune"| C
    M -->|Yes| N
    M -->|No| K
    N -->|"retry"| B

    style A fill:#e8f5e9,stroke:#2e7d32
    style F fill:#ffcdd2,stroke:#c62828,stroke-width:2px
    style G fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style N fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style K fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style L fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px
```

---

## 核心创新点

### 1. Adversarial Validation（对抗验证）
Bull vs Bear 辩论机制，高风险任务自动触发双方论证，64卦调解融合最终方案。在 agent runtime 中极为少见。

### 2. Hexagram Policy Engine（卦象策略引擎）
```
metrics → trigram → hexagram → strategy
```
基于64卦的符号化策略引擎，将系统状态映射为卦象，自动匹配对应策略。不是玄学，是 symbolic policy representation。

### 3. Self-Healing via Bootstrapped Regeneration（自愈重生）
灵感来自 sirius (NeurIPS 2025)：
```
failure → feedback → regenerate → retry → experience library
```
失败轨迹不丢弃，通过 LanceDB 向量检索历史成功策略，自动重生。

### 4. Closed-Loop Telemetry（闭环遥测）
完整的可观测性层：
- Metrics（成功率、延迟、资源）
- Entropy（系统混乱度）
- Timeline（状态转换序列）
- Failure Taxonomy（根因分类）
- Evolution Score（置信度融合）

---

## 类比

| 概念 | AIOS | 类比系统 |
|------|------|----------|
| Control Plane | Router + Hexagram + Evolution | K8s API Server + Scheduler |
| Data Plane | Agent Pool + Executors | K8s Kubelet + Pods |
| Policy Engine | 64 Hexagram | K8s Admission Controllers |
| Self-Healing | LowSuccess Regeneration | K8s Self-Healing + HPA |
| Observability | Observer + Telemetry | Prometheus + Grafana |
| Adversarial Validation | Bull vs Bear Debate | Chaos Engineering |

---

## 系统指标（当前）

- **Agent Pool**: 45+ specialized agents
- **Evolution Score**: 99.5/100
- **Task Success Rate**: 80.4% → 85%+ (target)
- **Confidence Fusion**: base × 0.65 + evolution × 0.35 + bonuses
- **Self-Healing Rate**: 75% auto-regeneration
- **Hexagram**: 坤卦 (stability phase)

---

*Generated: 2026-03-05 | AIOS v3.4*
