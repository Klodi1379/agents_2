"""
LM Studio Integration Service

This module provides integration with LM Studio for local LLM inference,
along with support for other local and cloud-based LLM providers.
"""

import aiohttp
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from django.conf import settings
import openai
import anthropic


logger = logging.getLogger(__name__)


class LLMProviderError(Exception):
    """Custom exception for LLM provider errors"""
    pass


class LLMRequest:
    """Standardized LLM request format"""
    def __init__(self, system_prompt: str, user_prompt: str, **kwargs):
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 4000)
        self.top_p = kwargs.get('top_p', 1.0)
        self.frequency_penalty = kwargs.get('frequency_penalty', 0.0)
        self.presence_penalty = kwargs.get('presence_penalty', 0.0)
        self.timeout = kwargs.get('timeout', 30)


class LLMResponse:
    """Standardized LLM response format"""
    def __init__(self, content: str, token_usage: int, model_used: str, 
                 execution_time: float, cost_estimate: float = 0.0):
        self.content = content
        self.token_usage = token_usage
        self.model_used = model_used
        self.execution_time = execution_time
        self.cost_estimate = cost_estimate
        self.timestamp = datetime.now()


class BaseLLMProvider:
    """Base class for all LLM providers"""
    
    def __init__(self, name: str, api_endpoint: str, api_key: str = None, **config):
        self.name = name
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.config = config
        self.is_available = False
    
    async def test_connection(self) -> bool:
        """Test if the provider is available"""
        try:
            response = await self.generate("Test", "Hello", max_tokens=10)
            self.is_available = True
            return True
        except Exception as e:
            logger.warning(f"Provider {self.name} connection test failed: {e}")
            self.is_available = False
            return False
    
    async def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> LLMResponse:
        """Generate response from the LLM"""
        raise NotImplementedError("Subclasses must implement generate method")
    
    def calculate_cost(self, token_usage: int, cost_per_1k_tokens: float) -> float:
        """Calculate cost based on token usage"""
        return (token_usage / 1000) * cost_per_1k_tokens


