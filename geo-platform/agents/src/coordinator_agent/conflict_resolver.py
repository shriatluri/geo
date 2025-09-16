"""
Handle agent conflicts for coordinator agent.
Detects and resolves contradictory recommendations between agents.
"""

import asyncio
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict
import difflib

from ..shared.models import (
    AgentResponse, AnalysisResult, ConflictResolution, WebsiteData,
    PriorityLevel, ImpactLevel, EffortLevel
)
from ..shared.llm_client import LLMClient


class ConflictType:
    """Types of conflicts that can occur between agents."""
    CONTRADICTORY_RECOMMENDATIONS = "contradictory_recommendations"
    OVERLAPPING_SCOPE = "overlapping_scope"
    PRIORITY_MISMATCH = "priority_mismatch"
    IMPLEMENTATION_CONFLICT = "implementation_conflict"
    RESOURCE_COMPETITION = "resource_competition"


class ConflictResolver:
    """
    Resolves conflicts between agent recommendations.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.conflict_strategies = self._initialize_strategies()

    async def detect_conflicts(self, agent_responses: List[AgentResponse]) -> List[Dict[str, Any]]:
        """
        Detect conflicts between agent responses.

        Args:
            agent_responses: List of agent responses to analyze

        Returns:
            List of detected conflicts with metadata
        """
        conflicts = []

        # Check for contradictory recommendations
        contradictory_conflicts = await self._detect_contradictory_recommendations(agent_responses)
        conflicts.extend(contradictory_conflicts)

        # Check for overlapping scope conflicts
        overlapping_conflicts = await self._detect_overlapping_scope(agent_responses)
        conflicts.extend(overlapping_conflicts)

        # Check for priority mismatches
        priority_conflicts = await self._detect_priority_mismatches(agent_responses)
        conflicts.extend(priority_conflicts)

        # Check for implementation conflicts
        implementation_conflicts = await self._detect_implementation_conflicts(agent_responses)
        conflicts.extend(implementation_conflicts)

        return conflicts

    async def resolve_conflicts(self, conflicts: List[Dict[str, Any]], website_data: WebsiteData) -> List[ConflictResolution]:
        """
        Resolve detected conflicts.

        Args:
            conflicts: List of detected conflicts
            website_data: Website context for resolution decisions

        Returns:
            List of conflict resolutions
        """
        resolutions = []

        for conflict in conflicts:
            try:
                resolution = await self._resolve_single_conflict(conflict, website_data)
                if resolution:
                    resolutions.append(resolution)
            except Exception as e:
                # Log error but continue with other resolutions
                print(f"Error resolving conflict {conflict.get('id', 'unknown')}: {e}")
                continue

        return resolutions

    async def _detect_contradictory_recommendations(self, agent_responses: List[AgentResponse]) -> List[Dict[str, Any]]:
        """
        Detect contradictory recommendations between agents.
        """
        conflicts = []
        result_pairs = []

        # Get all result pairs from different agents
        for i, response1 in enumerate(agent_responses):
            for j, response2 in enumerate(agent_responses[i+1:], i+1):
                for result1 in response1.results:
                    for result2 in response2.results:
                        result_pairs.append((result1, result2, response1.agent_name, response2.agent_name))

        # Check each pair for contradictions
        for result1, result2, agent1, agent2 in result_pairs:
            if await self._are_recommendations_contradictory(result1, result2):
                conflict_id = f"contradiction_{len(conflicts)}"
                conflicts.append({
                    "id": conflict_id,
                    "type": ConflictType.CONTRADICTORY_RECOMMENDATIONS,
                    "agents": [agent1, agent2],
                    "results": [result1, result2],
                    "description": f"Contradictory recommendations between {agent1} and {agent2}",
                    "severity": self._calculate_conflict_severity(result1, result2)
                })

        return conflicts

    async def _detect_overlapping_scope(self, agent_responses: List[AgentResponse]) -> List[Dict[str, Any]]:
        """
        Detect overlapping scope conflicts.
        """
        conflicts = []
        type_groups = defaultdict(list)

        # Group results by type
        for response in agent_responses:
            for result in response.results:
                type_groups[result.type].append((result, response.agent_name))

        # Check for overlaps within each type
        for result_type, results_and_agents in type_groups.items():
            if len(results_and_agents) > 1:
                # Multiple agents addressing the same type - potential overlap
                agents_involved = list(set(agent for _, agent in results_and_agents))
                if len(agents_involved) > 1:
                    conflict_id = f"overlap_{result_type}_{len(conflicts)}"
                    conflicts.append({
                        "id": conflict_id,
                        "type": ConflictType.OVERLAPPING_SCOPE,
                        "agents": agents_involved,
                        "results": [result for result, _ in results_and_agents],
                        "description": f"Multiple agents addressing {result_type}",
                        "severity": "medium"
                    })

        return conflicts

    async def _detect_priority_mismatches(self, agent_responses: List[AgentResponse]) -> List[Dict[str, Any]]:
        """
        Detect priority mismatches for similar recommendations.
        """
        conflicts = []
        similar_pairs = []

        # Find similar results with different priorities
        for i, response1 in enumerate(agent_responses):
            for j, response2 in enumerate(agent_responses[i+1:], i+1):
                for result1 in response1.results:
                    for result2 in response2.results:
                        if (self._are_results_similar(result1, result2) and
                            result1.priority != result2.priority):
                            similar_pairs.append((result1, result2, response1.agent_name, response2.agent_name))

        # Create conflicts for priority mismatches
        for result1, result2, agent1, agent2 in similar_pairs:
            conflict_id = f"priority_mismatch_{len(conflicts)}"
            conflicts.append({
                "id": conflict_id,
                "type": ConflictType.PRIORITY_MISMATCH,
                "agents": [agent1, agent2],
                "results": [result1, result2],
                "description": f"Priority mismatch for similar recommendations: {result1.priority} vs {result2.priority}",
                "severity": self._calculate_priority_mismatch_severity(result1.priority, result2.priority)
            })

        return conflicts

    async def _detect_implementation_conflicts(self, agent_responses: List[AgentResponse]) -> List[Dict[str, Any]]:
        """
        Detect implementation conflicts between recommendations.
        """
        conflicts = []
        implementation_steps = []

        # Collect all implementation steps
        for response in agent_responses:
            for result in response.results:
                for step in result.implementation_steps:
                    implementation_steps.append((step, result, response.agent_name))

        # Check for conflicting implementation steps
        for i, (step1, result1, agent1) in enumerate(implementation_steps):
            for j, (step2, result2, agent2) in enumerate(implementation_steps[i+1:], i+1):
                if agent1 != agent2 and self._are_steps_conflicting(step1, step2):
                    conflict_id = f"implementation_conflict_{len(conflicts)}"
                    conflicts.append({
                        "id": conflict_id,
                        "type": ConflictType.IMPLEMENTATION_CONFLICT,
                        "agents": [agent1, agent2],
                        "results": [result1, result2],
                        "description": f"Conflicting implementation steps: '{step1}' vs '{step2}'",
                        "severity": "high"
                    })

        return conflicts

    async def _resolve_single_conflict(self, conflict: Dict[str, Any], website_data: WebsiteData) -> ConflictResolution:
        """
        Resolve a single conflict.
        """
        conflict_type = conflict["type"]
        strategy = self.conflict_strategies.get(conflict_type, "merge")

        if conflict_type == ConflictType.CONTRADICTORY_RECOMMENDATIONS:
            return await self._resolve_contradictory_recommendations(conflict, website_data)
        elif conflict_type == ConflictType.OVERLAPPING_SCOPE:
            return await self._resolve_overlapping_scope(conflict, website_data)
        elif conflict_type == ConflictType.PRIORITY_MISMATCH:
            return await self._resolve_priority_mismatch(conflict, website_data)
        elif conflict_type == ConflictType.IMPLEMENTATION_CONFLICT:
            return await self._resolve_implementation_conflict(conflict, website_data)
        else:
            return await self._resolve_generic_conflict(conflict, website_data)

    async def _resolve_contradictory_recommendations(self, conflict: Dict[str, Any], website_data: WebsiteData) -> ConflictResolution:
        """
        Resolve contradictory recommendations.
        """
        results = conflict["results"]
        agents = conflict["agents"]

        # Use LLM to determine the best approach
        prompt = f"""
        Two agents have provided contradictory recommendations:

        Agent {agents[0]}: {results[0].recommendation}
        Priority: {results[0].priority}, Impact: {results[0].impact}, Effort: {results[0].effort}

        Agent {agents[1]}: {results[1].recommendation}
        Priority: {results[1].priority}, Impact: {results[1].impact}, Effort: {results[1].effort}

        Website URL: {website_data.url}

        Please provide a unified recommendation that resolves this conflict.
        Consider the priority, impact, and effort levels when making your decision.

        Return only the final recommendation without explanation.
        """

        try:
            unified_recommendation = await self.llm_client.generate_text(prompt)
        except Exception:
            # Fallback to rule-based resolution
            unified_recommendation = self._rule_based_resolution(results)

        return ConflictResolution(
            conflict_id=conflict["id"],
            conflicting_agents=agents,
            conflict_description=conflict["description"],
            resolution_strategy="LLM-guided unification",
            final_recommendation=unified_recommendation,
            confidence=0.8
        )

    async def _resolve_overlapping_scope(self, conflict: Dict[str, Any], website_data: WebsiteData) -> ConflictResolution:
        """
        Resolve overlapping scope conflicts by merging recommendations.
        """
        results = conflict["results"]
        agents = conflict["agents"]

        # Merge overlapping recommendations
        merged_steps = []
        seen_steps = set()

        for result in results:
            for step in result.implementation_steps:
                if step.lower() not in seen_steps:
                    merged_steps.append(step)
                    seen_steps.add(step.lower())

        final_recommendation = f"Consolidated approach addressing {conflict['description']}: {', '.join(merged_steps[:3])}..."

        return ConflictResolution(
            conflict_id=conflict["id"],
            conflicting_agents=agents,
            conflict_description=conflict["description"],
            resolution_strategy="Scope consolidation",
            final_recommendation=final_recommendation,
            confidence=0.7
        )

    async def _resolve_priority_mismatch(self, conflict: Dict[str, Any], website_data: WebsiteData) -> ConflictResolution:
        """
        Resolve priority mismatches.
        """
        results = conflict["results"]
        agents = conflict["agents"]

        # Choose the higher priority as the resolved priority
        priority_order = [PriorityLevel.CRITICAL, PriorityLevel.HIGH, PriorityLevel.MEDIUM, PriorityLevel.LOW]
        highest_priority = min(results, key=lambda r: priority_order.index(r.priority)).priority

        final_recommendation = f"Resolved priority conflict: Set priority to {highest_priority} based on agent consensus"

        return ConflictResolution(
            conflict_id=conflict["id"],
            conflicting_agents=agents,
            conflict_description=conflict["description"],
            resolution_strategy="Priority elevation",
            final_recommendation=final_recommendation,
            confidence=0.9
        )

    async def _resolve_implementation_conflict(self, conflict: Dict[str, Any], website_data: WebsiteData) -> ConflictResolution:
        """
        Resolve implementation conflicts.
        """
        results = conflict["results"]
        agents = conflict["agents"]

        # Sequence conflicting steps or choose the safer approach
        final_recommendation = "Sequence conflicting implementation steps to avoid conflicts"

        return ConflictResolution(
            conflict_id=conflict["id"],
            conflicting_agents=agents,
            conflict_description=conflict["description"],
            resolution_strategy="Step sequencing",
            final_recommendation=final_recommendation,
            confidence=0.75
        )

    async def _resolve_generic_conflict(self, conflict: Dict[str, Any], website_data: WebsiteData) -> ConflictResolution:
        """
        Generic conflict resolution fallback.
        """
        agents = conflict["agents"]
        final_recommendation = "Apply hybrid approach combining agent recommendations"

        return ConflictResolution(
            conflict_id=conflict["id"],
            conflicting_agents=agents,
            conflict_description=conflict["description"],
            resolution_strategy="Hybrid approach",
            final_recommendation=final_recommendation,
            confidence=0.6
        )

    def _initialize_strategies(self) -> Dict[str, str]:
        """
        Initialize conflict resolution strategies.
        """
        return {
            ConflictType.CONTRADICTORY_RECOMMENDATIONS: "llm_guided",
            ConflictType.OVERLAPPING_SCOPE: "merge",
            ConflictType.PRIORITY_MISMATCH: "elevate",
            ConflictType.IMPLEMENTATION_CONFLICT: "sequence",
            ConflictType.RESOURCE_COMPETITION: "optimize"
        }

    async def _are_recommendations_contradictory(self, result1: AnalysisResult, result2: AnalysisResult) -> bool:
        """
        Check if two recommendations are contradictory.
        """
        # Simple heuristic: check for opposite keywords
        contradictory_pairs = [
            (["add", "implement", "create"], ["remove", "delete", "disable"]),
            (["increase", "enhance", "improve"], ["decrease", "reduce", "minimize"]),
            (["enable", "activate"], ["disable", "deactivate"]),
            (["show", "display"], ["hide", "conceal"])
        ]

        rec1 = result1.recommendation.lower()
        rec2 = result2.recommendation.lower()

        for positive_words, negative_words in contradictory_pairs:
            if (any(word in rec1 for word in positive_words) and
                any(word in rec2 for word in negative_words)) or \
               (any(word in rec2 for word in positive_words) and
                any(word in rec1 for word in negative_words)):
                return True

        return False

    def _are_results_similar(self, result1: AnalysisResult, result2: AnalysisResult) -> bool:
        """
        Check if two results are similar enough to have priority conflicts.
        """
        # Use string similarity for titles and descriptions
        title_similarity = difflib.SequenceMatcher(None, result1.title, result2.title).ratio()
        desc_similarity = difflib.SequenceMatcher(None, result1.description, result2.description).ratio()

        return title_similarity > 0.6 or desc_similarity > 0.6

    def _are_steps_conflicting(self, step1: str, step2: str) -> bool:
        """
        Check if two implementation steps are conflicting.
        """
        # Simple conflict detection
        conflict_indicators = [
            ("add", "remove"),
            ("create", "delete"),
            ("enable", "disable"),
            ("increase", "decrease")
        ]

        step1_lower = step1.lower()
        step2_lower = step2.lower()

        for word1, word2 in conflict_indicators:
            if (word1 in step1_lower and word2 in step2_lower) or \
               (word2 in step1_lower and word1 in step2_lower):
                return True

        return False

    def _calculate_conflict_severity(self, result1: AnalysisResult, result2: AnalysisResult) -> str:
        """
        Calculate conflict severity based on result properties.
        """
        # High severity if both results have high priority/impact
        high_priority_levels = [PriorityLevel.HIGH, PriorityLevel.CRITICAL]
        high_impact_levels = [ImpactLevel.HIGH, ImpactLevel.CRITICAL]

        if (result1.priority in high_priority_levels and result2.priority in high_priority_levels) or \
           (result1.impact in high_impact_levels and result2.impact in high_impact_levels):
            return "high"
        elif result1.priority in high_priority_levels or result2.priority in high_priority_levels:
            return "medium"
        else:
            return "low"

    def _calculate_priority_mismatch_severity(self, priority1: PriorityLevel, priority2: PriorityLevel) -> str:
        """
        Calculate severity of priority mismatch.
        """
        priority_values = {
            PriorityLevel.LOW: 1,
            PriorityLevel.MEDIUM: 2,
            PriorityLevel.HIGH: 3,
            PriorityLevel.CRITICAL: 4
        }

        diff = abs(priority_values[priority1] - priority_values[priority2])
        if diff >= 3:
            return "high"
        elif diff >= 2:
            return "medium"
        else:
            return "low"

    def _rule_based_resolution(self, results: List[AnalysisResult]) -> str:
        """
        Fallback rule-based resolution when LLM is unavailable.
        """
        # Choose the result with higher confidence
        best_result = max(results, key=lambda r: r.confidence)
        return f"Resolved using highest confidence recommendation: {best_result.recommendation}"
