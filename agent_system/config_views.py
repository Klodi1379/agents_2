"""
Enhanced Views for Agent Configuration Management

Additional views for comprehensive agent configuration, LLM provider management,
and agent testing capabilities.
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
from .services import (
    AgentConfigurationService, AgentExecutionService, 
    setup_default_agent_system, test_agent_configuration
)
from analysis_engine.models import AgentReport


@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def agent_management_dashboard_view(request):
    """Main dashboard for agent management"""
    
    # Get overview statistics
    total_configs = AgentConfiguration.objects.count()
    active_configs = AgentConfiguration.objects.filter(status='active').count()
    total_providers = LLMProvider.objects.count()
    active_providers = LLMProvider.objects.filter(is_active=True).count()
    
    # Recent activity
    recent_logs = AgentExecutionLog.objects.order_by('-execution_timestamp')[:10]
    
    # Performance summary
    performance_summary = {}
    for config in AgentConfiguration.objects.filter(status='active'):
        try:
            metrics = config.performance_metrics
            performance_summary[config.agent_type] = {
                'name': config.name,
                'success_rate': metrics.success_rate(),
                'avg_execution_time': metrics.average_execution_time,
                'total_executions': metrics.total_executions,
                'last_execution': metrics.last_execution_at
            }
        except AgentPerformanceMetrics.DoesNotExist:
            performance_summary[config.agent_type] = {
                'name': config.name,
                'success_rate': 0,
                'avg_execution_time': 0,
                'total_executions': 0,
                'last_execution': None
            }
    
    context = {
        'title': 'Agent Management Dashboard',
        'stats': {
            'total_configs': total_configs,
            'active_configs': active_configs,
            'total_providers': total_providers,
            'active_providers': active_providers,
        },
        'recent_logs': recent_logs,
        'performance_summary': performance_summary,
    }
    
    return render(request, 'agent_system/management_dashboard.html', context)


@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def agent_configuration_edit_view(request, config_id):
    """Edit agent configuration"""
    
    config = get_object_or_404(AgentConfiguration, id=config_id)
    
    if request.method == 'POST':
        # Update configuration
        config.name = request.POST.get('name', config.name)
        config.description = request.POST.get('description', config.description)
        config.status = request.POST.get('status', config.status)
        
        # LLM settings
        llm_provider_id = request.POST.get('llm_provider')
        if llm_provider_id:
            try:
                config.llm_provider = LLMProvider.objects.get(id=llm_provider_id)
            except LLMProvider.DoesNotExist:
                pass
        
        config.model_name = request.POST.get('model_name', config.model_name)
        config.temperature = float(request.POST.get('temperature', config.temperature))
        config.max_tokens = int(request.POST.get('max_tokens', config.max_tokens))
        config.top_p = float(request.POST.get('top_p', config.top_p))
        config.frequency_penalty = float(request.POST.get('frequency_penalty', config.frequency_penalty))
        config.presence_penalty = float(request.POST.get('presence_penalty', config.presence_penalty))
        
        # Performance settings
        config.timeout_seconds = int(request.POST.get('timeout_seconds', config.timeout_seconds))
        config.max_retries = int(request.POST.get('max_retries', config.max_retries))
        
        # Capabilities and tags
        capabilities_str = request.POST.get('capabilities', '')
        if capabilities_str:
            config.capabilities = [cap.strip() for cap in capabilities_str.split(',')]
        
        tags_str = request.POST.get('tags', '')
        if tags_str:
            config.tags = [tag.strip() for tag in tags_str.split(',')]
        
        config.updated_by = request.user
        config.save()
        
        messages.success(request, f'Configuration for {config.name} updated successfully.')
        return redirect('agent_system:configuration_detail', config_id=config.id)
    
    # Get available providers
    providers = LLMProvider.objects.filter(is_active=True)
    
    context = {
        'title': f'Edit {config.name}',
        'config': config,
        'providers': providers,
        'status_choices': AgentConfiguration.STATUS_CHOICES,
        'capabilities_str': ', '.join(config.capabilities) if config.capabilities else '',
        'tags_str': ', '.join(config.tags) if config.tags else '',
    }
    
    return render(request, 'agent_system/configuration_edit.html', context)


@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def llm_provider_edit_view(request, provider_id):
    """Edit LLM provider configuration"""
    
    provider = get_object_or_404(LLMProvider, id=provider_id)
    
    if request.method == 'POST':
        provider.name = request.POST.get('name', provider.name)
        provider.api_endpoint = request.POST.get('api_endpoint', provider.api_endpoint)
        provider.api_key = request.POST.get('api_key', provider.api_key)
        provider.default_model = request.POST.get('default_model', provider.default_model)
        provider.max_tokens = int(request.POST.get('max_tokens', provider.max_tokens))
        provider.temperature = float(request.POST.get('temperature', provider.temperature))
        provider.timeout_seconds = int(request.POST.get('timeout_seconds', provider.timeout_seconds))
        provider.cost_per_1k_tokens = float(request.POST.get('cost_per_1k_tokens', provider.cost_per_1k_tokens))
        provider.is_active = 'is_active' in request.POST
        
        provider.save()
        messages.success(request, f'Provider {provider.name} updated successfully.')
        return redirect('agent_system:provider_list')
    
    context = {
        'title': f'Edit {provider.name}',
        'provider': provider,
        'provider_types': LLMProvider.PROVIDER_TYPES,
    }
    
    return render(request, 'agent_system/provider_edit.html', context)


@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def prompt_template_create_view(request, config_id):
    """Create new prompt template"""
    
    config = get_object_or_404(AgentConfiguration, id=config_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        prompt_type = request.POST.get('prompt_type')
        template = request.POST.get('template')
        notes = request.POST.get('notes', '')
        
        if not all([name, prompt_type, template]):
            messages.error(request, 'Name, type, and template are required.')
        else:
            try:
                # Parse variables from JSON
                variables_json = request.POST.get('variables', '{}')
                variables = json.loads(variables_json) if variables_json else {}
            except json.JSONDecodeError:
                variables = {}
            
            prompt_template = AgentPromptTemplate.objects.create(
                agent_config=config,
                prompt_type=prompt_type,
                name=name,
                template=template,
                variables=variables,
                notes=notes,
                is_active=True,
                version='1.0.0'
            )
            
            messages.success(request, f'Prompt template "{name}" created successfully.')
            return redirect('agent_system:prompt_templates', config_id=config.id)
    
    context = {
        'title': f'Create Prompt Template for {config.name}',
        'config': config,
        'prompt_types': AgentPromptTemplate.PROMPT_TYPES,
    }
    
    return render(request, 'agent_system/prompt_template_create.html', context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_default_system_view(request):
    """API endpoint to set up default agent system"""
    
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=403)
    
    try:
        agents = setup_default_agent_system()
        
        return Response({
            'success': True,
            'message': f'Default agent system set up successfully with {len(agents)} agents',
            'agents_created': [agent.name for agent in agents]
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_agent_configuration_view(request, config_id):
    """Test an agent configuration"""
    
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=403)
    
    try:
        config = AgentConfiguration.objects.get(id=config_id)
        
        # Run the test asynchronously
        async def run_test():
            return await test_agent_configuration(config)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_test())
        loop.close()
        
        return Response({
            'success': True,
            'test_result': result
        })
        
    except AgentConfiguration.DoesNotExist:
        return Response({'error': 'Agent configuration not found'}, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agent_execution_logs_view(request, config_id):
    """Get execution logs for an agent configuration"""
    
    try:
        config = AgentConfiguration.objects.get(id=config_id)
        logs = config.execution_logs.order_by('-execution_timestamp')
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_logs = logs[start:end]
        
        logs_data = []
        for log in paginated_logs:
            logs_data.append({
                'id': log.id,
                'status': log.status,
                'execution_time': log.execution_time_seconds,
                'token_usage': log.token_usage,
                'cost': float(log.estimated_cost),
                'timestamp': log.execution_timestamp.isoformat(),
                'error_message': log.error_message,
                'business_idea_id': log.business_idea_id,
            })
        
        return Response({
            'logs': logs_data,
            'total_count': logs.count(),
            'page': page,
            'page_size': page_size,
            'has_next': end < logs.count()
        })
        
    except AgentConfiguration.DoesNotExist:
        return Response({'error': 'Agent configuration not found'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initialize_llm_providers_view(request):
    """Initialize LLM providers"""
    
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=403)
    
    try:
        # Run async initialization
        async def run_init():
            return await initialize_llm_providers()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(run_init())
        loop.close()
        
        return Response({
            'success': True,
            'provider_test_results': results,
            'available_providers': llm_manager.get_available_providers()
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def agent_configuration_clone_view(request, config_id):
    """Clone an existing agent configuration"""
    
    original_config = get_object_or_404(AgentConfiguration, id=config_id)
    
    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        new_agent_type = request.POST.get('new_agent_type')
        
        if not new_name:
            messages.error(request, 'New name is required.')
        else:
            # Clone the configuration
            new_config = AgentConfiguration.objects.create(
                agent_type=new_agent_type or original_config.agent_type,
                name=new_name,
                description=f"Cloned from {original_config.name}",
                version="1.0.0",
                status='inactive',  # Start as inactive
                llm_provider=original_config.llm_provider,
                model_name=original_config.model_name,
                temperature=original_config.temperature,
                max_tokens=original_config.max_tokens,
                top_p=original_config.top_p,
                frequency_penalty=original_config.frequency_penalty,
                presence_penalty=original_config.presence_penalty,
                capabilities=original_config.capabilities.copy(),
                required_data_sources=original_config.required_data_sources.copy(),
                tags=original_config.tags.copy(),
                timeout_seconds=original_config.timeout_seconds,
                max_retries=original_config.max_retries,
                retry_delay_seconds=original_config.retry_delay_seconds,
                created_by=request.user,
                updated_by=request.user,
            )
            
            # Clone prompt templates
            for template in original_config.prompt_templates.all():
                AgentPromptTemplate.objects.create(
                    agent_config=new_config,
                    prompt_type=template.prompt_type,
                    name=template.name,
                    template=template.template,
                    variables=template.variables.copy(),
                    is_active=template.is_active,
                    version=template.version,
                    notes=f"Cloned from {original_config.name}"
                )
            
            # Create performance metrics
            AgentPerformanceMetrics.objects.create(agent_config=new_config)
            
            messages.success(request, f'Configuration cloned successfully as "{new_name}".')
            return redirect('agent_system:configuration_detail', config_id=new_config.id)
    
    context = {
        'title': f'Clone {original_config.name}',
        'original_config': original_config,
        'agent_types': AgentConfiguration.AGENT_TYPES,
    }
    
    return render(request, 'agent_system/configuration_clone.html', context)


@login_required
@user_passes_test(lambda user: user.is_staff or user.is_superuser)
def configuration_presets_view(request):
    """Manage configuration presets"""
    
    presets = AgentConfigurationPreset.objects.filter(
        Q(is_public=True) | Q(created_by=request.user)
    ).order_by('agent_type', 'name')
    
    context = {
        'title': 'Configuration Presets',
        'presets': presets,
    }
    
    return render(request, 'agent_system/configuration_presets.html', context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_preset_from_config_view(request, config_id):
    """Create a preset from an existing configuration"""
    
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=403)
    
    try:
        config = AgentConfiguration.objects.get(id=config_id)
        preset_name = request.data.get('preset_name')
        description = request.data.get('description', '')
        is_public = request.data.get('is_public', False)
        
        if not preset_name:
            return Response({'error': 'Preset name is required'}, status=400)
        
        # Create config data
        config_data = {
            'name': preset_name,
            'description': description,
            'llm_provider_type': config.llm_provider.provider_type,
            'model_name': config.model_name,
            'temperature': config.temperature,
            'max_tokens': config.max_tokens,
            'capabilities': config.capabilities,
            'tags': config.tags,
        }
        
        # Get prompt templates
        prompt_templates = []
        for template in config.prompt_templates.filter(is_active=True):
            prompt_templates.append({
                'prompt_type': template.prompt_type,
                'name': template.name,
                'template': template.template,
                'variables': template.variables,
            })
        
        preset = AgentConfigurationPreset.objects.create(
            name=preset_name,
            description=description,
            agent_type=config.agent_type,
            config_data=config_data,
            prompt_templates=prompt_templates,
            is_public=is_public,
            created_by=request.user
        )
        
        return Response({
            'success': True,
            'preset_id': preset.id,
            'message': f'Preset "{preset_name}" created successfully'
        })
        
    except AgentConfiguration.DoesNotExist:
        return Response({'error': 'Agent configuration not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
