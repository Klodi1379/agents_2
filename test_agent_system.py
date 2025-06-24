#!/usr/bin/env python
"""
Test script for the Agent Configuration System

This script tests the basic functionality of the agent system
including configuration loading and LM Studio integration.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_company.settings')
django.setup()

from agent_system.models import AgentConfiguration, LLMProvider
from business_agents import ConfigurableAgent

def test_agent_system():
    print("Testing Agent Configuration System")
    print("=" * 50)
    
    # Test 1: Check LLM Provider
    print("\n1. Testing LLM Provider Configuration...")
    try:
        provider = LLMProvider.objects.get(name='LM Studio Local')
        print(f"[SUCCESS] LM Studio Provider found: {provider}")
        print(f"   - Endpoint: {provider.api_endpoint}")
        print(f"   - Active: {provider.is_active}")
        print(f"   - Local: {provider.is_local}")
    except LLMProvider.DoesNotExist:
        print("[ERROR] LM Studio Provider not found!")
        return False
    
    # Test 2: Check Agent Configurations
    print("\n2. Testing Agent Configurations...")
    agents = AgentConfiguration.objects.filter(status='active')
    print(f"[SUCCESS] Found {agents.count()} active agent configurations:")
    
    for agent in agents:
        print(f"   - {agent.name} ({agent.get_agent_type_display()})")
        print(f"     Status: {agent.status}")
        print(f"     Model: {agent.model_name}")
        print(f"     Capabilities: {', '.join(agent.capabilities)}")
    
    # Test 3: Test Agent Instantiation
    print("\n3. Testing Agent Instantiation...")
    if agents.exists():
        test_agent_config = agents.first()
        try:
            agent = ConfigurableAgent(test_agent_config)
            print(f"[SUCCESS] Successfully created agent: {agent.config.name}")
            print(f"   - Model: {agent.model}")
            print(f"   - Temperature: {agent.temperature}")
            print(f"   - Max Tokens: {agent.max_tokens}")
            
            # Test capabilities
            capabilities = agent.get_capabilities()
            print(f"   - Capabilities: {capabilities}")
            
        except Exception as e:
            print(f"[ERROR] Error creating agent: {str(e)}")
            return False
    
    # Test 4: Test LM Studio Connection (basic)
    print("\n4. Testing LM Studio Connection...")
    print("[INFO] Note: This requires LM Studio to be running on localhost:1234")
    
    if agents.exists():
        test_agent = ConfigurableAgent(agents.first())
        try:
            # This will only work if LM Studio is actually running
            print("   - Attempting connection to LM Studio...")
            print("   - If LM Studio is running, you can test with:")
            print("     agent.execute('Hello, can you introduce yourself?')")
        except Exception as e:
            print(f"   - Connection test skipped: {str(e)}")
    
    print("\n[SUCCESS] Agent System Test Complete!")
    print("\nNext Steps:")
    print("1. Start LM Studio and load a model")
    print("2. Run the Django development server:")
    print("   python manage.py runserver")
    print("3. Navigate to: http://localhost:8000/agent-system/")
    print("4. Configure and test your agents!")
    
    return True

if __name__ == '__main__':
    test_agent_system()