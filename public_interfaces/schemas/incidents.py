"""
VectoraFix Public Interface Specification
Module: schemas.incidents

Defines the Pydantic v2 data models for production incident ingestion,
diagnostic evidence validation, and remediation lifecycle payloads.
Core proprietary agent logic and execution engines remain guarded.
"""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

ErrorSource = Literal[
    "browser_console",
    "frontend_runtime",
    "backend_runtime",
    "vercel_build",
    "vercel_deployment",
    "other_hosting_build",
    "github_actions",
    "dependency_installation",
    "configuration",
    "database",
    "network",
    "unknown",
]


class IncidentCreate(BaseModel):
    """
    Ingestion payload for new incident reports.
    Enforces deterministic validation boundaries and input length bounds.
    """
    model_config = ConfigDict(extra="ignore")

    projectId: str = Field(min_length=1, max_length=120, description="Unique identifier for the registered project")
    environment: str = Field(default="production", max_length=80, description="Target environment (production, staging, preview)")
    title: str = Field(default="Reported error", min_length=1, max_length=200, description="Short descriptive title of the incident")
    description: str = Field(default="", max_length=10_000, description="Human-written issue explanation")
    stackTrace: str | None = Field(default=None, max_length=60_000, description="Raw stack trace or exception trace")
    deploymentRef: str | None = Field(default=None, max_length=300, description="Vercel deployment ID, commit SHA, or build URL")
    repositoryId: int | None = Field(default=None, description="GitHub repository ID")
    repositoryFullName: str | None = Field(default=None, max_length=300, description="Repository identifier (owner/repo)")
    commitSha: str | None = Field(default=None, max_length=80, description="Target base commit SHA")
    errorSource: ErrorSource = Field(default="unknown", description="Classification source of the failure")
    errorMessage: str | None = Field(default=None, max_length=10_000, description="Primary error message")
    logs: str | None = Field(default=None, max_length=60_000, description="Server, build, or container log excerpts")
    affectedUrl: str | None = Field(default=None, max_length=2_000, description="HTTP endpoint or web URL where failure was observed")
    framework: str | None = Field(default=None, max_length=100, description="Target framework (Next.js, FastAPI, Express, etc.)")
    runtime: str | None = Field(default=None, max_length=100, description="Target runtime (Node.js 20, Python 3.12, etc.)")
    expectedBehavior: str | None = Field(default=None, max_length=5_000, description="Expected operational behavior")
    actualBehavior: str | None = Field(default=None, max_length=5_000, description="Observed failure behavior")
    idempotencyKey: str | None = Field(default=None, max_length=200, description="Deduplication key for webhook/API retries")

    @model_validator(mode="after")
    def validate_diagnostic_evidence(self):
        """Ensures at least one actionable diagnostic signal exists within safe size bounds."""
        if not any((self.description.strip(), self.errorMessage, self.stackTrace, self.logs)):
            raise ValueError("At least one diagnostic signal is required: description, errorMessage, stackTrace, or logs")
        total = sum(
            len(getattr(self, name) or "")
            for name in ("description", "errorMessage", "stackTrace", "logs", "expectedBehavior", "actualBehavior")
        )
        if total > 100_000:
            raise ValueError("Combined diagnostic input exceeds the 100,000 character maximum limit")
        return self


class EvidenceUpdate(BaseModel):
    """
    Payload for incrementally adding error logs or reproduction signals to an existing incident.
    """
    model_config = ConfigDict(extra="ignore")

    logs: str | None = Field(default=None, max_length=60_000)
    stackTrace: str | None = Field(default=None, max_length=60_000)
    errorMessage: str | None = Field(default=None, max_length=10_000)
    description: str | None = Field(default=None, max_length=10_000)
    commitSha: str | None = Field(default=None, max_length=80)
    deploymentRef: str | None = Field(default=None, max_length=300)
    expectedBehavior: str | None = Field(default=None, max_length=5_000)
    actualBehavior: str | None = Field(default=None, max_length=5_000)

    @model_validator(mode="after")
    def validate_evidence_presence(self):
        values = self.model_dump(exclude_none=True)
        if not values:
            raise ValueError("At least one evidence field must be supplied")
        if sum(len(value) for value in values.values() if isinstance(value, str)) > 100_000:
            raise ValueError("Combined diagnostic update exceeds 100,000 characters")
        return self


class IncidentResponse(BaseModel):
    """Public read model for an incident record."""
    model_config = ConfigDict(extra="ignore")

    id: str
    projectId: str
    title: str
    environment: str
    status: Literal["open", "diagnosing", "diagnosed", "repairing", "verified", "failed", "resolved"]
    errorSource: ErrorSource
    createdAt: str
    updatedAt: str
