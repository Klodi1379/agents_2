from django.core.management.base import BaseCommand
from agent_system.models import AgentConfiguration, LLMProvider, AgentPromptTemplate

class Command(BaseCommand):
    help = 'Create default agent configurations'

    def handle(self, *args, **options):
        self.stdout.write('Creating default agent configurations...')

        # First, ensure we have an LM Studio provider
        lm_studio_provider, created = LLMProvider.objects.get_or_create(
            name='LM Studio Local',
            defaults={
                'provider_type': 'lm_studio',
                'api_endpoint': 'http://localhost:1234/v1',
                'is_active': True,
                'is_local': True,
                'default_model': 'local-model',
                'max_tokens': 4000,
                'temperature': 0.7,
                'timeout_seconds': 60
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('Created LM Studio provider'))

        # Define agent configurations
        agents_data = [
            {
                'agent_type': 'CEO',
                'name': 'Business Strategy Advisor',
                'description': 'Expert in business strategy, market analysis, and strategic planning',
                'capabilities': ['strategic_planning', 'market_analysis', 'decision_making'],
                'system_prompt': """You are a senior business strategy consultant with 20+ years of experience. 
You help companies analyze markets, develop strategies, and make informed business decisions.

Your expertise includes:
- Market analysis and competitive intelligence
- Strategic planning and roadmap development
- Business model innovation
- Growth strategies and expansion planning
- Risk assessment and mitigation
- Financial planning and forecasting

Always provide:
1. Clear, actionable recommendations
2. Data-driven insights where possible
3. Risk considerations for each recommendation
4. Implementation timelines and milestones
5. Success metrics and KPIs

Be concise but thorough. Ask clarifying questions when needed."""
            },

            {
                'agent_type': 'FINANCIAL_ANALYST',
                'name': 'Financial Analysis Expert',
                'description': 'Specialized in financial modeling, analysis, and investment decisions',
                'capabilities': ['financial_analysis', 'modeling', 'forecasting'],
                'system_prompt': """You are a CFO-level financial analyst with expertise in:
- Financial statement analysis
- Cash flow modeling and forecasting
- Investment analysis and ROI calculations
- Budget planning and variance analysis
- Risk assessment and scenario planning
- Valuation methodologies

Always provide:
1. Quantitative analysis with supporting data
2. Multiple scenarios (best case, worst case, most likely)
3. Clear assumptions and methodologies
4. Visual representations when helpful
5. Executive summaries for complex analyses

Be precise with numbers and clearly explain your reasoning."""
            },
            {
                'agent_type': 'MARKET_RESEARCH',
                'name': 'Market Research Analyst',
                'description': 'Specialist in market analysis, consumer insights, and competitive intelligence',
                'capabilities': ['market_analysis', 'research', 'competitive_intelligence'],
                'system_prompt': """You are a market research analyst with expertise in:
- Market size and growth analysis
- Consumer behavior and preferences
- Competitive landscape analysis
- Industry trends and forecasting
- Survey design and data interpretation
- SWOT and Porter's Five Forces analysis

Always provide:
1. Data-backed market insights
2. Clear methodology for research approaches
3. Actionable recommendations based on findings
4. Relevant charts and visualizations
5. Sources and confidence levels for data

Focus on actionable insights that drive business decisions."""
            }

        ]

        created_count = 0
        for agent_data in agents_data:
            # Create the agent configuration
            config_data = {
                'agent_type': agent_data['agent_type'],
                'name': agent_data['name'],
                'description': agent_data['description'],
                'llm_provider': lm_studio_provider,
                'model_name': 'local-model',
                'temperature': 0.7,
                'max_tokens': 2048,
                'capabilities': agent_data['capabilities'],
                'status': 'active',
                'timeout_seconds': 60,
                'max_retries': 3
            }
            
            config, created = AgentConfiguration.objects.get_or_create(
                agent_type=agent_data['agent_type'],
                defaults=config_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {config.name}')
                )
                
                # Create system prompt template
                AgentPromptTemplate.objects.get_or_create(
                    agent_config=config,
                    prompt_type='system',
                    name='Default System Prompt',
                    defaults={
                        'template': agent_data['system_prompt'],
                        'variables': {},
                        'is_active': True
                    }
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Already exists: {config.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new agent configurations')
        )