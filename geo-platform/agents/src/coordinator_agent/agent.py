"""
Main coordinator class for orchestration.
Orchestrates multiple agents, resolves conflicts, and prioritizes recommendations.
"""

import time
from typing import Dict, Any, List, Optional
from collections import defaultdict

from ..shared.base_agent import BaseAgent
from ..shared.models import (
    WebsiteData, AgentResponse, AnalysisResult, AgentType,
    CoordinatorResponse, ConflictResolution, PriorityMatrix, ImplementationPlan,
    PriorityLevel, ImpactLevel, EffortLevel
)
from ..shared.llm_client import LLMClient
from .conflict_resolver import ConflictResolver
from .prioritizer import Prioritizer


class CoordinatorAgent(BaseAgent):
    """
    Coordinator Agent for multi-agent orchestration.

    Coordinates multiple specialized agents, resolves conflicts between
    their recommendations, and creates unified, prioritized action plans.
    """

    def __init__(self, llm_client: LLMClient):
        super().__init__("Coordinator Agent", llm_client)
        self.conflict_resolver = ConflictResolver(llm_client)
        self.prioritizer = Prioritizer(llm_client)
        self.agent_responses: Dict[str, AgentResponse] = {}

    def get_agent_type(self) -> str:
        return AgentType.COORDINATOR

    async def coordinate_agents(self, agent_responses: List[AgentResponse], website_data: WebsiteData) -> CoordinatorResponse:
        """
        Coordinate multiple agent responses into a unified plan.

        Args:
            agent_responses: List of responses from different agents
            website_data: Original website data for context

        Returns:
            CoordinatorResponse with unified recommendations and implementation plan
        """
        start_time = time.time()
        self._log_analysis_start(str(website_data.url))

        try:
            # Store agent responses for reference
            for response in agent_responses:
                self.agent_responses[response.agent_name] = response

            # Collect all analysis results
            all_results = []
            for response in agent_responses:
                all_results.extend(response.results)

            # Detect and resolve conflicts
            conflicts = await self.conflict_resolver.detect_conflicts(agent_responses)
            conflict_resolutions = await self.conflict_resolver.resolve_conflicts(conflicts, website_data)

            # Apply conflict resolutions to get unified results
            unified_results = self._apply_conflict_resolutions(all_results, conflict_resolutions)

            # Create priority matrix
            priority_matrix = await self.prioritizer.create_priority_matrix(unified_results)

            # Generate implementation plan
            implementation_plan = await self.prioritizer.create_implementation_plan(priority_matrix, website_data)

            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(agent_responses, conflict_resolutions)

            processing_time = time.time() - start_time

            self._log_analysis_complete(str(website_data.url), len(unified_results), overall_confidence)

            return CoordinatorResponse(
                unified_results=unified_results,
                conflict_resolutions=conflict_resolutions,
                priority_matrix=priority_matrix,
                implementation_plan=implementation_plan,
                overall_confidence=overall_confidence,
                processing_time=processing_time,
                timestamp=time.time(),
                metadata={
                    "agent_count": len(agent_responses),
                    "conflict_count": len(conflicts),
                    "resolution_count": len(conflict_resolutions),
                    "total_recommendations": len(unified_results),
                    "agent_confidence_scores": {r.agent_name: r.confidence for r in agent_responses}
                }
            )

        except Exception as e:
            self._log_error(e, f"coordinating agents for {website_data.url}")
            processing_time = time.time() - start_time

            # Return empty coordination response on error
            return CoordinatorResponse(
                unified_results=[],
                conflict_resolutions=[],
                priority_matrix=PriorityMatrix(),
                implementation_plan=ImplementationPlan(),
                overall_confidence=0.0,
                processing_time=processing_time,
                timestamp=time.time(),
                metadata={"error": str(e)}
            )

    async def analyze(self, website_data: WebsiteData) -> AgentResponse:
        """
        Standard analyze method for base compatibility.
        Note: Coordinator typically works with other agent responses.
        """
        # This is a placeholder - coordinators typically don't analyze directly
        return self._create_response(
            results=[],
            confidence=0.0,
            processing_time=0.0,
            metadata={"note": "Coordinator agent requires other agent responses to function"}
        )

    def _apply_conflict_resolutions(self, all_results: List[AnalysisResult],
                                   conflict_resolutions: List[ConflictResolution]) -> List[AnalysisResult]:
        """
        Apply conflict resolutions to create unified results.
        """
        # Create a map of conflicted result IDs
        conflicted_ids = set()
        resolution_map = {}

        for resolution in conflict_resolutions:
            # Track which results were involved in conflicts
            for agent_name in resolution.conflicting_agents:
                if agent_name in self.agent_responses:
                    agent_results = self.agent_responses[agent_name].results
                    for result in agent_results:
                        if self._is_result_related_to_conflict(result, resolution):
                            conflicted_ids.add(result.id)

            # Create new unified result from resolution
            resolution_map[resolution.conflict_id] = self._create_result_from_resolution(resolution)

        # Filter out conflicted results and add resolutions
        unified_results = []

        # Add non-conflicted results
        for result in all_results:
            if result.id not in conflicted_ids:
                unified_results.append(result)

        # Add resolution results
        unified_results.extend(resolution_map.values())

        return unified_results

    def _is_result_related_to_conflict(self, result: AnalysisResult, resolution: ConflictResolution) -> bool:
        """
        Check if a result is related to a specific conflict.
        """
        # Simple heuristic: check if result type or title relates to conflict description
        conflict_keywords = resolution.conflict_description.lower().split()
        result_text = f"{result.type} {result.title} {result.description}".lower()

        # If any conflict keywords appear in result text, consider it related
        return any(keyword in result_text for keyword in conflict_keywords if len(keyword) > 3)

    def _create_result_from_resolution(self, resolution: ConflictResolution) -> AnalysisResult:
        """
        Create an AnalysisResult from a ConflictResolution.
        """
        return AnalysisResult(
            id=f"resolved_{resolution.conflict_id}",
            type="conflict_resolution",
            title=f"Resolved: {resolution.conflict_description}",
            description=resolution.final_recommendation,
            priority=PriorityLevel.HIGH,  # Resolutions are typically high priority
            impact=ImpactLevel.HIGH,
            effort=EffortLevel.MEDIUM,
            recommendation=resolution.final_recommendation,
            implementation_steps=[f"Apply {resolution.resolution_strategy}"],
            confidence=resolution.confidence,
            metadata={
                "conflict_id": resolution.conflict_id,
                "conflicting_agents": resolution.conflicting_agents,
                "resolution_strategy": resolution.resolution_strategy
            }
        )

    def _calculate_overall_confidence(self, agent_responses: List[AgentResponse],
                                    conflict_resolutions: List[ConflictResolution]) -> float:
        """
        Calculate overall confidence based on agent responses and conflict resolutions.
        """
        if not agent_responses:
            return 0.0

        # Base confidence from agent responses
        agent_confidences = [response.confidence for response in agent_responses]
        base_confidence = sum(agent_confidences) / len(agent_confidences)

        # Adjust for conflicts - more conflicts reduce confidence
        conflict_penalty = len(conflict_resolutions) * 0.05  # 5% penalty per conflict

        # Adjust for resolution quality
        if conflict_resolutions:
            resolution_confidences = [res.confidence for res in conflict_resolutions]
            resolution_bonus = (sum(resolution_confidences) / len(resolution_confidences)) * 0.1
        else:
            resolution_bonus = 0.0

        final_confidence = base_confidence - conflict_penalty + resolution_bonus
        return max(0.0, min(1.0, final_confidence))  # Clamp between 0 and 1
