"""
VectoraFix Public Interface Specification
Module: contracts.base_agent

Provides the abstract protocol for LangGraph-integrated agent participants.
Shows clean typing, lifecycle hooks, and contract separation. Proprietary reasoning
nodes and prompt templates remain guarded in the private repository.
"""

from abc import ABC, abstractmethod
from typing import Any
from public_interfaces.schemas.agents import AgentRole, SpecialistReview


class BaseAgent(ABC):
    """
    Abstract interface for specialized engineering personas participating
    in the LangGraph collaborative consensus loop.
    """

    def __init__(self, role: AgentRole, model_name: str, timeout_seconds: int = 180) -> None:
        self.role = role
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    @abstractmethod
    async def analyze(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Executes domain-specific analysis based on sanitized evidence
        and AST knowledge base context.

        Args:
            state: Current LangGraph shared state dictionary.

        Returns:
            Dictionary containing state delta to be merged into LangGraph state.
        """
        pass

    @abstractmethod
    async def review_plan(self, draft_plan: dict[str, Any], context: dict[str, Any]) -> SpecialistReview:
        """
        Adversarially audits a proposed multi-file repair plan.

        Args:
            draft_plan: Proposed file modifications and structural changes.
            context: AST symbol signatures and sanitized incident evidence.

        Returns:
            SpecialistReview containing verdict, confidence, and critique.
        """
        pass
