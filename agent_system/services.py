"""
Enhanced Agent Configuration Service

This module provides high-level services for configuring and managing AI agents,
including default configurations and prompt templates.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from django.db import transaction
from django.contrib.auth.models import User

from .models import (
    AgentConfiguration, LLMProvider, AgentPromptTemplate, 
    AgentConfigurationPreset, AgentPerformanceMetrics
)
from .llm_service import llm_manager, initialize_llm_providers


logger = logging.getLogger(__name__)


class AgentConfigurationService:
    """Service for managing agent configurations"""
    
    @staticmethod
    def create_default_configurations():
        """Create default agent configurations and templates"""
        
        # Create default LM Studio provider if it doesn't exist
        lm_studio_provider, created = LLMProvider.objects.get_or_create(
            name="LM Studio Local",
            defaults={
                'provider_type': 'lm_studio',
                'api_endpoint': 'http://localhost:1234',
                'is_local': True,
                'is_active': True,
                'default_model': 'local-model',
                'max_tokens': 4000,
                'temperature': 0.7,
                'cost_per_1k_tokens': 0.0,
            }
        )
        
        if created:
            logger.info("Created default LM Studio provider")
        
        # Default agent configurations
        default_agents = [
            {
                'agent_type': 'CEO',
                'name': 'CEO Strategic Analyst',
                'description': 'Chief Executive Officer agent for strategic business analysis and decision making',
                'capabilities': ['Strategic planning', 'Executive decision making', 'Risk assessment', 'Team coordination'],
                'required_data_sources': ['market_data', 'financial_data', 'competitive_intelligence'],
                'tags': ['leadership', 'strategy', 'executive'],
            },
            {
                'agent_type': 'MARKET_RESEARCH',
                'name': 'Market Research Specialist',
                'description': 'Market research and competitive analysis specialist',
                'capabilities': ['Market sizing', 'Competitive analysis', 'Customer segmentation', 'Trend analysis'],
                'required_data_sources': ['market_reports', 'customer_surveys', 'competitor_data'],
                'tags': ['research', 'market', 'analysis'],
            },
            {
                'agent_type': 'FINANCIAL_ANALYST',
                'name': 'Financial Analysis Expert',
                'description': 'Financial modeling and investment analysis expert',
                'capabilities': ['Financial modeling', 'Valuation analysis', 'ROI calculation', 'Risk assessment'],
                'required_data_sources': ['financial_statements', 'market_data', 'industry_benchmarks'],
                'tags': ['finance', 'modeling', 'analysis'],
            },
            {
                'agent_type': 'TECHNICAL_LEAD',
                'name': 'Technical Architecture Lead',
                'description': 'Technical feasibility and architecture assessment specialist',
                'capabilities': ['Technical architecture', 'Feasibility analysis', 'Technology selection', 'Resource planning'],
                'required_data_sources': ['technical_requirements', 'industry_standards', 'technology_trends'],
                'tags': ['technology', 'architecture', 'feasibility'],
            },
            {
                'agent_type': 'RISK_ANALYST',
                'name': 'Risk Assessment Specialist',
                'description': 'Comprehensive risk analysis and mitigation planning expert',
                'capabilities': ['Risk identification', 'Impact assessment', 'Mitigation strategies', 'Compliance review'],
                'required_data_sources': ['regulatory_data', 'industry_risks', 'historical_incidents'],
                'tags': ['risk', 'compliance', 'security'],
            },
        ]
        
        created_agents = []
        for agent_data in default_agents:
            agent_config, created = AgentConfiguration.objects.get_or_create(
                agent_type=agent_data['agent_type'],
                defaults={
                    **agent_data,
                    'llm_provider': lm_studio_provider,
                    'model_name': 'local-model',
                    'version': '1.0.0',
                    'status': 'active',
                }
            )
            
            if created:
                created_agents.append(agent_config)
                # Create performance metrics
                AgentPerformanceMetrics.objects.create(agent_config=agent_config)
                logger.info(f"Created default configuration for {agent_config.name}")
        
        return created_agents
    
    @staticmethod
    def create_default_prompt_templates():
        """Create default prompt templates for all agent configurations"""
        
        # CEO Agent Templates
        ceo_config = AgentConfiguration.objects.filter(agent_type='CEO').first()
        if ceo_config:
            AgentConfigurationService._create_ceo_templates(ceo_config)
        
        # Market Research Agent Templates
        market_config = AgentConfiguration.objects.filter(agent_type='MARKET_RESEARCH').first()
        if market_config:
            AgentConfigurationService._create_market_research_templates(market_config)
        
        # Financial Analyst Templates
        financial_config = AgentConfiguration.objects.filter(agent_type='FINANCIAL_ANALYST').first()
        if financial_config:
            AgentConfigurationService._create_financial_templates(financial_config)
        
        # Technical Lead Templates
        technical_config = AgentConfiguration.objects.filter(agent_type='TECHNICAL_LEAD').first()
        if technical_config:
            AgentConfigurationService._create_technical_templates(technical_config)
        
        # Risk Analyst Templates
        risk_config = AgentConfiguration.objects.filter(agent_type='RISK_ANALYST').first()
        if risk_config:
            AgentConfigurationService._create_risk_templates(risk_config)
    
    @staticmethod
    def _create_ceo_templates(agent_config):
        """Create CEO agent prompt templates"""
        templates = [
            {
                'prompt_type': 'system',
                'name': 'CEO System Prompt',
                'template': '''You are an experienced Chief Executive Officer with 20+ years of experience building and scaling successful businesses across multiple industries. 

Your role is to:
1. Provide strategic oversight and executive-level analysis
2. Synthesize insights from various department reports
3. Make final recommendations on business viability
4. Identify critical success factors and major risks
5. Evaluate overall business model and market fit

Your analysis should be:
- Strategic and high-level, not operational details
- Based on proven business principles and market realities
- Focused on scalability, profitability, and sustainable competitive advantage
- Balanced between optimism and realistic risk assessment

Always provide structured, actionable insights with clear reasoning.''',
                'variables': {
                    'experience_level': 'Years of CEO experience to emphasize',
                    'industry_focus': 'Specific industries to highlight'
                }
            },
            {
                'prompt_type': 'analysis',
                'name': 'Business Viability Analysis',
                'template': '''Analyze this business idea from a CEO perspective:

**Business Idea:** {title}
**Description:** {description}
**Industry:** {industry}
**Target Market:** {target_market}
**Estimated Budget:** {budget}

Provide an executive analysis covering:

1. **STRATEGIC ASSESSMENT**
   - Market opportunity size and growth potential
   - Competitive landscape and positioning
   - Business model viability and scalability

2. **CRITICAL SUCCESS FACTORS**
   - Key metrics that will determine success/failure
   - Required capabilities and resources
   - Timeline considerations

3. **MAJOR RISKS & MITIGATION**
   - Market risks (competition, demand, timing)
   - Execution risks (team, technology, funding)
   - External risks (regulation, economic factors)

4. **FINANCIAL VIABILITY**
   - Revenue model assessment
   - Cost structure evaluation
   - Path to profitability

5. **RECOMMENDATION**
   - Overall viability score (1-100)
   - Go/No-Go recommendation with rationale
   - Key next steps if proceeding''',
                'variables': {
                    'title': 'Business idea title',
                    'description': 'Business idea description',
                    'industry': 'Target industry',
                    'target_market': 'Target market description',
                    'budget': 'Estimated budget'
                }
            }
        ]
        
        for template_data in templates:
            AgentPromptTemplate.objects.get_or_create(
                agent_config=agent_config,
                prompt_type=template_data['prompt_type'],
                name=template_data['name'],
                defaults={
                    'template': template_data['template'],
                    'variables': template_data['variables'],
                    'is_active': True,
                    'version': '1.0.0'
                }
            )
    
    @staticmethod
    def _create_market_research_templates(agent_config):
        """Create Market Research agent prompt templates"""
        templates = [
            {
                'prompt_type': 'system',
                'name': 'Market Research System Prompt',
                'template': '''You are a senior Market Research Analyst with expertise in evaluating market opportunities across various industries. 

Your specialties include:
- Market sizing and growth analysis using TAM/SAM/SOM framework
- Competitive landscape mapping and competitor analysis
- Customer segmentation and persona development
- Market trend identification and impact assessment
- Go-to-market strategy recommendations

Your analysis should be data-driven, methodical, and include specific market metrics where possible. Focus on actionable insights that inform business strategy.''',
                'variables': {}
            },
            {
                'prompt_type': 'analysis',
                'name': 'Comprehensive Market Analysis',
                'template': '''Conduct a comprehensive market research analysis for:

**Business Idea:** {title}
**Description:** {description}
**Industry:** {industry}
**Target Market:** {target_market}

Provide detailed analysis in these areas:

1. **MARKET OPPORTUNITY**
   - Total Addressable Market (TAM) estimation
   - Serviceable Addressable Market (SAM)
   - Serviceable Obtainable Market (SOM)
   - Market growth rate and trends

2. **COMPETITIVE LANDSCAPE**
   - Direct competitors (top 3-5)
   - Indirect competitors and alternatives
   - Competitive advantages and gaps
   - Market share distribution

3. **CUSTOMER ANALYSIS**
   - Primary customer segments
   - Customer pain points and needs
   - Buying behavior and decision factors
   - Price sensitivity analysis

4. **MARKET ENTRY STRATEGY**
   - Optimal market entry approach
   - Key distribution channels
   - Partnership opportunities
   - Regulatory considerations''',
                'variables': {
                    'title': 'Business idea title',
                    'description': 'Business idea description',
                    'industry': 'Target industry',
                    'target_market': 'Target market description'
                }
            }
        ]
        
        for template_data in templates:
            AgentPromptTemplate.objects.get_or_create(
                agent_config=agent_config,
                prompt_type=template_data['prompt_type'],
                name=template_data['name'],
                defaults={
                    'template': template_data['template'],
                    'variables': template_data['variables'],
                    'is_active': True,
                    'version': '1.0.0'
                }
            )
    
    @staticmethod
    def _create_financial_templates(agent_config):
        """Create Financial Analyst agent prompt templates"""
        templates = [
            {
                'prompt_type': 'system',
                'name': 'Financial Analyst System Prompt',
                'template': '''You are a Senior Financial Analyst with expertise in startup and growth company financial modeling. 

Your core competencies include:
- Building comprehensive financial models and projections
- Valuation analysis using multiple methodologies
- Cash flow analysis and break-even calculations
- Funding requirement assessment and strategy
- Risk-adjusted return analysis

Your analysis should be quantitative, conservative in assumptions, and provide multiple scenarios (optimistic, realistic, pessimistic). Focus on key financial metrics that investors and stakeholders care about.''',
                'variables': {}
            },
            {
                'prompt_type': 'analysis',
                'name': 'Financial Viability Analysis',
                'template': '''Conduct financial analysis and modeling for:

**Business Idea:** {title}
**Description:** {description}
**Industry:** {industry}
**Estimated Budget:** {budget}

Provide comprehensive financial analysis:

1. **REVENUE MODEL ANALYSIS**
   - Revenue streams identification
   - Pricing strategy evaluation
   - Revenue projections (3-year)
   - Unit economics analysis

2. **COST STRUCTURE**
   - Initial setup costs
   - Fixed vs variable costs
   - Operating expense breakdown
   - Scaling cost implications

3. **FINANCIAL PROJECTIONS**
   - 3-year P&L projection
   - Cash flow analysis
   - Break-even analysis
   - ROI calculations

4. **FUNDING REQUIREMENTS**
   - Initial capital needs
   - Working capital requirements
   - Funding milestones and timeline
   - Potential funding sources''',
                'variables': {
                    'title': 'Business idea title',
                    'description': 'Business idea description',
                    'industry': 'Target industry',
                    'budget': 'Estimated budget'
                }
            }
        ]
        
        for template_data in templates:
            AgentPromptTemplate.objects.get_or_create(
                agent_config=agent_config,
                prompt_type=template_data['prompt_type'],
                name=template_data['name'],
                defaults={
                    'template': template_data['template'],
                    'variables': template_data['variables'],
                    'is_active': True,
                    'version': '1.0.0'
                }
            )
    
    @staticmethod
    def _create_technical_templates(agent_config):
        """Create Technical Lead agent prompt templates"""
        templates = [
            {
                'prompt_type': 'system',
                'name': 'Technical Lead System Prompt',
                'template': '''You are a Senior Technical Lead with extensive experience in software architecture, system design, and technology implementation across various industries.

Your expertise includes:
- System architecture design and evaluation
- Technology stack selection and optimization
- Technical feasibility assessment
- Resource planning and capacity estimation
- Security and scalability considerations

Your analysis should be practical, technically sound, and consider both current and future requirements. Focus on realistic implementation timelines and resource needs.''',
                'variables': {}
            },
            {
                'prompt_type': 'analysis',
                'name': 'Technical Feasibility Analysis',
                'template': '''Analyze the technical feasibility for:

**Business Idea:** {title}
**Description:** {description}
**Industry:** {industry}
**Technical Requirements:** {technical_requirements}

Provide comprehensive technical analysis:

1. **ARCHITECTURE ASSESSMENT**
   - Recommended system architecture
   - Technology stack selection
   - Integration requirements
   - Scalability considerations

2. **IMPLEMENTATION FEASIBILITY**
   - Development complexity assessment
   - Required technical skills and team size
   - Estimated development timeline
   - Critical technical risks

3. **INFRASTRUCTURE REQUIREMENTS**
   - Hardware and software requirements
   - Cloud vs on-premise considerations
   - Security and compliance needs
   - Monitoring and maintenance requirements

4. **RESOURCE PLANNING**
   - Technical team structure
   - Development phases and milestones
   - Budget estimation for technology components
   - Third-party service dependencies''',
                'variables': {
                    'title': 'Business idea title',
                    'description': 'Business idea description',
                    'industry': 'Target industry',
                    'technical_requirements': 'Technical requirements and constraints'
                }
            }
        ]
        
        for template_data in templates:
            AgentPromptTemplate.objects.get_or_create(
                agent_config=agent_config,
                prompt_type=template_data['prompt_type'],
                name=template_data['name'],
                defaults={
                    'template': template_data['template'],
                    'variables': template_data['variables'],
                    'is_active': True,
                    'version': '1.0.0'
                }
            )
    
    @staticmethod
    def _create_risk_templates(agent_config):
        """Create Risk Analyst agent prompt templates"""
        templates = [
            {
                'prompt_type': 'system',
                'name': 'Risk Analyst System Prompt',
                'template': '''You are a Senior Risk Analyst with expertise in comprehensive risk assessment and mitigation planning across various business domains.

Your specialties include:
- Risk identification and categorization
- Impact and probability assessment
- Mitigation strategy development
- Regulatory and compliance analysis
- Business continuity planning

Your analysis should be thorough, systematic, and provide actionable risk mitigation strategies. Consider both quantitative and qualitative risk factors.''',
                'variables': {}
            },
            {
                'prompt_type': 'analysis',
                'name': 'Comprehensive Risk Assessment',
                'template': '''Conduct a comprehensive risk analysis for:

**Business Idea:** {title}
**Description:** {description}
**Industry:** {industry}
**Target Market:** {target_market}

Provide detailed risk assessment:

1. **BUSINESS RISKS**
   - Market risks (demand, competition, timing)
   - Financial risks (funding, cash flow, costs)
   - Operational risks (execution, supply chain, quality)
   - Strategic risks (business model, positioning)

2. **EXTERNAL RISKS**
   - Regulatory and compliance risks
   - Economic and market condition risks
   - Technology and cybersecurity risks
   - Environmental and social risks

3. **RISK PRIORITIZATION**
   - Risk impact assessment (High/Medium/Low)
   - Probability assessment (High/Medium/Low)
   - Risk matrix and prioritization
   - Critical risk factors

4. **MITIGATION STRATEGIES**
   - Risk prevention measures
   - Risk transfer options (insurance, partnerships)
   - Contingency planning
   - Monitoring and early warning systems''',
                'variables': {
                    'title': 'Business idea title',
                    'description': 'Business idea description',
                    'industry': 'Target industry',
                    'target_market': 'Target market description'
                }
            }
        ]
        
        for template_data in templates:
            AgentPromptTemplate.objects.get_or_create(
                agent_config=agent_config,
                prompt_type=template_data['prompt_type'],
                name=template_data['name'],
                defaults={
                    'template': template_data['template'],
                    'variables': template_data['variables'],
                    'is_active': True,
                    'version': '1.0.0'
                }
            )


class AgentExecutionService:
    """Service for executing agents with configured settings"""
    
    @staticmethod
    async def execute_agent(agent_config: AgentConfiguration, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an agent with the given context"""
        from .business_agents import communication_hub
        from datetime import datetime
        
        start_time = datetime.now()
        
        try:
            # Get the system prompt template
            system_template = agent_config.prompt_templates.filter(
                prompt_type='system',
                is_active=True
            ).first()
            
            # Get the analysis prompt template
            analysis_template = agent_config.prompt_templates.filter(
                prompt_type='analysis',
                is_active=True
            ).first()
            
            if not system_template or not analysis_template:
                raise ValueError(f"Missing prompt templates for agent {agent_config.name}")
            
            # Render the prompts
            system_prompt = system_template.render_template(context_data)
            analysis_prompt = analysis_template.render_template(context_data)
            
            # Execute using the LLM service
            response = await llm_manager.generate(
                provider_name=agent_config.llm_provider.name,
                system_prompt=system_prompt,
                user_prompt=analysis_prompt,
                model=agent_config.model_name,
                temperature=agent_config.temperature,
                max_tokens=agent_config.max_tokens,
                top_p=agent_config.top_p,
                frequency_penalty=agent_config.frequency_penalty,
                presence_penalty=agent_config.presence_penalty,
                timeout=agent_config.timeout_seconds
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Parse the response based on agent type
            if agent_config.agent_type == 'CEO':
                from .business_agents import CEOAgent
                parsed_response = CEOAgent().parse_response(response.content)
            elif agent_config.agent_type == 'MARKET_RESEARCH':
                from .business_agents import MarketResearchAgent
                parsed_response = MarketResearchAgent().parse_response(response.content)
            elif agent_config.agent_type == 'FINANCIAL_ANALYST':
                from .business_agents import FinancialAnalystAgent
                parsed_response = FinancialAnalystAgent().parse_response(response.content)
            else:
                # Default parsing
                parsed_response = {'raw_content': response.content}
            
            return {
                'success': True,
                'parsed_response': parsed_response,
                'raw_response': response.content,
                'execution_time': execution_time,
                'token_usage': response.token_usage,
                'cost_estimate': response.cost_estimate,
                'model_used': response.model_used
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Agent execution failed for {agent_config.name}: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'execution_time': execution_time,
                'token_usage': 0,
                'cost_estimate': 0.0
            }


# Utility functions
def setup_default_agent_system():
    """Set up the default agent system with configurations and templates"""
    with transaction.atomic():
        # Create default configurations
        agents = AgentConfigurationService.create_default_configurations()
        
        # Create default prompt templates
        AgentConfigurationService.create_default_prompt_templates()
        
        logger.info(f"Set up default agent system with {len(agents)} agents")
        
        return agents


async def test_agent_configuration(agent_config: AgentConfiguration) -> Dict[str, Any]:
    """Test an agent configuration with a simple prompt"""
    test_context = {
        'title': 'Test Business Idea',
        'description': 'A simple test to verify agent configuration',
        'industry': 'Technology',
        'target_market': 'General consumers',
        'budget': '$10,000'
    }
    
    result = await AgentExecutionService.execute_agent(agent_config, test_context)
    
    return {
        'agent_name': agent_config.name,
        'test_successful': result['success'],
        'execution_time': result.get('execution_time', 0),
        'error': result.get('error'),
        'token_usage': result.get('token_usage', 0)
    }