class LMStudioProvider(BaseLLMProvider):
    """LM Studio local LLM provider"""
    
    def __init__(self, name: str = "LM Studio", api_endpoint: str = "http://localhost:1234", **config):
        super().__init__(name, api_endpoint, **config)
        self.default_model = config.get('default_model', 'local-model')
    
    async def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> LLMResponse:
        """Generate response using LM Studio API"""
        start_time = datetime.now()
        
        request_data = {
            "model": kwargs.get('model', self.default_model),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": kwargs.get('temperature', 0.7),
            "max_tokens": kwargs.get('max_tokens', 4000),
            "top_p": kwargs.get('top_p', 1.0),
            "frequency_penalty": kwargs.get('frequency_penalty', 0.0),
            "presence_penalty": kwargs.get('presence_penalty', 0.0),
            "stream": False
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=kwargs.get('timeout', 30))
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.api_endpoint}/v1/chat/completions",
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise LLMProviderError(f"LM Studio API error {response.status}: {error_text}")
                    
                    result = await response.json()
                    
                    # Extract response data
                    content = result['choices'][0]['message']['content']
                    token_usage = result.get('usage', {}).get('total_tokens', 0)
                    model_used = result.get('model', self.default_model)
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    return LLMResponse(
                        content=content,
                        token_usage=token_usage,
                        model_used=model_used,
                        execution_time=execution_time,
                        cost_estimate=0.0  # Local models are free
                    )
                    
        except aiohttp.ClientError as e:
            raise LLMProviderError(f"LM Studio connection error: {e}")
        except Exception as e:
            raise LLMProviderError(f"LM Studio error: {e}")


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider"""
    
    def __init__(self, name: str = "Ollama", api_endpoint: str = "http://localhost:11434", **config):
        super().__init__(name, api_endpoint, **config)
        self.default_model = config.get('default_model', 'llama2')
    
    async def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> LLMResponse:
        """Generate response using Ollama API"""
        start_time = datetime.now()
        
        # Combine system and user prompts for Ollama
        combined_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"
        
        request_data = {
            "model": kwargs.get('model', self.default_model),
            "prompt": combined_prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get('temperature', 0.7),
                "num_predict": kwargs.get('max_tokens', 4000),
                "top_p": kwargs.get('top_p', 1.0),
            }
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=kwargs.get('timeout', 30))
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.api_endpoint}/api/generate",
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise LLMProviderError(f"Ollama API error {response.status}: {error_text}")
                    
                    result = await response.json()
                    
                    content = result.get('response', '')
                    # Ollama doesn't provide token count, estimate based on characters
                    token_usage = len(content.split()) * 1.3  # Rough estimation
                    model_used = result.get('model', self.default_model)
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    return LLMResponse(
                        content=content,
                        token_usage=int(token_usage),
                        model_used=model_used,
                        execution_time=execution_time,
                        cost_estimate=0.0  # Local models are free
                    )
                    
        except aiohttp.ClientError as e:
            raise LLMProviderError(f"Ollama connection error: {e}")
        except Exception as e:
            raise LLMProviderError(f"Ollama error: {e}")


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, name: str = "OpenAI", api_key: str = None, **config):
        super().__init__(name, "https://api.openai.com", api_key, **config)
        self.default_model = config.get('default_model', 'gpt-4-turbo-preview')
        self.cost_per_1k_tokens = config.get('cost_per_1k_tokens', 0.03)
    
    async def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> LLMResponse:
        """Generate response using OpenAI API"""
        start_time = datetime.now()
        
        try:
            client = openai.AsyncOpenAI(api_key=self.api_key)
            
            response = await client.chat.completions.create(
                model=kwargs.get('model', self.default_model),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 4000),
                top_p=kwargs.get('top_p', 1.0),
                frequency_penalty=kwargs.get('frequency_penalty', 0.0),
                presence_penalty=kwargs.get('presence_penalty', 0.0),
            )
            
            content = response.choices[0].message.content
            token_usage = response.usage.total_tokens
            model_used = response.model
            execution_time = (datetime.now() - start_time).total_seconds()
            cost_estimate = self.calculate_cost(token_usage, self.cost_per_1k_tokens)
            
            return LLMResponse(
                content=content,
                token_usage=token_usage,
                model_used=model_used,
                execution_time=execution_time,
                cost_estimate=cost_estimate
            )
            
        except Exception as e:
            raise LLMProviderError(f"OpenAI error: {e}")


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider"""
    
    def __init__(self, name: str = "Anthropic", api_key: str = None, **config):
        super().__init__(name, "https://api.anthropic.com", api_key, **config)
        self.default_model = config.get('default_model', 'claude-3-sonnet-20240229')
        self.cost_per_1k_tokens = config.get('cost_per_1k_tokens', 0.015)
    
    async def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> LLMResponse:
        """Generate response using Anthropic API"""
        start_time = datetime.now()
        
        try:
            client = anthropic.AsyncAnthropic(api_key=self.api_key)
            
            response = await client.messages.create(
                model=kwargs.get('model', self.default_model),
                max_tokens=kwargs.get('max_tokens', 4000),
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                temperature=kwargs.get('temperature', 0.7),
            )
            
            content = response.content[0].text
            token_usage = response.usage.input_tokens + response.usage.output_tokens
            model_used = response.model
            execution_time = (datetime.now() - start_time).total_seconds()
            cost_estimate = self.calculate_cost(token_usage, self.cost_per_1k_tokens)
            
            return LLMResponse(
                content=content,
                token_usage=token_usage,
                model_used=model_used,
                execution_time=execution_time,
                cost_estimate=cost_estimate
            )
            
        except Exception as e:
            raise LLMProviderError(f"Anthropic error: {e}")


