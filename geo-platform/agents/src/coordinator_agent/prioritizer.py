"""
Impact/effort matrix for coordinator agent.
Creates priority matrices and implementation plans for coordinated recommendations.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from ..shared.models import (
    AnalysisResult, PriorityMatrix, ImplementationPlan, WebsiteData,
    PriorityLevel, ImpactLevel, EffortLevel
)
from ..shared.llm_client import LLMClient


class Prioritizer:
    """
    Creates priority matrices and implementation plans for recommendations.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.impact_weights = self._initialize_impact_weights()
        self.effort_weights = self._initialize_effort_weights()

    async def create_priority_matrix(self, results: List[AnalysisResult]) -> PriorityMatrix:
        """
        Create a priority matrix categorizing results by impact and effort.

        Args:
            results: List of analysis results to prioritize

        Returns:
            PriorityMatrix with categorized recommendations
        """
        matrix = PriorityMatrix()

        for result in results:
            category = self._categorize_by_impact_effort(result)

            if category == "high_impact_low_effort":
                matrix.high_impact_low_effort.append(result)
            elif category == "high_impact_high_effort":
                matrix.high_impact_high_effort.append(result)
            elif category == "low_impact_low_effort":
                matrix.low_impact_low_effort.append(result)
            elif category == "low_impact_high_effort":
                matrix.low_impact_high_effort.append(result)

        # Sort each category by priority and confidence
        matrix.high_impact_low_effort = self._sort_results(matrix.high_impact_low_effort)
        matrix.high_impact_high_effort = self._sort_results(matrix.high_impact_high_effort)
        matrix.low_impact_low_effort = self._sort_results(matrix.low_impact_low_effort)
        matrix.low_impact_high_effort = self._sort_results(matrix.low_impact_high_effort)

        return matrix

    async def create_implementation_plan(self, priority_matrix: PriorityMatrix, website_data: WebsiteData) -> ImplementationPlan:
        """
        Create a phased implementation plan based on the priority matrix.

        Args:
            priority_matrix: Priority matrix with categorized recommendations
            website_data: Website context for planning

        Returns:
            ImplementationPlan with phased approach
        """
        phases = []
        current_date = datetime.now()

        # Phase 1: Quick Wins (High Impact, Low Effort)
        if priority_matrix.high_impact_low_effort:
            phase1 = self._create_phase(
                "Quick Wins",
                priority_matrix.high_impact_low_effort,
                current_date,
                "1-2 weeks",
                "Immediate impact with minimal effort"
            )
            phases.append(phase1)
            current_date += timedelta(weeks=2)

        # Phase 2: Critical Improvements (High Impact, High Effort)
        if priority_matrix.high_impact_high_effort:
            phase2 = self._create_phase(
                "Critical Improvements",
                priority_matrix.high_impact_high_effort,
                current_date,
                "4-8 weeks",
                "Major improvements requiring significant effort"
            )
            phases.append(phase2)
            current_date += timedelta(weeks=6)

        # Phase 3: Easy Maintenance (Low Impact, Low Effort)
        if priority_matrix.low_impact_low_effort:
            phase3 = self._create_phase(
                "Maintenance Tasks",
                priority_matrix.low_impact_low_effort,
                current_date,
                "2-4 weeks",
                "Low-effort maintenance and optimization"
            )
            phases.append(phase3)
            current_date += timedelta(weeks=3)

        # Phase 4: Future Considerations (Low Impact, High Effort) - only if resources allow
        if priority_matrix.low_impact_high_effort:
            phase4 = self._create_phase(
                "Future Considerations",
                priority_matrix.low_impact_high_effort[:3],  # Limit to top 3
                current_date,
                "8+ weeks",
                "Future improvements when resources are available"
            )
            phases.append(phase4)

        # Calculate overall timeline and resources
        total_weeks = sum(self._estimate_phase_duration(phase) for phase in phases)
        estimated_timeline = f"{total_weeks} weeks total"

        # Gather resource requirements
        all_results = (priority_matrix.high_impact_low_effort +
                      priority_matrix.high_impact_high_effort +
                      priority_matrix.low_impact_low_effort +
                      priority_matrix.low_impact_high_effort)

        resource_requirements = self._calculate_resource_requirements(all_results)
        dependencies = self._identify_dependencies(all_results)
        success_metrics = self._define_success_metrics(all_results, website_data)

        return ImplementationPlan(
            phases=phases,
            estimated_timeline=estimated_timeline,
            resource_requirements=resource_requirements,
            dependencies=dependencies,
            success_metrics=success_metrics
        )

    def _categorize_by_impact_effort(self, result: AnalysisResult) -> str:
        """
        Categorize a result by its impact and effort levels.
        """
        is_high_impact = result.impact in [ImpactLevel.HIGH, ImpactLevel.CRITICAL]
        is_low_effort = result.effort in [EffortLevel.LOW, EffortLevel.MEDIUM]

        if is_high_impact and is_low_effort:
            return "high_impact_low_effort"
        elif is_high_impact and not is_low_effort:
            return "high_impact_high_effort"
        elif not is_high_impact and is_low_effort:
            return "low_impact_low_effort"
        else:
            return "low_impact_high_effort"

    def _sort_results(self, results: List[AnalysisResult]) -> List[AnalysisResult]:
        """
        Sort results by priority, then by confidence.
        """
        priority_order = {
            PriorityLevel.CRITICAL: 4,
            PriorityLevel.HIGH: 3,
            PriorityLevel.MEDIUM: 2,
            PriorityLevel.LOW: 1
        }

        return sorted(results, key=lambda r: (
            priority_order.get(r.priority, 0),
            r.confidence
        ), reverse=True)

    def _create_phase(self, name: str, results: List[AnalysisResult], start_date: datetime,
                     duration: str, description: str) -> Dict[str, Any]:
        """
        Create a phase dictionary for the implementation plan.
        """
        return {
            "name": name,
            "description": description,
            "duration": duration,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "recommendations": [{
                "id": result.id,
                "title": result.title,
                "priority": result.priority,
                "effort": result.effort,
                "implementation_steps": result.implementation_steps[:3]  # Limit to top 3 steps
            } for result in results],
            "effort_estimate": self._calculate_phase_effort(results),
            "expected_outcomes": [result.recommendation for result in results[:3]]  # Top 3 outcomes
        }

    def _estimate_phase_duration(self, phase: Dict[str, Any]) -> int:
        """
        Estimate phase duration in weeks.
        """
        duration_map = {
            "1-2 weeks": 2,
            "4-8 weeks": 6,
            "2-4 weeks": 3,
            "8+ weeks": 10
        }
        return duration_map.get(phase["duration"], 4)

    def _calculate_phase_effort(self, results: List[AnalysisResult]) -> str:
        """
        Calculate total effort for a phase.
        """
        effort_scores = {
            EffortLevel.LOW: 1,
            EffortLevel.MEDIUM: 2,
            EffortLevel.HIGH: 3,
            EffortLevel.VERY_HIGH: 4
        }

        total_effort = sum(effort_scores.get(result.effort, 2) for result in results)
        avg_effort = total_effort / len(results) if results else 0

        if avg_effort <= 1.5:
            return "Low"
        elif avg_effort <= 2.5:
            return "Medium"
        elif avg_effort <= 3.5:
            return "High"
        else:
            return "Very High"

    def _calculate_resource_requirements(self, results: List[AnalysisResult]) -> List[str]:
        """
        Calculate resource requirements based on analysis results.
        """
        resources = set()

        for result in results:
            # Analyze result types to determine resources needed
            if "technical" in result.type.lower() or "schema" in result.type.lower():
                resources.add("Technical Developer")
            if "content" in result.type.lower() or "copywriting" in result.type.lower():
                resources.add("Content Creator")
            if "design" in result.type.lower() or "ui" in result.type.lower():
                resources.add("UI/UX Designer")
            if "seo" in result.type.lower() or "optimization" in result.type.lower():
                resources.add("SEO Specialist")
            if "business" in result.type.lower() or "strategy" in result.type.lower():
                resources.add("Business Analyst")

        # Add default resources if none identified
        if not resources:
            resources.add("Web Developer")
            resources.add("Project Manager")

        return sorted(list(resources))

    def _identify_dependencies(self, results: List[AnalysisResult]) -> List[str]:
        """
        Identify dependencies between recommendations.
        """
        dependencies = []

        # Look for common dependency patterns
        has_schema = any("schema" in result.type.lower() for result in results)
        has_technical = any("technical" in result.type.lower() for result in results)
        has_content = any("content" in result.type.lower() for result in results)

        if has_schema and has_content:
            dependencies.append("Content creation must precede schema implementation")

        if has_technical:
            dependencies.append("Technical infrastructure must be stable before optimization")

        # Look for sequential implementation needs
        for result in results:
            if "foundation" in result.title.lower() or "basic" in result.title.lower():
                dependencies.append(f"Complete '{result.title}' before advanced optimizations")

        return dependencies if dependencies else ["No major dependencies identified"]

    def _define_success_metrics(self, results: List[AnalysisResult], website_data: WebsiteData) -> List[str]:
        """
        Define success metrics for the implementation plan.
        """
        metrics = set()

        # Add metrics based on result types
        result_types = [result.type.lower() for result in results]

        if any("seo" in t or "schema" in t for t in result_types):
            metrics.add("Search engine ranking improvements")
            metrics.add("Rich snippet appearance in search results")

        if any("performance" in t or "speed" in t for t in result_types):
            metrics.add("Page load speed improvements")
            metrics.add("Core Web Vitals scores")

        if any("content" in t or "user" in t for t in result_types):
            metrics.add("User engagement metrics (time on page, bounce rate)")
            metrics.add("Conversion rate improvements")

        if any("business" in t or "accuracy" in t for t in result_types):
            metrics.add("Business information accuracy score")
            metrics.add("Local search visibility")

        if any("accessibility" in t for t in result_types):
            metrics.add("Accessibility compliance score")
            metrics.add("User experience improvements")

        # Add default metrics if none identified
        if not metrics:
            metrics.add("Overall website quality score")
            metrics.add("Implementation completion rate")

        return sorted(list(metrics))

    def _initialize_impact_weights(self) -> Dict[ImpactLevel, float]:
        """
        Initialize impact level weights for calculations.
        """
        return {
            ImpactLevel.LOW: 0.25,
            ImpactLevel.MEDIUM: 0.5,
            ImpactLevel.HIGH: 0.75,
            ImpactLevel.CRITICAL: 1.0
        }

    def _initialize_effort_weights(self) -> Dict[EffortLevel, float]:
        """
        Initialize effort level weights for calculations.
        """
        return {
            EffortLevel.LOW: 0.25,
            EffortLevel.MEDIUM: 0.5,
            EffortLevel.HIGH: 0.75,
            EffortLevel.VERY_HIGH: 1.0
        }
