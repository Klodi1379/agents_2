"""
Celery Configuration for AI Company

This file configures Celery for handling background tasks like AI agent
orchestration and business analysis processing.
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_company.settings')

app = Celery('ai_company')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery beat schedule for periodic tasks (optional - can be removed if not needed)
app.conf.beat_schedule = {
    # Uncomment these when you want periodic tasks
    # 'cleanup-failed-tasks': {
    #     'task': 'analysis_engine.tasks.cleanup_failed_tasks',
    #     'schedule': 300.0,  # Run every 5 minutes
    # },
    # 'update-agent-metrics': {
    #     'task': 'analysis_engine.tasks.update_agent_metrics',
    #     'schedule': 600.0,  # Run every 10 minutes
    # },
}

app.conf.timezone = 'UTC'

# Task routing - send different types of tasks to different queues
app.conf.task_routes = {
    'analysis_engine.tasks.orchestrate_business_analysis': {'queue': 'analysis'},
    'analysis_engine.tasks.analyze_with_agent': {'queue': 'agents'},
    'analysis_engine.tasks.create_final_analysis_report': {'queue': 'reports'},
    'analysis_engine.tasks.generate_business_ideas': {'queue': 'generation'},
}

# Task configuration
app.conf.update(
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Task execution
    task_always_eager=settings.DEBUG,  # Run tasks synchronously in development
    task_eager_propagates=True,
    
    # Result backend configuration
    result_expires=3600,  # Results expire after 1 hour
    result_persistent=True,
    
    # Task routing
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
    
    # Worker configuration
    worker_prefetch_multiplier=1,  # Prevent workers from grabbing too many tasks
    worker_max_tasks_per_child=1000,  # Restart workers after 1000 tasks
    worker_disable_rate_limits=False,
    
    # Task time limits
    task_soft_time_limit=300,  # 5 minutes soft limit
    task_time_limit=600,  # 10 minutes hard limit
    
    # Task retry configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration"""
    print(f'Request: {self.request!r}')
    return 'Debug task completed'
