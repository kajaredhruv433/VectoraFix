# VectoraFix: Runtime Sandboxing & Enterprise Security Specification

---

## 1. Security Philosophy & Threat Model

VectoraFix treats all external inputs-including stack traces, error logs, user descriptions, and third-party repository code-as **strictly untrusted data**. To prevent host compromise, secret leakage, or unauthorized code execution, VectoraFix enforces strict isolation boundaries around both the LLM reasoning layer and the execution sandbox.

```mermaid
flowchart TD
    subgraph UntrustedZone ["Untrusted Input Zone"]
        Logs["Error Logs & Stack Traces"]
        RepoSource["Target Repository Code"]
        Webhooks["External CI / Deploy Webhooks"]
    end

    subgraph DefenseLayer1 ["Defense Layer 1: Control Plane"]
        Scrubber["Deterministic Secret Scrubber (Regex Engine)"]
        Validator["Pydantic v2 Bounds & Input Validator"]
        AuthGate["GitHub OAuth & Token Scope Verifier"]
    end

    subgraph DefenseLayer2 ["Defense Layer 2: Docker Sandbox Container"]
        NonRoot["Non-Root User (UID 1000)"]
        ReadOnly["Read-Only Root Filesystem (--read-only)"]
        ResourceCaps["Resource Quotas: 2 Cores | 4 GB RAM | 180s Timeout"]
        NetGating["Controlled Network Bridge (Toggled for npm/pip only)"]
        AtomicWrites["SHA-256 Validated Atomic Writes & Rollback Vault"]
    end

    subgraph DefenseLayer3 ["Defense Layer 3: Deterministic Quality Gate"]
        ScopeCheck["Strict File Scope Enforcer (No Out-of-Plan Edits)"]
        SecretScan["Post-Patch Secret & Credential Scanner"]
        TestPass["Manifest-Derived Test Verification (pytest / npm test)"]
    end

    UntrustedZone --> DefenseLayer1
    DefenseLayer1 --> DefenseLayer2
    DefenseLayer2 --> DefenseLayer3
    DefenseLayer3 --> Production["Verified Branch Push to GitHub"]
```

---

## 2. Deterministic Secret Scrubbing Engine

Before any incident payload is stored in MongoDB or submitted to Google Gemini prompts, the control plane processes all text through a deterministic regular expression sanitization engine:

```mermaid
flowchart LR
    RawPayload["Raw Incident Payload<br/>(Logs, Headers, Traces)"] --> ScrubberEngine["Secret Scrubber Engine"]
    
    ScrubberEngine --> R1["Bearer Tokens & JWTs"]
    ScrubberEngine --> R2["Cloud API Keys (AWS, GCP, OpenAI)"]
    ScrubberEngine --> R3["Private Key Blocks (RSA, ECDSA)"]
    ScrubberEngine --> R4["Basic Auth & Connection Strings"]

    R1 & R2 & R3 & R4 --> SanitizedPayload["Sanitized Diagnostic Document<br/>(Tokens replaced with [REDACTED_SECRET])"]
    SanitizedPayload --> DB[("MongoDB")]
    SanitizedPayload --> LLM["Gemini Model Ingestion"]
```

### Redaction Rules
- **Authentication Tokens**: Authorization headers (`Bearer [A-Za-z0-9\-._~+/]+=*`) are scrubbed.
- **JWT Signatures**: Triple-base64 JSON Web Tokens (`eyJ...`) are replaced with `[REDACTED_JWT]`.
- **Cloud Provider Credentials**: Patterns for AWS access keys (`AKIA[0-9A-Z]{16}`), Google API keys (`AIza[0-9A-Za-z-_]{35}`), and private tokens are masked.
- **Private Key Blocks**: Any occurrences of `-----BEGIN RSA PRIVATE KEY-----` or `-----BEGIN OPENSSH PRIVATE KEY-----` blocks are completely redacted.
- **Database Connection Strings**: URLs with embedded credentials (`mongodb://user:pass@host...`) have credentials removed.

---

## 3. Docker Runtime Sandboxing Specification

All code modification, dependency installation, compilation, and test execution occur inside disposable Docker containers:

