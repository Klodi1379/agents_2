# 🤖 AI Company Agent Configuration System

A powerful, web-based system for creating, configuring, and managing AI agents with local LLM integration via LM Studio. This system provides a complete framework for building specialized business AI agents with custom prompts, capabilities, and monitoring.

## ✨ Features

### 🎯 Core Functionality
- **Agent Configuration**: Web-based interface for creating and managing AI agents
- **LM Studio Integration**: Seamless integration with local LLMs via LM Studio
- **Custom Prompts**: Sophisticated prompt template system with variables
- **Real-time Chat**: Interactive chat interface for testing and using agents
- **Performance Monitoring**: Track agent performance, usage, and metrics
- **Multi-Model Support**: Configure different LLM providers and models

### 🔧 Agent Management
- **Pre-built Agents**: Business Strategy, Financial Analysis, Market Research
- **Custom Agent Types**: Create specialized agents for specific business needs
- **Capability Tracking**: Define and monitor agent capabilities
- **Template System**: Reusable prompt templates with variable substitution
- **Version Control**: Track changes and updates to agent configurations

### 📊 Monitoring & Analytics
- **Status Dashboard**: Real-time agent status and health monitoring
- **Performance Metrics**: Response times, success rates, token usage
- **Usage Analytics**: Track which agents are used most frequently
- **Error Tracking**: Monitor and debug agent execution issues

## 🚀 Quick Start

