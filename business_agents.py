import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging
from django.conf import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LMStudioAgent:
    """Base class for LM Studio agents with local LLM integration"""
    
    def __init__(self, 
                 base_url: str = "http://localhost:1234/v1",
                 model: str = "local-model",
                 temperature: float = 0.7,
                 max_tokens: int = 2048,
                 timeout: int = 30):
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.conversation_history = []
        
    def _make_request(self, messages: List[Dict]) -> Optional[str]:
        """Make request to LM Studio API"""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error making request to LM Studio: {str(e)}")
            return None
    
    def chat(self, message: str, system_prompt: str = None) -> str:
        """Send a message and get response"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add new user message
        messages.append({"role": "user", "content": message})
        
        response = self._make_request(messages)
        
        if response:
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # Keep history manageable (last 10 exchanges)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
        
        return response or "I'm sorry, I encountered an error processing your request."
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

class ConfigurableAgent(LMStudioAgent):
    """Agent that uses AgentConfiguration from the database"""
    
    def __init__(self, config):
        """Initialize agent with configuration object"""
        # Extract LLM configuration from the related provider
        llm_provider = config.llm_provider
        
        super().__init__(
            base_url=llm_provider.api_endpoint,
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.timeout_seconds
        )
        
        self.config = config
        self.enabled_tools = config.capabilities  # Using capabilities as tools for now
        
        # Get system prompt from prompt templates
        system_prompt_template = config.prompt_templates.filter(
            prompt_type='system', 
            is_active=True
        ).first()
        
        self.system_prompt = system_prompt_template.template if system_prompt_template else (
            f"You are {config.name}. {config.description}"
        )
        
    def execute(self, user_input: str, context: Dict = None) -> str:
        """Execute agent with given input and optional context"""
        try:
            # Prepare the prompt with context if provided
            enhanced_prompt = self.system_prompt
            if context:
                enhanced_prompt += f"\n\nAdditional Context: {json.dumps(context, indent=2)}"
            
            response = self.chat(user_input, enhanced_prompt)
            
            # Log the interaction
            logger.info(f"Agent {self.config.name} processed request: {user_input[:100]}...")
            
            return response
            
        except Exception as e:
            logger.error(f"Error executing agent {self.config.name}: {str(e)}")
            return f"I encountered an error: {str(e)}"
    
    def get_capabilities(self) -> Dict:
        """Return agent capabilities"""
        return {
            'name': self.config.name,
            'type': self.config.agent_type,
            'description': self.config.description,
            'capabilities': self.config.capabilities,
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'status': self.config.status
        }