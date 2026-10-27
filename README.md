# VectoraFix: Autonomous Multi-Agent Incident Remediation Platform

> **Enterprise Multi-Agent AI System for Autonomous Incident Diagnosis, Sandboxed Code Repair, Verification, and Push-to-Deploy Delivery.**

---

## Executive Summary

**VectoraFix** is an enterprise-grade agentic platform engineered to autonomously diagnose, repair, verify, and remediate software failures across production and staging environments. The system derives its name from its foundational engineering mission: resolving both the **magnitude** (severity, scope, affected modules) and the **direction** (root-cause identification, minimal corrective patch, structural alignment) of software defects.

Built on a hybrid architecture of **multi-agent LLM reasoning** and **deterministic safety boundaries**, VectoraFix coordinates specialized engineering personas (implemented with LangGraph and LangChain, powered by Google Gemini) inside isolated Docker runtime sandboxes.

Rather than permitting unconstrained model execution, VectoraFix enforces strict human-in-the-loop gateways, immutable repository snapshots, full-diff scope verification, and fail-closed quality gates before pushing verified code to GitHub and updating live production deployments.

---

## Core Engineering Philosophy

```
+---------------------------------------------------------------------------------+
|                       VECTORAFIX CORE OPERATING PRINCIPLE                       |
|                                                                                 |
|  "Agentic reasoning is autonomous, but runtime execution and verification       |
|   are strictly deterministic."                                                  |
+---------------------------------------------------------------------------------+
```

Large Language Models (LLMs) excel at diagnostic deduction, cross-domain debate, and patch proposal. However, enterprise reliability mandates that code compilation, test execution, dependency isolation, and deployment synchronization remain governed by immutable, deterministic software boundaries:

1. **Untrusted Code and Input Isolation**: User logs, stack traces, and repository source code are treated strictly as untrusted data. Secrets and credentials are automatically scrubbed before persistence and model prompt injection.
2. **Container Sandboxing**: Code repairs, dependency installations, and test executions occur inside disposable, non-root Docker containers with read-only root filesystems and strict resource limits.
3. **Multi-Agent Consensus with Independent Code Review**: No single LLM prompt directly applies changes. A coordinator selects specialized domain engineers, forces iterative plan reviews, and mandates an independent code reviewer audit before any code modification is accepted.
4. **Human-in-the-Loop (HITL) Gateways**: Incident diagnosis generates a structured, human-readable repair plan. Source modification is strictly gated behind an explicit operator approval ("Start Repair").
5. **Continuous Deployment Synchronization**: Successful repairs are pushed directly to the repository branch (e.g., `main`), automatically triggering configured production build pipelines (such as Vercel, Render, or Railway).
6. **Fault-Tolerant Push Recovery**: If GitHub permissions, API rate limits, or network errors interrupt an automated push, the fully reviewed patch and workspace delta are preserved in an artifact vault. Operators can resolve permissions and trigger a direct push using the "Push Saved Repair" manual button without re-running model inference.

---

## System Architecture

The following diagram illustrates the four decoupled architectural tiers of VectoraFix: the Developer Operations Console, the FastAPI Control Plane, the LangGraph Multi-Agent Engine, and the Isolated Docker Sandbox.

