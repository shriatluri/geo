"""
Main Orchestration for GEO Platform Agents.
Coordinates the new modular architecture with LLM integration.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
import logging

from .shared.llm_client import LLMClient
from .shared.client_input_processor import ClientInputProcessor
from .shared.crawler_adapter import CrawlerAdapter
from .shared.models import WebsiteData, AgentResponse, ClientRequirements

from .aeo_agent.agent import AEOAgent
from .geo_agent.agent import GEOAgent
from .geo_plus_agent.agent import GEOPlusAgent
from .coordinator_agent.agent import CoordinatorAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GEOPlatformOrchestrator:
    """
    Main orchestrator for the GEO platform using the new modular architecture.
    
    Coordinates:
    - Client input processing
    - Website data collection  
    - Agent execution (AEO, GEO, GEO+)
    - Result coordination and delivery
    """
    
    def __init__(self):
        # Initialize LLM client
        self.llm_client = LLMClient()
        
        # Initialize components
        self.client_processor = ClientInputProcessor(self.llm_client)
        self.crawler_adapter = CrawlerAdapter()
        
        # Initialize agents with LLM client
        self.aeo_agent = AEOAgent(self.llm_client)
        self.geo_agent = GEOAgent(self.llm_client) 
        self.geo_plus_agent = GEOPlusAgent(self.llm_client)
        self.coordinator = CoordinatorAgent(self.llm_client)
        
        logger.info("GEO Platform Orchestrator initialized with new architecture")
    
    async def process_client_request(self, raw_client_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a complete client request from input to delivery.
        
        Args:
            raw_client_input: Raw client input data
            
        Returns:
            Complete analysis results and recommendations
        """
        start_time = time.time()
        logger.info("Starting client request processing")
        
        try:
            # 1. Process client input
            logger.info("Processing client input...")
            client_requirements = await self.client_processor.process_client_input(raw_client_input)
            
            # 2. Collect website data
            logger.info(f"Collecting website data for {client_requirements.website_url}")
            website_data = await self.crawler_adapter.fetch_website_data(client_requirements.website_url)
            
            # 3. Enhance client requirements with website analysis
            logger.info("Enhancing client requirements with website analysis...")
            enhanced_requirements = await self.client_processor.enhance_with_website_analysis(
                client_requirements, website_data
            )
            
            # 4. Execute agents based on services needed
            agent_results = await self._execute_agents(enhanced_requirements, website_data)
            
            # 5. Coordinate and prioritize results
            logger.info("Coordinating results...")
            coordinated_results = await self.coordinator.coordinate_agents(agent_results, enhanced_requirements)
            
            # 6. Prepare final response
            processing_time = time.time() - start_time
            final_response = self._prepare_final_response(
                enhanced_requirements, 
                agent_results, 
                coordinated_results, 
                processing_time
            )
            
            logger.info(f"Client request processed successfully in {processing_time:.2f}s")
            return final_response
            
        except Exception as e:
            logger.error(f"Error processing client request: {str(e)}")
            processing_time = time.time() - start_time
            return self._create_error_response(str(e), processing_time)
    
    async def _execute_agents(self, requirements: ClientRequirements, website_data: WebsiteData) -> Dict[str, AgentResponse]:
        """Execute agents based on services needed."""
        results = {}
        services = requirements.services_needed
        
        # Execute agents concurrently for better performance
        tasks = []
        
        if any(service in services for service in ["aeo", "visibility", "schema_markup"]):
            logger.info("Executing AEO Agent...")
            tasks.append(("aeo", self.aeo_agent.analyze(website_data)))
        
        if any(service in services for service in ["geo", "accuracy", "business_info"]):
            logger.info("Executing GEO Agent...")
            tasks.append(("geo", self.geo_agent.analyze(website_data)))
        
        if any(service in services for service in ["geo_plus", "actionability", "implementation"]):
            logger.info("Executing GEO+ Agent...")
            tasks.append(("geo_plus", self.geo_plus_agent.analyze(website_data)))
        
        # Wait for all agents to complete
        if tasks:
            completed_tasks = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
            
            for i, result in enumerate(completed_tasks):
                agent_name = tasks[i][0]
                if isinstance(result, Exception):
                    logger.error(f"{agent_name} agent failed: {str(result)}")
                    results[agent_name] = self._create_agent_error_response(agent_name, str(result))
                else:
                    results[agent_name] = result
                    logger.info(f"{agent_name} agent completed successfully")
        
        return results
    
    def _prepare_final_response(
        self, 
        requirements: ClientRequirements, 
        agent_results: Dict[str, AgentResponse], 
        coordinated_results: Dict[str, Any], 
        processing_time: float
    ) -> Dict[str, Any]:
        """Prepare the final response for the client."""
        return {
            "status": "success",
            "client_requirements": {
                "website_url": requirements.website_url,
                "services_requested": requirements.services_needed,
                "priority": requirements.priority,
                "timeline": requirements.timeline
            },
            "agent_results": {
                agent_name: {
                    "agent_type": result.agent_type,
                    "confidence": result.confidence,
                    "results_count": len(result.results),
                    "processing_time": result.processing_time,
                    "results": [
                        {
                            "id": r.id,
                            "type": r.type,
                            "title": r.title,
                            "description": r.description,
                            "priority": r.priority,
                            "impact": r.impact,
                            "effort": r.effort,
                            "recommendation": r.recommendation,
                            "confidence": r.confidence
                        } for r in result.results
                    ]
                } for agent_name, result in agent_results.items()
            },
            "coordinated_recommendations": coordinated_results,
            "metadata": {
                "processing_time": processing_time,
                "agents_executed": list(agent_results.keys()),
                "llm_enhanced": True,
                "architecture_version": "2.0_modular"
            }
        }
    
    def _create_error_response(self, error_message: str, processing_time: float) -> Dict[str, Any]:
        """Create error response."""
        return {
            "status": "error",
            "error": error_message,
            "metadata": {
                "processing_time": processing_time,
                "architecture_version": "2.0_modular"
            }
        }
    
    def _create_agent_error_response(self, agent_name: str, error_message: str) -> AgentResponse:
        """Create error response for failed agent."""
        from .shared.models import AnalysisResult, PriorityLevel, ImpactLevel, EffortLevel
        
        error_result = AnalysisResult(
            id=f"{agent_name}_error",
            type="error",
            title=f"{agent_name.upper()} Agent Error",
            description=f"Error in {agent_name} agent: {error_message}",
            priority=PriorityLevel.LOW,
            impact=ImpactLevel.LOW,
            effort=EffortLevel.LOW,
            recommendation="Review error and retry analysis",
            confidence=0.0
        )
        
        return AgentResponse(
            agent_type=agent_name,
            results=[error_result],
            confidence=0.0,
            processing_time=0.0,
            metadata={"error": error_message}
        )


