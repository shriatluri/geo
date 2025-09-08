"""
Base agent interface for all GEO platform agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging
from datetime import datetime

from .models import WebsiteData, AgentResponse, AnalysisResult
from .llm_client import LLMClient


class BaseAgent(ABC):
    """
    Abstract base class for all GEO platform agents.
    """
    
    def __init__(self, name: str, llm_client: LLMClient):
        self.name = name
        self.llm_client = llm_client
        self.logger = logging.getLogger(f"geo.{name}")
        
    @abstractmethod
    async def analyze(self, website_data: WebsiteData) -> AgentResponse:
        """
        Analyze website data and return recommendations.
        
        Args:
            website_data: Website data to analyze
            
        Returns:
            AgentResponse with analysis results and recommendations
        """
        pass
    
    @abstractmethod
    def get_agent_type(self) -> str:
        """
        Get the type of this agent.
        
        Returns:
            String identifier for the agent type
        """
        pass
    
    def _create_response(
        self,
        results: List[AnalysisResult],
        confidence: float,
        processing_time: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Create a standardized agent response.
        
        Args:
            results: List of analysis results
            confidence: Confidence score (0-1)
            processing_time: Time taken to process in seconds
            metadata: Additional metadata
            
        Returns:
            Standardized AgentResponse
        """
        return AgentResponse(
            agent_name=self.name,
            agent_type=self.get_agent_type(),
            results=results,
            confidence=confidence,
            processing_time=processing_time,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
    
    def _log_analysis_start(self, url: str) -> None:
        """Log the start of analysis."""
        self.logger.info(f"Starting {self.name} analysis for {url}")
    
    def _log_analysis_complete(self, url: str, results_count: int, confidence: float) -> None:
        """Log the completion of analysis."""
        self.logger.info(
            f"Completed {self.name} analysis for {url}: "
            f"{results_count} results, confidence: {confidence:.2f}"
        )
    
    def _log_error(self, error: Exception, context: str = "") -> None:
        """Log an error with context."""
        self.logger.error(f"{self.name} error {context}: {str(error)}", exc_info=True)
