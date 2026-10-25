"""
VectoraFix Public Interface Specification
Module: schemas.agents

Defines public contract models for multi-agent coordination, domain specialist
critique structures, human-in-the-loop repair plans, and verification verdicts.
"""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

AgentRole = Literal[
    "coordinator",
    "investigator",
    "repository_analyst",
    "test_engineer",
    "python_specialist",
    "typescript_specialist",
    "frontend_specialist",
    "backend_specialist",
    "database_specialist",
    "security_specialist",
    "devops_specialist",
    "plan_reviewer",
    "repair_engineer",
    "code_reviewer",
    "verification_agent",
    "release_engineer",
]

ReviewStatus = Literal["approved", "needs_revision", "rejected"]
VerificationVerdict = Literal["resolved", "not_resolved", "inconclusive"]


class FileRepairTarget(BaseModel):
    """Specification of an atomic file modification target in an approved plan."""
    model_config = ConfigDict(extra="ignore")

    path: str = Field(description="Normalized repository relative path")
    defectDescription: str = Field(description="Identified root defect in this file")
    plannedFix: str = Field(description="Exact structural or logic correction")
    expectedBehavior: str = Field(description="Post-modification contract")
    riskLevel: Literal["low", "medium", "high"] = Field(default="low")


class SpecialistReview(BaseModel):
    """Structured critique returned by an adversarial specialist agent."""
    model_config = ConfigDict(extra="ignore")

    role: AgentRole
    status: ReviewStatus
    confidenceScore: float = Field(ge=0.0, le=1.0)
    critique: str
    suggestedImprovements: list[str] = Field(default_factory=list)
    securityFlags: list[str] = Field(default_factory=list)


class RepairPlanSummary(BaseModel):
    """Human-in-the-loop repair plan presented for explicit operator authorization."""
    model_config = ConfigDict(extra="ignore")

    workflowId: str
    incidentId: str
    summary: str
    rootCause: str
    filesToModify: list[FileRepairTarget]
    hasDatabaseMigration: bool = False
    requiredTests: list[str] = Field(default_factory=list)
    riskAssessment: str
    consensusRounds: int = 1
    operatorApproved: bool = False


class VerificationResult(BaseModel):
    """Deterministic validation output from post-repair execution."""
    model_config = ConfigDict(extra="ignore")

    verdict: VerificationVerdict
    reproducedOnBaseline: bool
    reproducedAfterPatch: bool
    regressionTestsPassed: bool
    codeReviewApproved: bool
    scopeViolationsDetected: bool
    executionLogsExcerpt: str