async def demo_client_request():
    """Demonstrate the new orchestration with a sample client request."""
    # Sample client input
    sample_input = {
        "website_url": "https://purdueagr.com",
        "business_info": {
            "name": "Purdue Agricultural Innovation Foundation",
            "services": ["Agricultural Innovation", "Research Programs"]
        },
        "services": ["visibility", "accuracy"],
        "priority": "high",
        "timeline": "2_weeks",
        "platform_access": {
            "squarespace_access": True
        }
    }
    
    # Process with orchestrator
    orchestrator = GEOPlatformOrchestrator()
    result = await orchestrator.process_client_request(sample_input)
    
    print("=== GEO Platform Results ===")
    print(f"Status: {result['status']}")
    print(f"Processing Time: {result['metadata']['processing_time']:.2f}s")
    print(f"Agents Executed: {result['metadata']['agents_executed']}")
    
    if result['status'] == 'success':
        for agent_name, agent_result in result['agent_results'].items():
            print(f"\n{agent_name.upper()} Agent:")
            print(f"  Confidence: {agent_result['confidence']:.2f}")
            print(f"  Results: {agent_result['results_count']}")
            
            for r in agent_result['results'][:2]:  # Show first 2 results
                print(f"    - {r['title']}: {r['description'][:100]}...")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_client_request())
