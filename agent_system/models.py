"""
Agent Configuration Models

This module defines database models for configuring and managing AI agents,
including their prompts, settings, and LLM configurations.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class LLMProvider(models.Model):
    """Configuration for different LLM providers (OpenAI, Anthropic, LM Studio, etc.)"""
    
    PROVIDER_TYPES = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic Claude'),
        ('lm_studio', 'LM Studio (Local)'),
        ('ollama', 'Ollama (Local)'),
        ('huggingface', 'Hugging Face'),
        ('custom', 'Custom API'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    provider_type = models.CharField(max_length=20, choices=PROVIDER_TYPES)
    api_endpoint = models.URLField(help_text="API endpoint URL")
    api_key = models.CharField(max_length=255, blank=True, help_text="API key (if required)")
    is_active = models.BooleanField(default=True)
    is_local = models.BooleanField(default=False, help_text="Is this a local LLM?")
    
    # Configuration options
    default_model = models.CharField(max_length=100, blank=True)
    max_tokens = models.IntegerField(default=4000)
    temperature = models.FloatField(default=0.7, validators=[MinValueValidator(0.0), MaxValueValidator(2.0)])
    timeout_seconds = models.IntegerField(default=30)
    
    # Cost tracking
    cost_per_1k_tokens = models.DecimalField(max_digits=8, decimal_places=6, default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()})"


class AgentConfiguration(models.Model):
    """Configuration for individual AI agents"""
    
    AGENT_TYPES = [
        ('CEO', 'CEO Agent'),
        ('MARKET_RESEARCH', 'Market Research Agent'),
        ('FINANCIAL_ANALYST', 'Financial Analyst Agent'),
        ('TECHNICAL_LEAD', 'Technical Lead Agent'),
        ('RISK_ANALYST', 'Risk Analyst Agent'),
        ('MARKETING_STRATEGIST', 'Marketing Strategist Agent'),
        ('IDEA_GENERATOR', 'Idea Generator Agent'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
        ('testing', 'Testing'),
    ]
    
    # Basic Information
    agent_type = models.CharField(max_length=50, choices=AGENT_TYPES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    version = models.CharField(max_length=20, default="1.0.0")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # LLM Configuration
    llm_provider = models.ForeignKey(LLMProvider, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=100, help_text="Specific model to use")
    temperature = models.FloatField(default=0.7, validators=[MinValueValidator(0.0), MaxValueValidator(2.0)])
    max_tokens = models.IntegerField(default=4000)
    top_p = models.FloatField(default=1.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    frequency_penalty = models.FloatField(default=0.0, validators=[MinValueValidator(-2.0), MaxValueValidator(2.0)])
    presence_penalty = models.FloatField(default=0.0, validators=[MinValueValidator(-2.0), MaxValueValidator(2.0)])
    
    # Capabilities and Metadata
    capabilities = models.JSONField(default=list, help_text="List of agent capabilities")
    required_data_sources = models.JSONField(default=list)
    tags = models.JSONField(default=list, help_text="Tags for categorization")
    
    # Performance Settings
    timeout_seconds = models.IntegerField(default=30)
    max_retries = models.IntegerField(default=3)
    retry_delay_seconds = models.IntegerField(default=5)
    
    # Audit Fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_agents')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_agents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['agent_type']
    
    def __str__(self):
        return f"{self.name} ({self.get_agent_type_display()})"
    
    def get_capabilities_list(self):
        """Return capabilities as a formatted list"""
        return self.capabilities if isinstance(self.capabilities, list) else []
    
    def is_available(self):
        """Check if agent is available for use"""
        return self.status == 'active' and self.llm_provider.is_active


class AgentPromptTemplate(models.Model):
    """Prompt templates for agents"""
    
    PROMPT_TYPES = [
        ('system', 'System Prompt'),
        ('analysis', 'Analysis Prompt'),
        ('instruction', 'Instruction Template'),
        ('example', 'Example Template'),
    ]
    
    agent_config = models.ForeignKey(AgentConfiguration, on_delete=models.CASCADE, related_name='prompt_templates')
    prompt_type = models.CharField(max_length=20, choices=PROMPT_TYPES)
    name = models.CharField(max_length=100)
    template = models.TextField(help_text="Prompt template with variable placeholders")
    variables = models.JSONField(default=dict, help_text="Available variables and their descriptions")
    
    # Template metadata
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=20, default="1.0.0")
    notes = models.TextField(blank=True)
    
    # Performance tracking
    usage_count = models.IntegerField(default=0)
    average_response_time = models.FloatField(default=0.0)
    average_token_usage = models.IntegerField(default=0)
    success_rate = models.FloatField(default=100.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['agent_config', 'prompt_type', 'name']
        ordering = ['agent_config', 'prompt_type', 'name']
    
    def __str__(self):
        return f"{self.agent_config.name} - {self.get_prompt_type_display()}: {self.name}"
    
    def render_template(self, context_data):
        """Render the template with provided context data"""
        template_str = self.template
        for key, value in context_data.items():
            placeholder = f"{{{key}}}"
            template_str = template_str.replace(placeholder, str(value))
        return template_str
    
    def get_variables_list(self):
        """Return variables as a formatted list"""
        return self.variables if isinstance(self.variables, dict) else {}


class AgentExecutionLog(models.Model):
    """Log of agent executions for monitoring and debugging"""
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('timeout', 'Timeout'),
        ('error', 'Error'),
    ]
    
    agent_config = models.ForeignKey(AgentConfiguration, on_delete=models.CASCADE, related_name='execution_logs')
    business_idea_id = models.CharField(max_length=100, blank=True)
    
    # Execution details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    execution_time_seconds = models.FloatField()
    token_usage = models.IntegerField(default=0)
    estimated_cost = models.DecimalField(max_digits=8, decimal_places=6, default=0.0)
    
    # Request/Response data
    prompt_used = models.TextField()
    response_content = models.TextField(blank=True)
    structured_data = models.JSONField(default=dict)
    confidence_score = models.FloatField(default=0.0)
    
    # Error information
    error_message = models.TextField(blank=True)
    error_type = models.CharField(max_length=100, blank=True)
    
    # Metadata
    model_used = models.CharField(max_length=100)
    llm_provider_name = models.CharField(max_length=100)
    execution_timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-execution_timestamp']
    
    def __str__(self):
        return f"{self.agent_config.name} - {self.status} ({self.execution_timestamp})"


class AgentPerformanceMetrics(models.Model):
    """Aggregated performance metrics for agents"""
    
    agent_config = models.OneToOneField(AgentConfiguration, on_delete=models.CASCADE, related_name='performance_metrics')
    
    # Execution metrics
    total_executions = models.IntegerField(default=0)
    successful_executions = models.IntegerField(default=0)
    failed_executions = models.IntegerField(default=0)
    average_execution_time = models.FloatField(default=0.0)
    average_token_usage = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    
    # Quality metrics
    average_confidence_score = models.FloatField(default=0.0)
    average_response_quality = models.FloatField(default=0.0)
    
    # Time-based metrics
    executions_last_24h = models.IntegerField(default=0)
    executions_last_7d = models.IntegerField(default=0)
    executions_last_30d = models.IntegerField(default=0)
    
    # Status tracking
    last_execution_at = models.DateTimeField(null=True, blank=True)
    last_successful_execution_at = models.DateTimeField(null=True, blank=True)
    last_failure_at = models.DateTimeField(null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_executions == 0:
            return 0.0
        return (self.successful_executions / self.total_executions) * 100
    
    def average_cost_per_execution(self):
        """Calculate average cost per execution"""
        if self.total_executions == 0:
            return 0.0
        return float(self.total_cost / self.total_executions)
    
    def __str__(self):
        return f"{self.agent_config.name} Metrics"


class AgentConfigurationPreset(models.Model):
    """Predefined configuration presets for quick agent setup"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    agent_type = models.CharField(max_length=50, choices=AgentConfiguration.AGENT_TYPES)
    
    # Configuration data
    config_data = models.JSONField(help_text="Complete agent configuration as JSON")
    prompt_templates = models.JSONField(default=list, help_text="Prompt templates for this preset")
    
    # Metadata
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['agent_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_agent_type_display()})"
