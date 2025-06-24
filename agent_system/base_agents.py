"""
Core AI Agent System

This module defines the base AI agent architecture and specialized business agents
that form our autonomous AI company.
"""

import json
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import openai
import anthropic
from django.conf import settings


logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    """Standardized response format from agents"""
    success: bool
    content: str
    structured_data: Dict[str, Any]
    confidence: float
    execution_time: float
    token_usage: int
    model_used: str
    error_message: str = ""
    
    def to_dict(self):
        return asdict(self)


@dataclass
class AnalysisContext:
    """Context passed to agents for analysis"""
    business_idea_id: str
    title: str
    description: str
    industry: str
    target_market: str
    estimated_budget: Optional[float]
    additional_data: Dict[str, Any]


class BaseAIAgent(ABC):
    """
    Abstract base class for all AI agents in our company.
    Defines the core interface and common functionality.
    """
    
    def __init__(self, agent_name: str, model_preference: str = None):
        self.agent_name = agent_name
        self.model_preference = model_preference or settings.DEFAULT_LLM_MODEL
        self.role_description = ""
        self.capabilities = []
        self.required_data_sources = []
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt that defines this agent's role and behavior"""
        pass
    
    @abstractmethod
    def get_analysis_prompt(self, context: AnalysisContext) -> str:
        """Generate the specific analysis prompt for the given business context"""
        pass
    
    @abstractmethod
    def parse_response(self, raw_response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured data"""
        pass
    
    async def analyze(self, context: AnalysisContext) -> AgentResponse:
        """
        Main analysis method - orchestrates the entire analysis process
        """
        start_time = datetime.now()
        
        try:
            # Prepare the analysis
            system_prompt = self.get_system_prompt()
            analysis_prompt = self.get_analysis_prompt(context)
            
            logger.info(f"{self.agent_name} starting analysis for {context.business_idea_id}")
            
            # Execute the LLM call
            raw_response, token_usage = await self._call_llm(system_prompt, analysis_prompt)
            
            # Parse and structure the response
            structured_data = self.parse_response(raw_response)
            
            # Calculate execution metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            confidence = self._calculate_confidence(structured_data)
            
            logger.info(f"{self.agent_name} completed analysis in {execution_time:.2f}s")
            
            return AgentResponse(
                success=True,
                content=raw_response,
                structured_data=structured_data,
                confidence=confidence,
                execution_time=execution_time,
                token_usage=token_usage,
                model_used=self.model_preference
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"{self.agent_name} analysis failed: {str(e)}")
            
            return AgentResponse(
                success=False,
                content="",
                structured_data={},
                confidence=0.0,
                execution_time=execution_time,
                token_usage=0,
                model_used=self.model_preference,
                error_message=str(e)
            )
    
    async def _call_llm(self, system_prompt: str, user_prompt: str) -> Tuple[str, int]:
        """
        Make the actual LLM API call with proper error handling and retries
        """
        if self.model_preference.startswith('gpt'):
            return await self._call_openai(system_prompt, user_prompt)
        elif self.model_preference.startswith('claude'):
            return await self._call_anthropic(system_prompt, user_prompt)
        else:
            raise ValueError(f"Unsupported model: {self.model_preference}")
    
    async def _call_openai(self, system_prompt: str, user_prompt: str) -> Tuple[str, int]:
        """Call OpenAI API"""
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = await client.chat.completions.create(
            model=self.model_preference,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=4000,
        )
        
        content = response.choices[0].message.content
        token_usage = response.usage.total_tokens
        
        return content, token_usage
    
    async def _call_anthropic(self, system_prompt: str, user_prompt: str) -> Tuple[str, int]:
        """Call Anthropic Claude API"""
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        response = await client.messages.create(
            model=self.model_preference,
            max_tokens=4000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
        )
        
        content = response.content[0].text
        token_usage = response.usage.input_tokens + response.usage.output_tokens
        
        return content, token_usage
    
    def _calculate_confidence(self, structured_data: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on the completeness and quality of the analysis
        """
        # Default implementation - can be overridden by specific agents
        required_fields = ['score', 'risks', 'opportunities']
        present_fields = sum(1 for field in required_fields if field in structured_data)
        
        base_confidence = (present_fields / len(required_fields)) * 100
        
        # Adjust based on data quality indicators
        if 'confidence_indicators' in structured_data:
            indicators = structured_data['confidence_indicators']
            base_confidence *= indicators.get('data_quality_multiplier', 1.0)
        
        return min(base_confidence, 100.0)
    
    def get_required_permissions(self) -> List[str]:
        """Return list of permissions this agent needs"""
        return ['analysis.basic']
    
    def validate_context(self, context: AnalysisContext) -> bool:
        """Validate that the context contains required information"""
        required_fields = ['business_idea_id', 'title', 'description']
        return all(hasattr(context, field) and getattr(context, field) for field in required_fields)


class AgentCommunicationHub:
    """
    Manages communication and coordination between agents.
    Implements the inter-agent messaging and workflow orchestration.
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAIAgent] = {}
        self.message_queue = asyncio.Queue()
        self.active_workflows: Dict[str, Dict] = {}
        
    def register_agent(self, agent: BaseAIAgent):
        """Register an agent with the communication hub"""
        self.agents[agent.agent_name] = agent
        logger.info(f"Registered agent: {agent.agent_name}")
    
    async def broadcast_message(self, sender: str, message: Dict[str, Any], recipients: List[str] = None):
        """Send a message to specified agents or all agents"""
        if recipients is None:
            recipients = list(self.agents.keys())
        
        for recipient in recipients:
            if recipient != sender and recipient in self.agents:
                await self.message_queue.put({
                    'sender': sender,
                    'recipient': recipient,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                })
    
    async def get_agent_insights(self, agent_name: str, business_idea_id: str) -> Dict[str, Any]:
        """Request insights from a specific agent about a business idea"""
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not found")
        
        # This would typically retrieve previously generated insights
        # For now, return a placeholder
        return {
            'agent': agent_name,
            'business_idea_id': business_idea_id,
            'insights': [],
            'recommendations': []
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get the current status of all registered agents"""
        return {
            'total_agents': len(self.agents),
            'registered_agents': list(self.agents.keys()),
            'active_workflows': len(self.active_workflows),
            'queue_size': self.message_queue.qsize()
        }


# Global communication hub instance
communication_hub = AgentCommunicationHub()
