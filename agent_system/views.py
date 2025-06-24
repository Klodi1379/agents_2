"""
Enhanced Views for the Agent System

Provides monitoring, management, and configuration interfaces for AI agents.
"""

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.forms import modelform_factory
import asyncio
import json

from .base_agents import communication_hub
from .models import (
    AgentConfiguration, LLMProvider, AgentPromptTemplate, 
    AgentExecutionLog, AgentPerformanceMetrics, AgentConfigurationPreset
)
from .llm_service import llm_manager, initialize_llm_providers
from analysis_engine.models import AgentReport


def is_staff_or_admin(user):
    """Check if user is staff or admin"""
    return user.is_staff or user.is_superuser


@login_required
@require_http_methods(["GET"])
def agent_status_view(request):
    """View to show the status of all agents"""
    
    # Get agent status from communication hub
    hub_status = communication_hub.get_agent_status()
    
    # Get agent configurations from database
    agent_configs = AgentConfiguration.objects.filter(status='active').select_related('llm_provider')
    
    # Get performance metrics from database
    agent_metrics = {}
    for config in agent_configs:
        reports = AgentReport.objects.filter(agent_type=config.agent_type)
        completed_reports = reports.filter(status='COMPLETED')
        
        if completed_reports.exists():
            agent_metrics[config.agent_type] = {
                'name': config.name,
                'total_reports': reports.count(),
                'completed_reports': completed_reports.count(),
                'success_rate': (completed_reports.count() / reports.count()) * 100,
                'average_score': completed_reports.aggregate(avg=Avg('agent_score'))['avg'],
                'average_execution_time': completed_reports.aggregate(
                    avg=Avg('execution_time')
                )['avg'].total_seconds() if completed_reports.aggregate(
                    avg=Avg('execution_time')
                )['avg'] else 0,
                'llm_provider': config.llm_provider.name,
                'model_name': config.model_name,
                'status': config.status,
                'last_updated': config.updated_at,
            }
        else:
            # No reports yet, show basic config info
            agent_metrics[config.agent_type] = {
                'name': config.name,
                'total_reports': 0,
                'completed_reports': 0,
                'success_rate': 0,
                'average_score': None,
                'average_execution_time': 0,
                'llm_provider': config.llm_provider.name,
                'model_name': config.model_name,
                'status': config.status,
                'last_updated': config.updated_at,
            }
    
    context = {
        'hub_status': hub_status,
        'agent_metrics': agent_metrics,
        'agent_configs': agent_configs,
        'title': 'Agent System Status'
    }
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(context)
    
    return render(request, 'agent_system/status.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def agent_configuration_list_view(request):
    """List all agent configurations"""
    
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    agent_type_filter = request.GET.get('agent_type', '')
    status_filter = request.GET.get('status', '')
    provider_filter = request.GET.get('provider', '')
    
    # Build query
    configs = AgentConfiguration.objects.select_related('llm_provider', 'created_by')
    
    if search_query:
        configs = configs.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if agent_type_filter:
        configs = configs.filter(agent_type=agent_type_filter)
    
    if status_filter:
        configs = configs.filter(status=status_filter)
    
    if provider_filter:
        configs = configs.filter(llm_provider__name=provider_filter)
    
    # Pagination
    paginator = Paginator(configs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    agent_types = AgentConfiguration.AGENT_TYPES
    statuses = AgentConfiguration.STATUS_CHOICES
    providers = LLMProvider.objects.filter(is_active=True)
    
    context = {
        'title': 'Agent Configurations',
        'page_obj': page_obj,
        'search_query': search_query,
        'agent_type_filter': agent_type_filter,
        'status_filter': status_filter,
        'provider_filter': provider_filter,
        'agent_types': agent_types,
        'statuses': statuses,
        'providers': providers,
    }
    
    return render(request, 'agent_system/configuration_list.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def agent_configuration_detail_view(request, config_id):
    """Detailed view of agent configuration"""
    
    config = get_object_or_404(AgentConfiguration, id=config_id)
    
    # Get prompt templates
    prompt_templates = config.prompt_templates.filter(is_active=True)
    
    # Get recent execution logs
    recent_logs = config.execution_logs.order_by('-execution_timestamp')[:10]
    
    # Get performance metrics
    try:
        performance = config.performance_metrics
    except AgentPerformanceMetrics.DoesNotExist:
        performance = None
    
    context = {
        'title': f'{config.name} Configuration',
        'config': config,
        'prompt_templates': prompt_templates,
        'recent_logs': recent_logs,
        'performance': performance,
    }
    
    return render(request, 'agent_system/configuration_detail.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def agent_configuration_create_view(request):
    """Create new agent configuration"""
    
    if request.method == 'POST':
        # Handle form submission
        name = request.POST.get('name')
        agent_type = request.POST.get('agent_type')
        description = request.POST.get('description')
        llm_provider_id = request.POST.get('llm_provider')
        model_name = request.POST.get('model_name')
        
        # Validation
        if not all([name, agent_type, description, llm_provider_id, model_name]):
            messages.error(request, 'All required fields must be filled.')
        else:
            try:
                llm_provider = LLMProvider.objects.get(id=llm_provider_id)
                
                config = AgentConfiguration.objects.create(
                    name=name,
                    agent_type=agent_type,
                    description=description,
                    llm_provider=llm_provider,
                    model_name=model_name,
                    temperature=float(request.POST.get('temperature', 0.7)),
                    max_tokens=int(request.POST.get('max_tokens', 4000)),
                    created_by=request.user,
                    updated_by=request.user,
                )
                
                messages.success(request, f'Agent configuration "{name}" created successfully.')
                return redirect('agent_system:configuration_detail', config_id=config.id)
                
            except Exception as e:
                messages.error(request, f'Error creating configuration: {str(e)}')
    
    # Get data for form
    agent_types = AgentConfiguration.AGENT_TYPES
    providers = LLMProvider.objects.filter(is_active=True)
    presets = AgentConfigurationPreset.objects.filter(is_public=True)
    
    context = {
        'title': 'Create Agent Configuration',
        'agent_types': agent_types,
        'providers': providers,
        'presets': presets,
    }
    
    return render(request, 'agent_system/configuration_create.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def llm_provider_list_view(request):
    """List all LLM providers"""
    
    providers = LLMProvider.objects.all().order_by('name')
    
    context = {
        'title': 'LLM Providers',
        'providers': providers,
    }
    
    return render(request, 'agent_system/provider_list.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def llm_provider_create_view(request):
    """Create new LLM provider"""
    
    if request.method == 'POST':
        name = request.POST.get('name')
        provider_type = request.POST.get('provider_type')
        api_endpoint = request.POST.get('api_endpoint')
        api_key = request.POST.get('api_key', '')
        default_model = request.POST.get('default_model')
        
        if not all([name, provider_type, api_endpoint, default_model]):
            messages.error(request, 'All required fields must be filled.')
        else:
            try:
                provider = LLMProvider.objects.create(
                    name=name,
                    provider_type=provider_type,
                    api_endpoint=api_endpoint,
                    api_key=api_key,
                    default_model=default_model,
                    is_local=provider_type in ['lm_studio', 'ollama'],
                    max_tokens=int(request.POST.get('max_tokens', 4000)),
                    temperature=float(request.POST.get('temperature', 0.7)),
                    timeout_seconds=int(request.POST.get('timeout_seconds', 30)),
                )
                
                messages.success(request, f'LLM provider "{name}" created successfully.')
                return redirect('agent_system:provider_list')
                
            except Exception as e:
                messages.error(request, f'Error creating provider: {str(e)}')
    
    provider_types = LLMProvider.PROVIDER_TYPES
    
    context = {
        'title': 'Create LLM Provider',
        'provider_types': provider_types,
    }
    
    return render(request, 'agent_system/provider_create.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def prompt_template_list_view(request, config_id):
    """List prompt templates for an agent configuration"""
    
    config = get_object_or_404(AgentConfiguration, id=config_id)
    templates = config.prompt_templates.all().order_by('prompt_type', 'name')
    
    context = {
        'title': f'{config.name} - Prompt Templates',
        'config': config,
        'templates': templates,
    }
    
    return render(request, 'agent_system/prompt_templates.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def prompt_template_edit_view(request, template_id):
    """Edit prompt template"""
    
    template = get_object_or_404(AgentPromptTemplate, id=template_id)
    
    if request.method == 'POST':
        template.name = request.POST.get('name', template.name)
        template.template = request.POST.get('template', template.template)
        template.notes = request.POST.get('notes', template.notes)
        template.is_active = 'is_active' in request.POST
        
        try:
            # Parse variables from JSON
            variables_json = request.POST.get('variables', '{}')
            template.variables = json.loads(variables_json)
        except json.JSONDecodeError:
            pass
        
        template.save()
        messages.success(request, 'Prompt template updated successfully.')
        return redirect('agent_system:prompt_templates', config_id=template.agent_config.id)
    
    context = {
        'title': f'Edit {template.name}',
        'template': template,
        'variables_json': json.dumps(template.variables, indent=2),
    }
    
    return render(request, 'agent_system/prompt_template_edit.html', context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agent_metrics_view(request):
    """API view to get detailed agent performance metrics"""
    
    metrics = {}
    
    # Get metrics for each agent type
    for agent_type, agent_name in AgentReport.AGENT_TYPES:
        reports = AgentReport.objects.filter(agent_type=agent_type)
        completed_reports = reports.filter(status='COMPLETED')
        failed_reports = reports.filter(status='FAILED')
        
        # Calculate detailed metrics
        total_reports = reports.count()
        success_count = completed_reports.count()
        failure_count = failed_reports.count()
        
        success_rate = (success_count / total_reports * 100) if total_reports > 0 else 0
        
        # Average metrics for successful reports
        avg_score = completed_reports.aggregate(avg=Avg('agent_score'))['avg']
        avg_confidence = completed_reports.aggregate(avg=Avg('confidence'))['avg']
        avg_tokens = completed_reports.aggregate(avg=Avg('token_usage'))['avg']
        avg_cost = completed_reports.aggregate(avg=Avg('cost_estimate'))['avg']
        
        # Execution time statistics
        execution_times = []
        for report in completed_reports:
            if report.execution_time:
                execution_times.append(report.execution_time.total_seconds())
        
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        metrics[agent_type] = {
            'agent_name': agent_name,
            'performance': {
                'total_reports': total_reports,
                'successful_reports': success_count,
                'failed_reports': failure_count,
                'success_rate': round(success_rate, 2),
            },
            'quality_metrics': {
                'average_score': round(float(avg_score), 1) if avg_score else None,
                'average_confidence': round(float(avg_confidence), 1) if avg_confidence else None,
            },
            'efficiency_metrics': {
                'average_execution_time': round(avg_execution_time, 2),
                'average_token_usage': int(avg_tokens) if avg_tokens else None,
                'average_cost': round(float(avg_cost), 4) if avg_cost else None,
            },
            'status': 'active' if agent_type in [name.split('.')[-1] for name in communication_hub.agents.keys()] else 'inactive'
        }
    
    return Response({
        'agent_metrics': metrics,
        'summary': {
            'total_agents': len(AgentReport.AGENT_TYPES),
            'active_agents': len(communication_hub.agents),
            'total_reports': AgentReport.objects.count(),
            'successful_reports': AgentReport.objects.filter(status='COMPLETED').count(),
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_llm_provider_view(request):
    """Test LLM provider connection"""
    
    provider_id = request.data.get('provider_id')
    
    if not provider_id:
        return Response({'error': 'Provider ID required'}, status=400)
    
    try:
        provider = LLMProvider.objects.get(id=provider_id)
        
        # Test the provider using the LLM service
        async def test_provider():
            try:
                if provider.provider_type == 'lm_studio':
                    from .llm_service import LMStudioProvider
                    test_provider = LMStudioProvider(
                        api_endpoint=provider.api_endpoint,
                        default_model=provider.default_model
                    )
                elif provider.provider_type == 'ollama':
                    from .llm_service import OllamaProvider
                    test_provider = OllamaProvider(
                        api_endpoint=provider.api_endpoint,
                        default_model=provider.default_model
                    )
                elif provider.provider_type == 'openai':
                    from .llm_service import OpenAIProvider
                    test_provider = OpenAIProvider(
                        api_key=provider.api_key,
                        default_model=provider.default_model
                    )
                elif provider.provider_type == 'anthropic':
                    from .llm_service import AnthropicProvider
                    test_provider = AnthropicProvider(
                        api_key=provider.api_key,
                        default_model=provider.default_model
                    )
                else:
                    return False, "Unsupported provider type"
                
                result = await test_provider.test_connection()
                return result, "Connection successful" if result else "Connection failed"
                
            except Exception as e:
                return False, str(e)
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success, message = loop.run_until_complete(test_provider())
        loop.close()
        
        return Response({
            'success': success,
            'message': message,
            'provider_name': provider.name
        })
        
    except LLMProvider.DoesNotExist:
        return Response({'error': 'Provider not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def communication_hub_view(request):
    """API view to get communication hub information"""
    
    hub_status = communication_hub.get_agent_status()
    
    # Add recent message queue information
    queue_info = {
        'queue_size': hub_status.get('queue_size', 0),
        'active_workflows': hub_status.get('active_workflows', 0),
    }
    
    return Response({
        'hub_status': hub_status,
        'queue_info': queue_info,
        'registered_agents': list(communication_hub.agents.keys()),
    })


@login_required
@require_http_methods(["GET"])
def agent_detail_view(request, agent_type):
    """View to show detailed information about a specific agent"""
    
    # Validate agent type
    valid_agent_types = dict(AgentReport.AGENT_TYPES)
    if agent_type not in valid_agent_types:
        return JsonResponse({'error': 'Invalid agent type'}, status=404)
    
    agent_name = valid_agent_types[agent_type]
    
    # Get agent configuration
    try:
        agent_config = AgentConfiguration.objects.get(agent_type=agent_type)
    except AgentConfiguration.DoesNotExist:
        agent_config = None
    
    # Get agent reports
    reports = AgentReport.objects.filter(agent_type=agent_type).order_by('-created_at')
    
    # Calculate metrics
    total_reports = reports.count()
    completed_reports = reports.filter(status='COMPLETED')
    success_rate = (completed_reports.count() / total_reports * 100) if total_reports > 0 else 0
    
    # Recent activity (last 10 reports)
    recent_reports = reports[:10]
    
    context = {
        'agent_type': agent_type,
        'agent_name': agent_name,
        'agent_config': agent_config,
        'total_reports': total_reports,
        'success_rate': round(success_rate, 1),
        'recent_reports': [
            {
                'id': report.id,
                'business_idea_title': report.business_idea.title,
                'status': report.status,
                'score': report.agent_score,
                'created_at': report.created_at.isoformat(),
                'execution_time': report.execution_time.total_seconds() if report.execution_time else None,
            }
            for report in recent_reports
        ]
    }
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(context)
    
    return render(request, 'agent_system/agent_detail.html', context)
@login_required
def api_available_agents(request):
    """API endpoint to get available agents for quick select"""
    try:
        agents = AgentConfiguration.objects.filter(status='active').select_related('llm_provider')
        
        agents_data = []
        for agent in agents:
            agents_data.append({
                'id': agent.id,
                'name': agent.name,
                'description': agent.description,
                'agent_type': agent.get_agent_type_display(),
                'capabilities': agent.capabilities,
                'status': agent.status,
                'model_name': agent.model_name,
                'provider': agent.llm_provider.name
            })
        
        return JsonResponse({
            'success': True,
            'agents': agents_data
        })
        
    except Exception as e:
        logger.error(f"Error getting available agents: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def config_list(request):
    """List all agent configurations (alias for compatibility)"""
    return agent_configuration_list_view(request)


@login_required  
def config_create(request):
    """Create new agent configuration (alias for compatibility)"""
    return agent_configuration_create_view(request)


@login_required
def config_edit(request, config_id):
    """Edit agent configuration"""
    config = get_object_or_404(AgentConfiguration, id=config_id)
    
    if request.method == 'POST':
        # Handle form submission
        try:
            config.name = request.POST.get('name')
            config.description = request.POST.get('description', '')
            config.temperature = float(request.POST.get('temperature', 0.7))
            config.max_tokens = int(request.POST.get('max_tokens', 2048))
            
            # Parse capabilities from comma-separated string
            capabilities_str = request.POST.get('capabilities', '')
            if capabilities_str:
                config.capabilities = [cap.strip() for cap in capabilities_str.split(',') if cap.strip()]
            
            config.updated_by = request.user
            config.save()
            
            # Update system prompt if provided
            system_prompt = request.POST.get('system_prompt')
            if system_prompt:
                prompt_template, created = AgentPromptTemplate.objects.get_or_create(
                    agent_config=config,
                    prompt_type='system',
                    name='Default System Prompt',
                    defaults={'template': system_prompt, 'is_active': True}
                )
                if not created:
                    prompt_template.template = system_prompt
                    prompt_template.save()
            
            messages.success(request, f'Agent "{config.name}" updated successfully!')
            return redirect('agent_system:config_list')
            
        except Exception as e:
            logger.error(f"Error updating agent configuration: {str(e)}")
            messages.error(request, f'Error updating agent: {str(e)}')
    
    # GET request - show form
    # Get system prompt from templates
    system_prompt_template = config.prompt_templates.filter(
        prompt_type='system', 
        is_active=True
    ).first()
    
    context = {
        'config': config,
        'agent_types': AgentConfiguration.AGENT_TYPES,
        'llm_providers': LLMProvider.objects.filter(is_active=True),
        'system_prompt': system_prompt_template.template if system_prompt_template else '',
        'capabilities_str': ', '.join(config.capabilities) if config.capabilities else '',
        'title': f'Edit {config.name}'
    }
    return render(request, 'agent_system/config_edit.html', context)


@login_required
def execute_agent(request, config_id):
    """Execute agent with chat interface"""
    config = get_object_or_404(AgentConfiguration, id=config_id)
    
    if request.method == 'POST':
        # Handle chat message
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            
            if not message.strip():
                return JsonResponse({'success': False, 'error': 'Message cannot be empty'})
            
            # Import ConfigurableAgent here to avoid circular imports
            from business_agents import ConfigurableAgent
            
            # Create agent instance
            agent = ConfigurableAgent(config)
            
            # Execute agent
            response = agent.execute(message)
            
            return JsonResponse({
                'success': True,
                'response': response,
                'agent_name': config.name
            })
            
        except Exception as e:
            logger.error(f"Error executing agent {config.name}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error executing agent: {str(e)}'
            })
    
    # GET request - show chat interface
    context = {
        'config': config,
        'title': f'Chat with {config.name}'
    }
    return render(request, 'agent_system/execute.html', context)


# Import logging here to avoid issues
import logging
logger = logging.getLogger(__name__)