```mermaid
flowchart TB
    subgraph FrontendTier ["Developer Operations Console (Next.js 16)"]
        UI_Incident["Incident Dashboard & Evidence Ingestion"]
        UI_Terminal["Real-time Container Terminal Stream"]
        UI_Diff["Side-by-Side Unified Diff Viewer"]
        UI_StartRepair["Start Repair (Human-in-the-Loop Approval Gate)"]
        UI_ManualPush["Push Saved Repair (Zero-Token Recovery Fallback)"]
    end

    subgraph ControlPlane ["FastAPI Control Plane (Python 3.12)"]
        API_Routes["REST Endpoints (/api/incidents)"]
        Scrubber["Deterministic Secret Scrubber & Error Intelligence"]
        StateEngine["Checkpoint Engine & State Persistence"]
        DB[("MongoDB Persistence")]
        Vault[("Artifact Storage Vault")]
    end

    subgraph OrchestrationTier ["LangGraph Multi-Agent Consensus Engine"]
        LG_Start(["START"])
        Investigator["Investigator Agent"]
        RepoAnalyst["Repository Analyst"]
        TestEng["Test Engineer"]
        Coordinator["Coordinator Agent"]
        Specialists["Domain Specialists (Python, TypeScript, DB, Security, DevOps)"]
        PlanReviewer["Independent Plan Reviewer"]
        RepairEng["Repair Engineer"]
        CodeReviewer["Independent Code Reviewer"]
        LG_End(["END"])
    end

    subgraph SandboxTier ["Deterministic Docker Runtime Sandbox"]
        DockerRuntime["Non-Root Container (UID 1000, Read-Only Root)"]
        KB_Index["AST Knowledge Base Symbol Mapper"]
        TerminalOp["Terminal Operator (SHA-256 Atomic Rewriter)"]
        QualityGate["Deterministic Quality Gate & Test Runner"]
    end

    subgraph DeploymentTier ["Continuous Deployment & External Hosts"]
        GitHub["GitHub API / Repository Branch"]
        ProdHosting["Production Host (Vercel / Render / Railway)"]
    end

    UI_Incident --> API_Routes
    UI_StartRepair --> API_Routes
    UI_ManualPush --> API_Routes
    API_Routes --> Scrubber
    Scrubber --> StateEngine
    StateEngine --> DB
    StateEngine --> Vault

    API_Routes --> LG_Start
    LG_Start --> Investigator & RepoAnalyst & TestEng
    Investigator & RepoAnalyst & TestEng --> Coordinator
    Coordinator --> Specialists
    Specialists --> PlanReviewer
    PlanReviewer -- "Needs Revision (Max 3 Rounds)" --> Coordinator
    PlanReviewer -- "Approved" --> RepairEng
    RepairEng --> CodeReviewer
    CodeReviewer -- "Diff Approved" --> LG_End

    LG_End --> DockerRuntime
    DockerRuntime --> KB_Index
    DockerRuntime --> TerminalOp
    TerminalOp --> QualityGate
    QualityGate --> GitHub
    GitHub -- "Webhook Triggered Deploy" --> ProdHosting
    API_Routes -. "Direct Push Fallback" .-> GitHub
```

---

## Agentic Maturity Assessment (Level 4 System)

VectoraFix is engineered in alignment with enterprise AI autonomy taxonomies:

| Level | Classification | Key Attributes | VectoraFix Implementation |
| :--- | :--- | :--- | :--- |
| **Level 1** | Simple Prompting / Direct Generation | Single-turn, stateless generation, no tool calling. | Atomic LLM leaf evaluations only. |
| **Level 2** | Chained Workflows & Routers | Fixed linear pipelines, prompt chaining, output parsing. | Sub-role LCEL prompt chains. |
| **Level 3** | Autonomous Tool-Using Agents | ReAct loops, dynamic tool calling, self-directed exploration. | `operate_isolated_terminal` inside Docker. |
| **Level 4** | **Collaborative Multi-Agent Systems** | **Dynamic role assignment, inter-agent debate, consensus loops, self-correction, DAG routing.** | **Core VectoraFix Architecture: Coordinated LangGraph team with specialized sub-agents and deterministic checkpoints.** |
| **Level 5** | Unconstrained Autonomous General Agents | Fully unbounded self-direction, open-ended goal generation. | Explicitly avoided. Enterprise production safety mandates deterministic boundaries. |

---

## Multi-Agent Team Composition

VectoraFix employs a directed acyclic graph (DAG) and cyclic review state machine managed by LangGraph. Specialized agent personas collaborate and debate before any code edit is authorized:

```mermaid
classDiagram
    class BaseAgent {
        <<abstract>>
        +AgentRole role
        +string model_name
        +int timeout_seconds
        +analyze(state)
        +review_plan(draft_plan)
    }

    class Investigator {
        +parse_error_traces()
        +isolate_failure_site()
    }
    class RepositoryAnalyst {
        +traverse_ast()
        +extract_symbol_contracts()
    }
    class TestEngineer {
        +discover_test_suites()
        +construct_reproduction_spec()
    }
    class Coordinator {
        +summon_specialists()
        +synthesize_repair_dictionary()
    }
    class DomainSpecialist {
        +string domain_name
        +audit_domain_rules()
    }
    class PlanReviewer {
        +audit_plan_completeness()
        +enforce_file_boundary_rules()
    }
    class RepairEngineer {
        +generate_atomic_file_patch()
    }
    class CodeReviewer {
        +verify_unified_diff()
        +check_regression_risk()
    }

    BaseAgent <|-- Investigator
    BaseAgent <|-- RepositoryAnalyst
    BaseAgent <|-- TestEngineer
    BaseAgent <|-- Coordinator
    BaseAgent <|-- DomainSpecialist
    BaseAgent <|-- PlanReviewer
    BaseAgent <|-- RepairEngineer
    BaseAgent <|-- CodeReviewer
```

