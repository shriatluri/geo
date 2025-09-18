"""
Tests for CoordinatorAgent and its components.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.coordinator_agent.agent import CoordinatorAgent
from src.coordinator_agent.conflict_resolver import ConflictResolver, ConflictType
from src.coordinator_agent.prioritizer import Prioritizer
from src.shared.models import (
    WebsiteData, AgentResponse, AnalysisResult, ConflictResolution,
    PriorityMatrix, ImplementationPlan, PriorityLevel, ImpactLevel, EffortLevel
)


class TestCoordinatorAgent:
    """Test cases for CoordinatorAgent."""

    @pytest.fixture
    def coordinator_agent(self, mock_llm_client):
        """Create coordinator agent instance."""
        return CoordinatorAgent(mock_llm_client)

    @pytest.mark.asyncio
    async def test_coordinate_agents_success(self, coordinator_agent, sample_agent_responses, sample_website_data):
        """Test successful agent coordination."""
        # Mock conflict resolver and prioritizer
        coordinator_agent.conflict_resolver.detect_conflicts = AsyncMock(return_value=[])
        coordinator_agent.conflict_resolver.resolve_conflicts = AsyncMock(return_value=[])
        coordinator_agent.prioritizer.create_priority_matrix = AsyncMock(return_value=PriorityMatrix())
        coordinator_agent.prioritizer.create_implementation_plan = AsyncMock(return_value=ImplementationPlan())

        result = await coordinator_agent.coordinate_agents(sample_agent_responses, sample_website_data)

        assert result.unified_results is not None
        assert len(result.unified_results) == 2  # Both agent results included
        assert result.overall_confidence > 0
        assert result.processing_time > 0

    @pytest.mark.asyncio
    async def test_coordinate_agents_with_conflicts(self, coordinator_agent, sample_agent_responses, sample_website_data):
        """Test coordination with conflicts that need resolution."""
        # Mock conflicts detected
        conflicts = [{
            "id": "test_conflict",
            "type": ConflictType.CONTRADICTORY_RECOMMENDATIONS,
            "agents": ["AEO Agent", "GEO Agent"],
            "description": "Test conflict"
        }]

        resolutions = [ConflictResolution(
            conflict_id="test_conflict",
            conflicting_agents=["AEO Agent", "GEO Agent"],
            conflict_description="Test conflict",
            resolution_strategy="merge",
            final_recommendation="Merged recommendation",
            confidence=0.8
        )]

        coordinator_agent.conflict_resolver.detect_conflicts = AsyncMock(return_value=conflicts)
        coordinator_agent.conflict_resolver.resolve_conflicts = AsyncMock(return_value=resolutions)
        coordinator_agent.prioritizer.create_priority_matrix = AsyncMock(return_value=PriorityMatrix())
        coordinator_agent.prioritizer.create_implementation_plan = AsyncMock(return_value=ImplementationPlan())

        result = await coordinator_agent.coordinate_agents(sample_agent_responses, sample_website_data)

        assert len(result.conflict_resolutions) == 1
        assert result.conflict_resolutions[0].conflict_id == "test_conflict"
        coordinator_agent.conflict_resolver.resolve_conflicts.assert_called_once()

    @pytest.mark.asyncio
    async def test_coordinate_agents_error_handling(self, coordinator_agent, sample_agent_responses, sample_website_data):
        """Test error handling during coordination."""
        # Mock error in conflict detection
        coordinator_agent.conflict_resolver.detect_conflicts = AsyncMock(side_effect=Exception("Test error"))

        result = await coordinator_agent.coordinate_agents(sample_agent_responses, sample_website_data)

        assert result.overall_confidence == 0.0
        assert "error" in result.metadata
        assert result.unified_results == []

    def test_apply_conflict_resolutions(self, coordinator_agent):
        """Test application of conflict resolutions."""
        # Create test results
        results = [
            AnalysisResult(
                id="test1", type="schema", title="Test 1", description="Test result 1",
                priority=PriorityLevel.HIGH, impact=ImpactLevel.HIGH, effort=EffortLevel.LOW,
                recommendation="Test recommendation 1", confidence=0.8
            ),
            AnalysisResult(
                id="test2", type="schema", title="Test 2", description="Test result 2",
                priority=PriorityLevel.MEDIUM, impact=ImpactLevel.MEDIUM, effort=EffortLevel.MEDIUM,
                recommendation="Test recommendation 2", confidence=0.7
            )
        ]

        # Create test resolution
        resolutions = [ConflictResolution(
            conflict_id="test_conflict",
            conflicting_agents=["Agent1", "Agent2"],
            conflict_description="schema markup conflict",
            resolution_strategy="merge",
            final_recommendation="Merged schema recommendation",
            confidence=0.85
        )]

        # Set up agent responses
        coordinator_agent.agent_responses = {
            "Agent1": MagicMock(results=[results[0]]),
            "Agent2": MagicMock(results=[results[1]])
        }

        unified_results = coordinator_agent._apply_conflict_resolutions(results, resolutions)

        # Check that resolution result was added
        resolution_results = [r for r in unified_results if r.type == "conflict_resolution"]
        assert len(resolution_results) == 1
        assert "Resolved" in resolution_results[0].title

    def test_calculate_overall_confidence(self, coordinator_agent, sample_agent_responses):
        """Test overall confidence calculation."""
        # Test with no conflicts
        confidence = coordinator_agent._calculate_overall_confidence(sample_agent_responses, [])
        expected = (0.85 + 0.8) / 2  # Average of agent confidences
        assert abs(confidence - expected) < 0.01

        # Test with conflicts (should reduce confidence)
        resolutions = [ConflictResolution(
            conflict_id="test", conflicting_agents=[], conflict_description="",
            resolution_strategy="", final_recommendation="", confidence=0.7
        )]

        confidence_with_conflicts = coordinator_agent._calculate_overall_confidence(sample_agent_responses, resolutions)
        assert confidence_with_conflicts < confidence  # Should be lower due to conflict penalty


class TestConflictResolver:
    """Test cases for ConflictResolver."""

    @pytest.fixture
    def conflict_resolver(self, mock_llm_client):
        """Create conflict resolver instance."""
        return ConflictResolver(mock_llm_client)

    @pytest.mark.asyncio
    async def test_detect_contradictory_recommendations(self, conflict_resolver, sample_agent_responses):
        """Test detection of contradictory recommendations."""
        # Create contradictory agent responses
        contradictory_responses = [
            AgentResponse(
                agent_name="Agent1", agent_type="test", results=[
                    AnalysisResult(
                        id="test1", type="action", title="Add Feature", description="Add this feature",
                        priority=PriorityLevel.HIGH, impact=ImpactLevel.HIGH, effort=EffortLevel.LOW,
                        recommendation="Add new schema markup", confidence=0.9
                    )
                ], confidence=0.9, processing_time=1.0, timestamp=datetime.utcnow()
            ),
            AgentResponse(
                agent_name="Agent2", agent_type="test", results=[
                    AnalysisResult(
                        id="test2", type="action", title="Remove Feature", description="Remove this feature",
                        priority=PriorityLevel.HIGH, impact=ImpactLevel.HIGH, effort=EffortLevel.LOW,
                        recommendation="Remove existing schema markup", confidence=0.8
                    )
                ], confidence=0.8, processing_time=1.2, timestamp=datetime.utcnow()
            )
        ]

        conflicts = await conflict_resolver.detect_conflicts(contradictory_responses)

        contradictory_conflicts = [c for c in conflicts if c["type"] == ConflictType.CONTRADICTORY_RECOMMENDATIONS]
        assert len(contradictory_conflicts) >= 1
        assert "Agent1" in contradictory_conflicts[0]["agents"]
        assert "Agent2" in contradictory_conflicts[0]["agents"]

    @pytest.mark.asyncio
    async def test_detect_overlapping_scope(self, conflict_resolver, sample_agent_responses):
        """Test detection of overlapping scope conflicts."""
        # Modify responses to have overlapping types
        for response in sample_agent_responses:
            for result in response.results:
                result.type = "schema_markup"  # Same type = overlap

        conflicts = await conflict_resolver.detect_conflicts(sample_agent_responses)

        overlapping_conflicts = [c for c in conflicts if c["type"] == ConflictType.OVERLAPPING_SCOPE]
        assert len(overlapping_conflicts) >= 1

    @pytest.mark.asyncio
    async def test_detect_priority_mismatches(self, conflict_resolver):
        """Test detection of priority mismatches."""
        responses = [
            AgentResponse(
                agent_name="Agent1", agent_type="test", results=[
                    AnalysisResult(
                        id="test1", type="schema", title="Similar Task", description="Similar description",
                        priority=PriorityLevel.HIGH, impact=ImpactLevel.HIGH, effort=EffortLevel.LOW,
                        recommendation="Similar recommendation", confidence=0.9
                    )
                ], confidence=0.9, processing_time=1.0, timestamp=datetime.utcnow()
            ),
            AgentResponse(
                agent_name="Agent2", agent_type="test", results=[
                    AnalysisResult(
                        id="test2", type="schema", title="Similar Task", description="Similar description",
                        priority=PriorityLevel.LOW, impact=ImpactLevel.HIGH, effort=EffortLevel.LOW,
                        recommendation="Similar recommendation", confidence=0.8
                    )
                ], confidence=0.8, processing_time=1.2, timestamp=datetime.utcnow()
            )
        ]

        conflicts = await conflict_resolver.detect_conflicts(responses)

        priority_conflicts = [c for c in conflicts if c["type"] == ConflictType.PRIORITY_MISMATCH]
        assert len(priority_conflicts) >= 1

    @pytest.mark.asyncio
    async def test_resolve_contradictory_recommendations(self, conflict_resolver, sample_website_data):
        """Test resolution of contradictory recommendations."""
        conflict = {
            "id": "test_conflict",
            "type": ConflictType.CONTRADICTORY_RECOMMENDATIONS,
            "agents": ["Agent1", "Agent2"],
            "results": [
                AnalysisResult(
                    id="test1", type="action", title="Add", description="Add feature",
                    priority=PriorityLevel.HIGH, impact=ImpactLevel.HIGH, effort=EffortLevel.LOW,
                    recommendation="Add schema", confidence=0.9
                ),
                AnalysisResult(
                    id="test2", type="action", title="Remove", description="Remove feature",
                    priority=PriorityLevel.HIGH, impact=ImpactLevel.HIGH, effort=EffortLevel.LOW,
                    recommendation="Remove schema", confidence=0.8
                )
            ]
        }

        resolution = await conflict_resolver._resolve_single_conflict(conflict, sample_website_data)

        assert resolution.conflict_id == "test_conflict"
        assert resolution.conflicting_agents == ["Agent1", "Agent2"]
        assert resolution.final_recommendation is not None
        assert resolution.confidence > 0

    @pytest.mark.asyncio
    async def test_resolve_priority_mismatch(self, conflict_resolver, sample_website_data):
        """Test resolution of priority mismatches."""
        conflict = {
            "id": "priority_conflict",
            "type": ConflictType.PRIORITY_MISMATCH,
            "agents": ["Agent1", "Agent2"],
            "results": [
                AnalysisResult(
                    id="test1", type="schema", title="Task", description="Description",
                    priority=PriorityLevel.HIGH, impact=ImpactLevel.HIGH, effort=EffortLevel.LOW,
                    recommendation="High priority recommendation", confidence=0.9
                ),
                AnalysisResult(
                    id="test2", type="schema", title="Task", description="Description",
                    priority=PriorityLevel.LOW, impact=ImpactLevel.HIGH, effort=EffortLevel.LOW,
                    recommendation="Low priority recommendation", confidence=0.8
                )
            ]
        }

        resolution = await conflict_resolver._resolve_single_conflict(conflict, sample_website_data)

        assert resolution.resolution_strategy == "Priority elevation"
        assert "high" in resolution.final_recommendation.lower()


class TestPrioritizer:
    """Test cases for Prioritizer."""

    @pytest.fixture
    def prioritizer(self, mock_llm_client):
        """Create prioritizer instance."""
        return Prioritizer(mock_llm_client)

    @pytest.mark.asyncio
    async def test_create_priority_matrix(self, prioritizer):
        """Test creation of priority matrix."""
        results = [
            AnalysisResult(
                id="high_impact_low_effort", type="test", title="Quick Win",
                description="Easy improvement", priority=PriorityLevel.HIGH,
                impact=ImpactLevel.HIGH, effort=EffortLevel.LOW,
                recommendation="Do this first", confidence=0.9
            ),
            AnalysisResult(
                id="low_impact_high_effort", type="test", title="Major Project",
                description="Complex improvement", priority=PriorityLevel.LOW,
                impact=ImpactLevel.LOW, effort=EffortLevel.HIGH,
                recommendation="Do this later", confidence=0.7
            )
        ]

        matrix = await prioritizer.create_priority_matrix(results)

        assert len(matrix.high_impact_low_effort) == 1
        assert len(matrix.low_impact_high_effort) == 1
        assert matrix.high_impact_low_effort[0].id == "high_impact_low_effort"

    @pytest.mark.asyncio
    async def test_create_implementation_plan(self, prioritizer, sample_website_data):
        """Test creation of implementation plan."""
        matrix = PriorityMatrix(
            high_impact_low_effort=[
                AnalysisResult(
                    id="quick_win", type="schema", title="Quick Schema Fix",
                    description="Easy schema improvement", priority=PriorityLevel.HIGH,
                    impact=ImpactLevel.HIGH, effort=EffortLevel.LOW,
                    recommendation="Add missing schema", confidence=0.9
                )
            ],
            high_impact_high_effort=[
                AnalysisResult(
                    id="major_project", type="redesign", title="Major Redesign",
                    description="Complex site improvement", priority=PriorityLevel.HIGH,
                    impact=ImpactLevel.HIGH, effort=EffortLevel.HIGH,
                    recommendation="Redesign website", confidence=0.8
                )
            ]
        )

        plan = await prioritizer.create_implementation_plan(matrix, sample_website_data)

        assert len(plan.phases) >= 2  # At least quick wins and major improvements
        assert "Quick Wins" in [phase["name"] for phase in plan.phases]
        assert plan.estimated_timeline is not None
        assert len(plan.resource_requirements) > 0

    def test_categorize_by_impact_effort(self, prioritizer):
        """Test categorization of results by impact and effort."""
        result = AnalysisResult(
            id="test", type="test", title="Test", description="Test",
            priority=PriorityLevel.HIGH, impact=ImpactLevel.HIGH, effort=EffortLevel.LOW,
            recommendation="Test", confidence=0.8
        )

        category = prioritizer._categorize_by_impact_effort(result)
        assert category == "high_impact_low_effort"

        # Test low impact, high effort
        result.impact = ImpactLevel.LOW
        result.effort = EffortLevel.HIGH
        category = prioritizer._categorize_by_impact_effort(result)
        assert category == "low_impact_high_effort"

    def test_sort_results(self, prioritizer):
        """Test sorting of results by priority and confidence."""
        results = [
            AnalysisResult(
                id="low_priority", type="test", title="Low", description="Low priority",
                priority=PriorityLevel.LOW, impact=ImpactLevel.LOW, effort=EffortLevel.LOW,
                recommendation="Low", confidence=0.6
            ),
            AnalysisResult(
                id="high_priority", type="test", title="High", description="High priority",
                priority=PriorityLevel.HIGH, impact=ImpactLevel.HIGH, effort=EffortLevel.LOW,
                recommendation="High", confidence=0.9
            )
        ]

        sorted_results = prioritizer._sort_results(results)

        assert sorted_results[0].id == "high_priority"  # High priority should be first
        assert sorted_results[1].id == "low_priority"