class LLMProviderManager:
    """Manages multiple LLM providers and routing"""
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.default_provider = None
    
    def register_provider(self, provider: BaseLLMProvider, is_default: bool = False):
        """Register a new LLM provider"""
        self.providers[provider.name] = provider
        if is_default or not self.default_provider:
            self.default_provider = provider.name
        logger.info(f"Registered LLM provider: {provider.name}")
    
    async def test_all_providers(self) -> Dict[str, bool]:
        """Test all registered providers"""
        results = {}
        for name, provider in self.providers.items():
            results[name] = await provider.test_connection()
        return results
    
    async def generate(self, provider_name: str = None, system_prompt: str = "",
                      user_prompt: str = "", **kwargs) -> LLMResponse:
        """Generate response using specified or default provider"""
        
        provider_name = provider_name or self.default_provider
        
        if provider_name not in self.providers:
            raise LLMProviderError(f"Provider {provider_name} not found")
        
        provider = self.providers[provider_name]
        
        if not provider.is_available:
            # Try to reconnect
            await provider.test_connection()
            if not provider.is_available:
                raise LLMProviderError(f"Provider {provider_name} is not available")
        
        return await provider.generate(system_prompt, user_prompt, **kwargs)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return [name for name, provider in self.providers.items() if provider.is_available]
    
    def get_provider_info(self, provider_name: str) -> Dict[str, Any]:
        """Get information about a specific provider"""
        if provider_name not in self.providers:
            return {}
        
        provider = self.providers[provider_name]
        return {
            'name': provider.name,
            'endpoint': provider.api_endpoint,
            'is_available': provider.is_available,
            'config': provider.config
        }


# Global LLM provider manager
llm_manager = LLMProviderManager()


async def initialize_llm_providers():
    """Initialize all LLM providers based on configuration"""
    
    # Initialize LM Studio (local)
    lm_studio = LMStudioProvider(
        api_endpoint=getattr(settings, 'LM_STUDIO_ENDPOINT', 'http://localhost:1234'),
        default_model=getattr(settings, 'LM_STUDIO_MODEL', 'local-model')
    )
    llm_manager.register_provider(lm_studio, is_default=True)
    
    # Initialize Ollama (local)
    ollama = OllamaProvider(
        api_endpoint=getattr(settings, 'OLLAMA_ENDPOINT', 'http://localhost:11434'),
        default_model=getattr(settings, 'OLLAMA_MODEL', 'llama2')
    )
    llm_manager.register_provider(ollama)
    
    # Initialize OpenAI (if API key available)
    openai_key = getattr(settings, 'OPENAI_API_KEY', None)
    if openai_key and openai_key != 'your-openai-api-key-here':
        openai_provider = OpenAIProvider(
            api_key=openai_key,
            default_model=getattr(settings, 'OPENAI_MODEL', 'gpt-4-turbo-preview')
        )
        llm_manager.register_provider(openai_provider)
    
    # Initialize Anthropic (if API key available)
    anthropic_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
    if anthropic_key and anthropic_key != 'your-anthropic-api-key-here':
        anthropic_provider = AnthropicProvider(
            api_key=anthropic_key,
            default_model=getattr(settings, 'ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
        )
        llm_manager.register_provider(anthropic_provider)
    
    # Test all providers
    logger.info("Testing LLM provider connections...")
    results = await llm_manager.test_all_providers()
    
    available_providers = [name for name, available in results.items() if available]
    logger.info(f"Available LLM providers: {available_providers}")
    
    if not available_providers:
        logger.warning("No LLM providers are available!")
    
    return results


# Utility functions
async def quick_generate(prompt: str, provider_name: str = None, **kwargs) -> str:
    """Quick generation for simple prompts"""
    response = await llm_manager.generate(
        provider_name=provider_name,
        system_prompt="You are a helpful AI assistant.",
        user_prompt=prompt,
        **kwargs
    )
    return response.content


def get_default_llm_config():
    """Get default LLM configuration for agents"""
    return {
        'temperature': 0.7,
        'max_tokens': 4000,
        'top_p': 1.0,
        'frequency_penalty': 0.0,
        'presence_penalty': 0.0,
        'timeout': 30
    }