### Specialized Persona Responsibilities

- **Investigator**: Deconstructs raw stack traces, error messages, and operational symptoms to isolate the primary failure site.
- **Repository Analyst**: Traverses the AST symbol map to pinpoint target modules, parameter contracts, and dependency graphs.
- **Test Engineer**: Scans test frameworks (`pytest`, `jest`, `vitest`) to discover baseline tests and construct reproduction specifications.
- **Coordinator**: Evaluates preliminary findings, summons up to three domain specialists, and synthesizes the human-readable repair plan.
- **Domain Specialists (Python, TypeScript, Database, Security, DevOps)**:
  - *Python / TypeScript*: Verifies language idioms, type soundness, runtime compatibility, and syntax constraints.
  - *Database*: Audits schema migrations, ORM definitions, and query performance. Strictly prohibits destructive operations.
  - *Security*: Possesses absolute veto authority. Audits authorization boundaries, injection risks, and secret leakage.
  - *DevOps*: Audits package manifests, lockfiles, and container configurations.
- **Plan Reviewer**: Independent auditor acting as a quality gate before repair execution. Rejects ambiguous plans lacking exact file paths or concrete fixes.
- **Repair Engineer**: Generates minimal, scoped atomic file replacements strictly confined to approved targets.
- **Code Reviewer**: Independently audits the complete unified diff against original sources, blocking unapproved edits, binary changes, or style violations.
- **Verification Agent**: Evaluates test execution logs and health probe telemetry against baseline reproduction evidence.
- **Release Engineer**: Enforces final release readiness checklist before granting deployment clearance.

---

## End-to-End Remediation Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer / Webhook
    participant CP as Control Plane (FastAPI)
    participant LG as LangGraph Orchestrator
    participant Sandbox as Docker Sandbox
    participant GH as GitHub API
    participant Prod as Production Host (Vercel/Render)

    Dev->>CP: Ingest Incident (logs, stack traces, metadata)
    CP->>CP: Deterministic Secret Scrubbing
    CP->>LG: Initiate Multi-Agent Diagnosis
    par Parallel Discovery
        LG->>LG: Investigator (Failure Isolation)
        LG->>LG: Repo Analyst (AST Symbol Mapping)
        LG->>LG: Test Engineer (Suite Discovery)
    end
    LG->>LG: Coordinator synthesizes repair plan
    loop Consensus & Adversarial Review (Max 3 Rounds)
        LG->>LG: Domain Specialists & Plan Reviewer Critique
    end
    LG-->>CP: Persist Approved Repair Plan
    CP-->>Dev: Present Repair Plan in UI
    Note over Dev,CP: Human-in-the-Loop Gateway: Operator clicks "Start Repair"
    Dev->>CP: Authorize Repair Execution
    CP->>Sandbox: Spawn Isolated Container (Read-Only Root, Non-Root UID)
    Sandbox->>Sandbox: Terminal Operator: SHA-256 Validated Atomic Writes
    Sandbox->>Sandbox: Execute Manifest-Derived Tests & Quality Gate
    Sandbox-->>CP: Return Verified Patch & Diff Evidence
    CP->>GH: Commit & Push Verified Branch (Git Database API)
    GH->>Prod: Trigger Continuous Deployment Webhook
    Prod-->>Dev: Live Production Service Restored
```

---

## Deterministic Sandbox & Security Architecture

```mermaid
flowchart LR
    subgraph Host ["Host System"]
        CP["FastAPI Control Plane"]
        DB[("MongoDB")]
        Vault[("Artifact Storage Vault")]
    end

    subgraph Sandbox ["Docker Runtime Sandbox"]
        direction TB
        SecurityPolicy["Security Constraints:<br/>- Non-Root UID 1000<br/>- Read-Only Root Filesystem<br/>- CPU: 2 Cores, RAM: 4 GB<br/>- Command Timeout: 180s"]
        NetworkController["Ephemeral Network Bridge<br/>(Toggled strictly for package installs)"]
        WorkspaceMount["/workspace Snapshot Mount<br/>- Prohibited: .git, .env, credentials<br/>- SHA-256 Pre-write verification<br/>- Atomic write and rollback protection"]
    end

    CP -->|"Spawn Ephemeral Container"| SecurityPolicy
    SecurityPolicy --> NetworkController
    NetworkController --> WorkspaceMount
    WorkspaceMount -->|"Store Patches & Logs"| Vault
    CP --> DB