```mermaid
flowchart TB
    subgraph HostOS ["Host Infrastructure"]
        HostDaemon["Docker Engine Daemon"]
        VaultDir["Artifact Storage Vault (/artifacts)"]
    end

    subgraph SandboxContainer ["Docker Sandbox Container (python:3.12-slim / node:22-slim)"]
        direction TB
        ContainerLimits["Kernel Constraints:<br/>- User: non-root (UID 1000)<br/>- Root FS: Read-Only (--read-only)<br/>- Memory: 4 GB max (--memory=4g)<br/>- CPU: 2 Cores max (--cpus=2.0)<br/>- Timeout: 180s per command"]
        
        subgraph Mounts ["Filesystem Mounts"]
            Workspace["/workspace (Disposable Snapshot Mount - R/W)"]
            TmpFs["/tmp (In-Memory tmpfs - 256MB)"]
        end

        subgraph NetworkState ["Ephemeral Network Controller"]
            NetClosed["External Network Disabled (Default for Tests)"]
            NetOpen["Package Registry Bridge (Enabled strictly for pip/npm install)"]
        end
    end

    HostDaemon --> SandboxContainer
    SandboxContainer --> VaultDir
```

### Container Hardening Specifications
1. **Unprivileged Execution**: The container user is pinned to UID 1000 (`non-root`). Root access inside the container is explicitly disabled.
2. **Read-Only Root Filesystem**: The container is started with the `--read-only` flag. System binaries, `/usr`, `/lib`, and `/etc` are immutable.
3. **Dedicated In-Memory `/tmp`**: A 256MB `tmpfs` is mounted at `/tmp` to allow temporary files without touching the host filesystem.
4. **Strict Resource Quotas**: Containers are constrained to 2 CPU cores and 4 GB of RAM to prevent denial-of-service via runaway processes or infinite test loops.
5. **Execution Timeouts**: Every shell command executed by the terminal operator enforces a hard 180-second timeout.

---

## 4. Atomic File Rewriting & Rollback Protection

To prevent file corruption or partial writes, the terminal operator performs **SHA-256 validated atomic rewrites**:

```mermaid
sequenceDiagram
    autonumber
    participant Op as Terminal Operator (Agent)
    participant FS as Container /workspace
    participant Vault as Snapshot Rollback Vault

    Op->>FS: 1. Read existing file content
    FS-->>Op: Return content & current SHA-256 hash
    Op->>Op: 2. Compute full replacement content
    Op->>FS: 3. Submit rewrite request (Target Path, Expected SHA-256, New Content)
    
    alt SHA-256 matches expected state
        FS->>FS: Write to temporary file (.tmp_update)
        FS->>FS: Atomically rename .tmp_update -> target file
        FS-->>Op: Confirm atomic rewrite success
    else SHA-256 Mismatch (Race Condition / Unauthorized Edit)
        FS-->>Op: Rewrite rejected: Pre-condition failed
        Op->>Vault: Trigger immediate rollback to baseline snapshot
        Vault->>FS: Restore clean workspace
    end
```

---

## 5. Scope-Enforcing Deterministic Quality Gate

Before any code modification can be considered for continuous deployment, it must satisfy the deterministic quality gate:

1. **Reproduction Baseline Check**: The failure reported in the incident must reproduce on the baseline repository snapshot.
2. **Failure Resolution Check**: The failure must no longer reproduce after the patch is applied.
3. **Regression Suite Pass**: All existing repository tests (`pytest`, `npm test`, `cargo test`) must execute and pass without failure.
4. **Scope Allowlist Validation**: The unified diff is parsed. If any file outside the coordinator's approved repair dictionary was modified, the patch is rejected.
5. **Secret & Sensitive File Scan**: The patch is scanned to ensure no credentials, tokens, `.env` files, or binary artifacts were added.
6. **Independent Code Reviewer Approval**: An independent LLM audit approves the diff for code style, maintainability, and architectural safety.

---

## Recruiter & Access Notice

The complete sandbox orchestration engine, container lifecycle manager, terminal operator, and rollback manager are maintained in a private repository. Full access to the private repository, technical walkthroughs, or code reviews is available upon contacting:

- **Author**: Dhruv Kajare
- **Email**: [kajaredhruv3@gmail.com](mailto:kajaredhruv3@gmail.com)
- **LinkedIn**: [https://www.linkedin.com/in/dhruv-kajare-b060b0260/](https://www.linkedin.com/in/dhruv-kajare-b060b0260/)
- **GitHub**: [@kajaredhruv433](https://github.com/kajaredhruv433)
