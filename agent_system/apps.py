from django.apps import AppConfig


class AgentSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agent_system'
    verbose_name = 'AI Agent System'
    
    def ready(self):
        # Initialize agents when Django starts
        from .business_agents import initialize_agents
        initialize_agents()