```

### Security Guardrails
1. **Deterministic Secret Scrubber**: Scans all ingested payloads with multi-pattern regular expressions, scrubbing bearer tokens, private keys, API keys, JWTs, and credential-bearing URLs prior to database persistence or LLM prompting.
2. **Read-Only Root Sandbox**: Containers run with `--read-only` root filesystems, restricting all write activity strictly to the `/workspace` mount.
3. **Non-Root Execution**: Container processes execute strictly as an unprivileged user (UID 1000).
4. **Network Gating**: The external network bridge is disabled by default and opened solely for detected package installation steps before being detached for test execution.
5. **Atomic SHA-256 Rewriting**: Source modifications verify target file checksums before performing atomic writes, rolling back to pre-repair snapshots if unexpected modifications occur.
6. **Strict Scope Control**: Any patch modifying files outside the coordinator's approved dictionary is rejected immediately by the deterministic quality gate.

---

## Fault-Tolerant Push Recovery ("Push Saved Repair")

When automated branch pushes fail due to GitHub App permission lapses, expired OAuth tokens, or branch protection rules, VectoraFix avoids wasting model inference or repeating diagnostic cycles:

```mermaid
stateDiagram-v2
    [*] --> DiagnosisApproved: Multi-Agent Consensus Reached
    DiagnosisApproved --> RepairExecution: Operator Clicks Start Repair
    RepairExecution --> Verification: Deterministic Quality Gate
    Verification --> GitPush: Attempt Branch Push via GitHub API
    
    GitPush --> Deployed: Push Succeeded - CI/CD Webhook Triggered
    Deployed --> [*]

    GitPush --> ArtifactVault: Push Failed - Auth or Rate Limit
    ArtifactVault --> SavedState: Persist Patch and Clean Snapshot in Vault
    SavedState --> OperatorResolution: UI Displays Instructions
    OperatorResolution --> ManualPush: Operator Clicks Push Saved Repair
    ManualPush --> Deployed: Reapply Vault Patch and Push Directly
```

---

## Repository Structure

```
VectoraFix/
├── README.md                                # Executive documentation & architecture overview
├── .gitignore                               # Production git ignore specification
│
├── docs/                                    # Exhaustive Architectural Specifications
│   ├── ARCHITECTURE.md                      # Comprehensive system architecture guide
│   ├── AGENT_ORCHESTRATION.md               # LangGraph DAG, cyclic review & agent specs
│   ├── RUNTIME_SANDBOX_AND_SECURITY.md      # Docker sandboxing, threat model & safety
│   ├── API_AND_DATA_CONTRACTS.md            # REST API schemas & persistence specs
│   └── RECRUITER_GUIDE.md                   # Technical breakdown for hiring managers
│
├── public_interfaces/                       # Non-Proprietary Interfaces & Public Contracts
│   ├── schemas/
│   │   ├── incidents.py                     # Pydantic v2 incident models & validators
│   │   └── agents.py                        # Multi-agent consensus & review models
│   └── contracts/
│       ├── base_agent.py                    # Abstract Base Agent contract interface
│       └── sandbox_interface.py             # Sandbox runtime & verification contract
│
└── config/                                  # Public Configuration & Packaging
    ├── .env.example                         # Environment configuration template
    └── pyproject.toml                       # Python packaging & tool definitions
```

---

## Recruiter & Codebase Access Information

> **Notice Regarding Proprietary Source Code**:  
> To protect proprietary intellectual property, algorithm implementations, LangGraph prompt graphs, and automated sandboxing runtimes from unauthorized cloning or distribution, core implementation source code is retained in a private repository.
>
> This showcase repository provides complete architectural documentation, system design specifications, and public contract interfaces demonstrating engineering standards, typing discipline, and system design maturity.

**Full access to the private source repository, end-to-end execution demonstrations, or architectural deep-dive interviews is available upon request.**

### Author & Contact Details

- **Author**: Dhruv Kajare
- **Email**: [kajaredhruv3@gmail.com](mailto:kajaredhruv3@gmail.com)
- **LinkedIn**: [https://www.linkedin.com/in/dhruv-kajare-b060b0260/](https://www.linkedin.com/in/dhruv-kajare-b060b0260/)
- **GitHub**: [@kajaredhruv433](https://github.com/kajaredhruv433)
- **Showcase Repository**: [https://github.com/kajaredhruv433/VectoraFix](https://github.com/kajaredhruv433/VectoraFix)
