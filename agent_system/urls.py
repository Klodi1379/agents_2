"""
URL Configuration for Agent System
"""

from django.urls import path
from . import views

app_name = 'agent_system'

urlpatterns = [
    # Main agent system entry points
    path('', views.config_list, name='config_list'),
    path('create/', views.config_create, name='config_create'),
    path('edit/<int:config_id>/', views.config_edit, name='config_edit'),
    path('execute/<int:config_id>/', views.execute_agent, name='execute_agent'),
    
    # Agent Status and Monitoring
    path('status/', views.agent_status_view, name='agent_status'),
    path('agent/<str:agent_type>/', views.agent_detail_view, name='agent_detail'),
    path('communication/', views.communication_hub_view, name='communication_hub'),
    path('metrics/', views.agent_metrics_view, name='agent_metrics'),
    
    # API Endpoints
    path('api/available-agents/', views.api_available_agents, name='api_available_agents'),
    
    # Agent Configuration Management
    path('config/', views.agent_configuration_list_view, name='configuration_list'),
    path('config/create/', views.agent_configuration_create_view, name='configuration_create'),
    path('config/<int:config_id>/', views.agent_configuration_detail_view, name='configuration_detail'),
    
    # LLM Provider Management
    path('providers/', views.llm_provider_list_view, name='provider_list'),
    path('providers/create/', views.llm_provider_create_view, name='provider_create'),
    path('providers/test/', views.test_llm_provider_view, name='test_provider'),
    
    # Prompt Template Management
    path('config/<int:config_id>/prompts/', views.prompt_template_list_view, name='prompt_templates'),
    path('prompts/<int:template_id>/edit/', views.prompt_template_edit_view, name='prompt_template_edit'),
]
