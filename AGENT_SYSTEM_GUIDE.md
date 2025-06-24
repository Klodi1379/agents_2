# Agent Configuration System with LM Studio Integration

This document provides a complete guide for setting up and using the AI Company's agent configuration system with local LLM integration via LM Studio.

## 🏗️ System Architecture

The agent system consists of several key components:

### Core Components
- **Agent Configurations**: Database models storing agent settings and prompts
- **LM Studio Integration**: Service for connecting to local LLMs
- **Web Interface**: Frontend for configuring and testing agents
- **Configurable Agents**: Python classes that execute agent logic

### Database Models
- `LLMProvider`: Configuration for LLM services (LM Studio, OpenAI, etc.)
- `AgentConfiguration`: Individual agent settings and capabilities
- `AgentPromptTemplate`: Reusable prompt templates for agents

## 🚀 Quick Start Guide

### Prerequisites
1. **LM Studio**: Download and install from [https://lmstudio.ai/](https://lmstudio.ai/)
2. **Python Environment**: Python 3.8+ with Django installed
3. **Project Setup**: Ensure the AI Company Django project is running

### Step 1: Start LM Studio
1. Launch LM Studio
2. Download a model (recommended: llama-2-7b-chat or similar)
3. Load the model and start the local server
4. Verify it's running on `http://localhost:1234`

### Step 2: Initialize Agent System
```bash
# Navigate to project directory
cd C:\GPT4_PROJECTS\agents_2\ai_company

# Run migrations
python manage.py migrate

# Create default agent configurations
python manage.py create_default_agents

# Test the system
python test_agent_system.py
```

### Step 3: Start Django Server
```bash
python manage.py runserver
```

### Step 4: Access Agent Interface
Navigate to: `http://localhost:8000/agent-system/`

## 🛠️ Configuration Guide

### LLM Provider Setup
The system includes a default LM Studio provider configuration:
- **Name**: LM Studio Local
- **Endpoint**: http://localhost:1234/v1
- **Type**: Local LLM
- **Default Model**: local-model

### Default Agents
The system creates three default agents:

#### 1. Business Strategy Advisor (CEO Agent)
- **Purpose**: Strategic planning and business analysis
- **Capabilities**: strategic_planning, market_analysis, decision_making
- **Use Cases**: Market strategy, competitive analysis, growth planning

#### 2. Financial Analysis Expert
- **Purpose**: Financial modeling and analysis
- **Capabilities**: financial_analysis, modeling, forecasting
- **Use Cases**: Budget planning, ROI analysis, financial forecasting

#### 3. Market Research Analyst
- **Purpose**: Market analysis and consumer insights
- **Capabilities**: market_analysis, research, competitive_intelligence
- **Use Cases**: Market sizing, competitor analysis, trend analysis

## 💻 Using the Web Interface

### Agent Configuration List
- View all configured agents
- Check agent status and capabilities
- Access configuration and execution interfaces

### Creating New Agents
1. Click "Create New Agent"
2. Fill in basic information:
   - Name and description
   - Agent type
   - LLM configuration
3. Define system prompt
4. Configure capabilities and tools
5. Set performance parameters

### Editing Agents
1. Select agent from list
2. Modify configuration as needed
3. Test changes before saving
4. Use prompt validation tools

### Executing Agents
1. Select agent to execute
2. Use chat interface for interaction
3. Monitor agent responses
4. Export chat history if needed

## 🔧 Advanced Configuration

### Custom LLM Providers
Add support for other LLM services:

```python
# Create new LLM provider
provider = LLMProvider.objects.create(
    name='Custom OpenAI',
    provider_type='openai',
    api_endpoint='https://api.openai.com/v1',
    api_key='your-api-key',
    default_model='gpt-4',
    is_local=False
)
```

### Custom Agent Types
Extend the agent type choices in `models.py`:

```python
AGENT_TYPES = [
    ('CEO', 'CEO Agent'),
    ('CUSTOM_TYPE', 'Custom Agent Type'),
    # Add more types as needed
]
```

### Advanced Prompt Templates
Create sophisticated prompt templates with variables:

```python
template = AgentPromptTemplate.objects.create(
    agent_config=agent_config,
    prompt_type='system',
    name='Advanced Analysis Template',
    template="""
    You are {agent_name}, specialized in {domain}.
    Current context: {context}
    User request: {user_input}
    
    Please provide analysis considering:
    - {analysis_criteria}
    - {constraints}
    """,
    variables={
        'agent_name': 'Agent display name',
        'domain': 'Area of expertise',
        'context': 'Current business context',
        'user_input': 'User query',
        'analysis_criteria': 'Specific analysis requirements',
        'constraints': 'Any limitations or requirements'
    }
)
```

## 🧪 Testing and Debugging

### Test Agent System
```bash
python test_agent_system.py
```

### Test Individual Agent
```python
from agent_system.models import AgentConfiguration
from business_agents import ConfigurableAgent

# Load agent
config = AgentConfiguration.objects.get(name='Business Strategy Advisor')
agent = ConfigurableAgent(config)

# Test execution
response = agent.execute("Analyze the current market trends for AI companies")
print(response)
```

### Debugging Connection Issues
1. Verify LM Studio is running: `http://localhost:1234/v1/models`
2. Check Django logs for API errors
3. Test API endpoint directly with curl:
```bash
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local-model",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## 📁 File Structure

```
agent_system/
├── models.py              # Database models
├── views.py               # Web interface views
├── urls.py                # URL configuration
├── templates/
│   └── agent_system/
│       ├── config_list.html    # Agent list view
│       ├── config_create.html  # Agent creation form
│       ├── config_edit.html    # Agent editing form
│       └── execute.html        # Agent execution interface
├── management/
│   └── commands/
│       └── create_default_agents.py  # Setup command
└── migrations/            # Database migrations

business_agents.py         # Agent execution classes
lm_studio_service.py      # LM Studio integration
test_agent_system.py      # Test script
```

## 🔍 API Reference

### ConfigurableAgent Class
```python
class ConfigurableAgent(LMStudioAgent):
    def __init__(self, config):
        """Initialize with AgentConfiguration"""
        
    def execute(self, user_input: str, context: Dict = None) -> str:
        """Execute agent with input and optional context"""
        
    def get_capabilities(self) -> Dict:
        """Return agent capabilities and metadata"""
        
    def clear_history(self):
        """Clear conversation history"""
```

### LMStudioService Class
```python
class LMStudioService:
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        
    def test_connection(self) -> bool:
        """Test connection to LM Studio"""
        
    def get_model_info(self, model_name: str) -> Dict:
        """Get information about specific model"""
```

## 🚧 Troubleshooting

### Common Issues

1. **LM Studio Connection Failed**
   - Ensure LM Studio is running
   - Check port 1234 is not blocked
   - Verify model is loaded in LM Studio

2. **Agent Not Responding**
   - Check agent configuration status
   - Verify LLM provider is active
   - Review system prompt for errors

3. **Template Rendering Errors**
   - Check template syntax
   - Verify all variables are defined
   - Test with simple prompts first

### Performance Optimization

1. **Response Time**
   - Adjust max_tokens for faster responses
   - Use smaller models for quicker processing
   - Implement caching for repeated queries

2. **Memory Usage**
   - Clear conversation history regularly
   - Limit context window size
   - Monitor LM Studio resource usage

## 🔄 Future Enhancements

### Planned Features
- [ ] Agent collaboration workflows
- [ ] Advanced tool integration
- [ ] Performance analytics dashboard
- [ ] Multi-model routing
- [ ] Agent learning from feedback
- [ ] Integration with external APIs
- [ ] Voice interface support
- [ ] Mobile-responsive design

### Contributing
To contribute to the agent system:
1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review Django logs
- Test LM Studio connection separately
- Verify agent configurations in admin panel

---

*This agent configuration system provides a flexible foundation for building and managing AI agents with local LLM integration. The modular design allows for easy extension and customization based on specific business needs.*