### Prerequisites
1. **LM Studio**: Download from [https://lmstudio.ai/](https://lmstudio.ai/)
2. **Python 3.8+** with Django installed
3. **AI Company Django Project** set up and running

### Installation

1. **Run the automated setup script:**
   ```bash
   cd C:\GPT4_PROJECTS\agents_2\ai_company
   python setup_agent_system.py
   ```

2. **Or set up manually:**
   ```bash
   # Apply database migrations
   python manage.py migrate
   
   # Create default agent configurations
   python manage.py create_default_agents
   
   # Test the system
   python test_agent_system.py
   ```

3. **Start LM Studio:**
   - Download and install LM Studio
   - Download a model (recommended: llama-2-7b-chat or similar)
   - Load the model and start the local server
   - Verify it's running on `http://localhost:1234`

4. **Start Django server:**
   ```bash
   python manage.py runserver
   ```

5. **Access the agent system:**
   - Navigate to: `http://localhost:8000/agent-system/`
   - Use the sidebar navigation to explore features

## 🎮 Usage Guide

### Creating Your First Agent

1. **Navigate to Agent System** → **Create Agent**
2. **Fill in basic information:**
   - Name: "My Custom Agent"
   - Type: Select appropriate type
   - Description: What the agent does
3. **Configure the system prompt:**
   ```
   You are a specialized AI assistant for [specific domain].
   Your expertise includes:
   - [Key capability 1]
   - [Key capability 2]
   - [Key capability 3]
   
   Always provide:
   1. Clear, actionable recommendations
   2. Relevant context and reasoning
   3. Next steps where appropriate
   ```
4. **Set capabilities and save**

### Chatting with Agents

1. **Use the sidebar "Chat with Agent" button**
2. **Select an agent from the quick-select modal**
3. **Start chatting!**
   - Test with simple questions first
   - Try complex business scenarios
   - Export chat history for records

### Monitoring Performance

1. **Visit Agent Status page**
2. **Review key metrics:**
   - Response times
   - Success rates
   - Usage patterns
   - Error rates
3. **Use insights to optimize agent configurations**

## 📋 Default Agents

The system comes with three pre-configured agents:

### 🎯 Business Strategy Advisor
- **Purpose**: Strategic planning and market analysis
- **Capabilities**: Market analysis, strategic planning, competitive intelligence
- **Use Cases**: Business strategy, market entry, growth planning

### 💰 Financial Analysis Expert
- **Purpose**: Financial modeling and analysis
- **Capabilities**: Financial modeling, forecasting, investment analysis
- **Use Cases**: Budget planning, ROI analysis, financial forecasting

### 📊 Market Research Analyst
- **Purpose**: Market analysis and consumer insights
- **Capabilities**: Market research, competitive analysis, trend analysis
- **Use Cases**: Market sizing, competitor analysis, consumer insights

## 🛠️ Configuration Options

### LLM Provider Settings
```python
# Example LM Studio configuration
{
    "name": "LM Studio Local",
    "provider_type": "lm_studio",
    "api_endpoint": "http://localhost:1234/v1",
    "default_model": "local-model",
    "temperature": 0.7,
    "max_tokens": 4000,
    "timeout_seconds": 60
}
```

### Agent Configuration
```python
# Example agent configuration
{
    "name": "Custom Business Agent",
    "agent_type": "CEO",
    "description": "Specialized business advisor",
    "capabilities": ["strategic_planning", "market_analysis"],
    "temperature": 0.7,
    "max_tokens": 2048,
    "status": "active"
}
```

### Prompt Template System
```python
# Advanced prompt template with variables
{
    "template": """
    You are {agent_name}, an expert in {domain}.
    
    Context: {business_context}
    User Request: {user_input}
    
    Provide analysis considering:
    - {criteria_1}
    - {criteria_2}
    """,
    "variables": {
        "agent_name": "Agent display name",
        "domain": "Area of expertise",
        "business_context": "Current business situation",
        "user_input": "User's specific request"
    }
}
```

## 🔗 Navigation & URLs

### Main Navigation (Sidebar)
- **Agent Configurations**: `/agent-system/` - View and manage all agents
- **Create Agent**: `/agent-system/create/` - Create new agent configurations
- **Agent Status**: `/agent-system/status/` - Monitor system health and performance
- **Chat with Agent**: Quick-select modal for immediate agent interaction

### Direct URLs
- **Agent System Dashboard**: `http://localhost:8000/agent-system/`
- **Create New Agent**: `http://localhost:8000/agent-system/create/`
- **Edit Agent**: `http://localhost:8000/agent-system/edit/{id}/`
- **Chat Interface**: `http://localhost:8000/agent-system/execute/{id}/`
- **System Status**: `http://localhost:8000/agent-system/status/`
- **Admin Panel**: `http://localhost:8000/admin/`

### API Endpoints
- **Available Agents**: `/agent-system/api/available-agents/`
- **Agent Metrics**: `/agent-system/api/metrics/`
- **Configuration Management**: `/agent-system/config/`

## 🧪 Testing

### Automated Testing
```bash
# Run the comprehensive test script
python test_agent_system.py
```

### Manual Testing
1. **Test LM Studio connection**: Visit `http://localhost:1234/v1/models`
2. **Test agent creation**: Create a simple test agent
3. **Test chat functionality**: Send test messages to agents
4. **Test performance monitoring**: Check status dashboard

### Debugging
1. **Check Django logs** for detailed error information
2. **Verify LM Studio is running** on port 1234
3. **Test API endpoints** directly with curl or Postman
4. **Review agent configurations** in the admin panel

## 📁 File Structure

```
agent_system/
├── models.py                    # Database models
├── views.py                     # Web interface views
├── urls.py                      # URL routing
├── templates/agent_system/      # HTML templates
│   ├── config_list.html         # Agent list view
│   ├── config_create.html       # Agent creation form
│   ├── config_edit.html         # Agent editing interface
│   └── execute.html             # Chat interface
├── management/commands/         # Django management commands
│   └── create_default_agents.py # Default agent setup
└── migrations/                  # Database migrations

business_agents.py               # Agent execution classes
lm_studio_service.py            # LM Studio integration service
test_agent_system.py            # System test script
setup_agent_system.py           # Automated setup script
AGENT_SYSTEM_GUIDE.md           # Detailed technical documentation
```

## 🔧 Advanced Configuration

### Custom Agent Types
Add new agent types by modifying `models.py`:
```python
AGENT_TYPES = [
    ('CEO', 'CEO Agent'),
    ('CUSTOM_TYPE', 'My Custom Agent Type'),
    # Add your custom types here
]
```

### Multi-Provider Setup
Configure multiple LLM providers for different use cases:
```python
# OpenAI for production
openai_provider = LLMProvider(
    name="OpenAI GPT-4",
    provider_type="openai",
    api_endpoint="https://api.openai.com/v1",
    api_key="your-key-here"
)

# Local LM Studio for development
local_provider = LLMProvider(
    name="LM Studio Local",
    provider_type="lm_studio",
    api_endpoint="http://localhost:1234/v1",
    is_local=True
)
```

### Performance Optimization
1. **Adjust token limits** based on your use case
2. **Set appropriate timeouts** for your network conditions
3. **Monitor response times** and adjust accordingly
4. **Use caching** for repeated queries
5. **Implement rate limiting** for production use

## 🚧 Troubleshooting

### Common Issues

1. **LM Studio Connection Failed**
   - Ensure LM Studio is running on port 1234
   - Check that a model is loaded and active
   - Verify firewall settings aren't blocking the connection

2. **Agent Not Responding**
   - Check agent configuration status (should be "active")
   - Verify LLM provider is configured correctly
   - Review system prompt for syntax errors

3. **Slow Response Times**
   - Reduce max_tokens for faster responses
   - Check LM Studio model size and performance
   - Monitor system resources (CPU, RAM)

4. **Template Errors**
   - Verify all variables in templates are defined
   - Check JSON syntax in configuration fields
   - Test with simple prompts first

### Performance Tips
- Use smaller models for faster responses during development
- Implement conversation history limits to manage memory
- Monitor token usage to optimize costs
- Set appropriate timeout values for your environment

## 🤝 Contributing

To extend the agent system:
1. Create new agent types in `models.py`
2. Add corresponding templates in `templates/`
3. Implement custom agent logic in `business_agents.py`
4. Update navigation and URLs as needed
5. Test thoroughly with the provided test scripts

## 📞 Support

For help with the agent system:
1. Check this README and the detailed guide (`AGENT_SYSTEM_GUIDE.md`)
2. Run the test script to diagnose issues
3. Review Django logs for detailed error information
4. Verify LM Studio configuration and connectivity

---

**🎉 Enjoy building powerful AI agents with the AI Company Agent System!**

*This system provides a solid foundation for creating sophisticated AI agents tailored to your specific business needs. The modular design allows for easy customization and extension as your requirements evolve.*