"""
Dashboard Views

Provides the main web interface for the AI Company platform.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
import json

from analysis_engine.models import (
    BusinessIdea, AgentReport, FinalAnalysisReport, 
    IdeaGenerationRequest
)
from analysis_engine.tasks import orchestrate_business_analysis


def home_view(request):
    """Landing page - redirects to dashboard if authenticated"""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    context = {
        'title': 'AI Company - Autonomous Business Analysis',
        'description': 'Get comprehensive business analysis from our AI agents'
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def dashboard_view(request):
    """Main dashboard view"""
    
    user_ideas = BusinessIdea.objects.filter(submitted_by=request.user)
    
    # Dashboard statistics
    total_ideas = user_ideas.count()
    completed_analyses = user_ideas.filter(status='COMPLETED').count()
    in_progress = user_ideas.filter(status__in=['ANALYZING', 'QUEUE']).count()
    
    # Recent activity
    recent_ideas = user_ideas.order_by('-submitted_at')[:5]
    
    # Performance metrics
    completed_ideas = user_ideas.filter(status='COMPLETED', overall_score__isnull=False)
    avg_score = completed_ideas.aggregate(avg=Avg('overall_score'))['avg']
    
    # Status distribution for chart
    status_distribution = user_ideas.values('status').annotate(
        count=Count('status')
    ).order_by('status')
    
    # Recent activity timeline
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_activity = user_ideas.filter(
        submitted_at__gte=thirty_days_ago
    ).order_by('-submitted_at')
    
    context = {
        'title': 'Dashboard',
        'total_ideas': total_ideas,
        'completed_analyses': completed_analyses,
        'in_progress': in_progress,
        'average_score': round(avg_score, 1) if avg_score else None,
        'recent_ideas': recent_ideas,
        'status_distribution': list(status_distribution),
        'recent_activity': recent_activity,
        'completion_rate': (completed_analyses / total_ideas * 100) if total_ideas > 0 else 0,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def submit_idea_view(request):
    """Submit a new business idea for analysis"""
    
    if request.method == 'POST':
        # Extract form data
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        industry = request.POST.get('industry', 'OTHER')
        target_market = request.POST.get('target_market', '').strip()
        estimated_budget = request.POST.get('estimated_budget')
        
        # Basic validation
        errors = []
        if not title or len(title) < 5:
            errors.append("Title must be at least 5 characters long")
        if not description or len(description) < 20:
            errors.append("Description must be at least 20 characters long")
        
        # Convert budget to decimal if provided
        budget_value = None
        if estimated_budget:
            try:
                budget_value = float(estimated_budget)
                if budget_value < 0:
                    errors.append("Budget cannot be negative")
            except ValueError:
                errors.append("Invalid budget amount")
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Create the business idea
            business_idea = BusinessIdea.objects.create(
                title=title,
                description=description,
                industry=industry,
                target_market=target_market,
                estimated_budget=budget_value,
                submitted_by=request.user
            )
            
            # Trigger analysis
            try:
                orchestrate_business_analysis.delay(str(business_idea.id))
                messages.success(request, f'Business idea "{title}" submitted successfully! Analysis is starting...')
                return redirect('dashboard:idea_detail', idea_id=business_idea.id)
            except Exception as e:
                messages.error(request, f'Failed to start analysis: {str(e)}')
    
    # Industry choices for the form
    industry_choices = BusinessIdea.INDUSTRY_CHOICES
    
    context = {
        'title': 'Submit New Business Idea',
        'industry_choices': industry_choices,
    }
    
    return render(request, 'dashboard/submit_idea.html', context)


@login_required
def ideas_list_view(request):
    """List all user's business ideas with filtering and pagination"""
    
    user_ideas = BusinessIdea.objects.filter(submitted_by=request.user)
    
    # Filtering
    status_filter = request.GET.get('status')
    industry_filter = request.GET.get('industry')
    search_query = request.GET.get('search')
    
    if status_filter:
        user_ideas = user_ideas.filter(status=status_filter)
    
    if industry_filter:
        user_ideas = user_ideas.filter(industry=industry_filter)
    
    if search_query:
        user_ideas = user_ideas.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Ordering
    order_by = request.GET.get('order_by', '-submitted_at')
    user_ideas = user_ideas.order_by(order_by)
    
    # Pagination
    paginator = Paginator(user_ideas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Filter options for the template
    status_choices = BusinessIdea.STATUS_CHOICES
    industry_choices = BusinessIdea.INDUSTRY_CHOICES
    
    context = {
        'title': 'My Business Ideas',
        'page_obj': page_obj,
        'status_filter': status_filter,
        'industry_filter': industry_filter,
        'search_query': search_query,
        'order_by': order_by,
        'status_choices': status_choices,
        'industry_choices': industry_choices,
    }
    
    return render(request, 'dashboard/ideas_list.html', context)


@login_required
def idea_detail_view(request, idea_id):
    """Detailed view of a specific business idea and its analysis"""
    
    # Get the business idea (ensure user owns it)
    business_idea = get_object_or_404(
        BusinessIdea, 
        id=idea_id, 
        submitted_by=request.user
    )
    
    # Get all agent reports
    agent_reports = AgentReport.objects.filter(
        business_idea=business_idea
    ).order_by('created_at')
    
    # Get final report if available
    final_report = None
    try:
        final_report = FinalAnalysisReport.objects.get(business_idea=business_idea)
    except FinalAnalysisReport.DoesNotExist:
        pass
    
    # Calculate progress
    total_agent_types = len(AgentReport.AGENT_TYPES)
    completed_reports = agent_reports.filter(status='COMPLETED').count()
    progress_percentage = (completed_reports / total_agent_types * 100) if total_agent_types > 0 else 0
    
    # Group reports by agent type for better display
    reports_by_agent = {}
    for report in agent_reports:
        reports_by_agent[report.agent_type] = report
    
    # Add missing agent types as "pending"
    for agent_type, agent_name in AgentReport.AGENT_TYPES:
        if agent_type not in reports_by_agent:
            reports_by_agent[agent_type] = {
                'agent_type': agent_type,
                'agent_name': agent_name,
                'status': 'PENDING',
                'created_at': None
            }
    
    context = {
        'title': f'Analysis: {business_idea.title}',
        'business_idea': business_idea,
        'agent_reports': agent_reports,
        'reports_by_agent': reports_by_agent,
        'final_report': final_report,
        'progress_percentage': round(progress_percentage, 1),
        'is_complete': business_idea.status == 'COMPLETED',
        'agent_types': dict(AgentReport.AGENT_TYPES),
    }
    
    return render(request, 'dashboard/idea_detail.html', context)


@login_required
def agent_report_detail_view(request, report_id):
    """Detailed view of a specific agent report"""
    
    # Get the agent report (ensure user owns the business idea)
    agent_report = get_object_or_404(
        AgentReport,
        id=report_id,
        business_idea__submitted_by=request.user
    )
    
    # Parse structured data for better display
    structured_data = agent_report.structured_data
    structured_data_json = json.dumps(structured_data, indent=2) if structured_data else None
    
    context = {
        'title': f'{agent_report.get_agent_type_display()} Report',
        'agent_report': agent_report,
        'business_idea': agent_report.business_idea,
        'structured_data_json': structured_data_json,
    }
    
    return render(request, 'dashboard/agent_report_detail.html', context)


@login_required
def analytics_view(request):
    """Analytics and insights dashboard"""
    
    user_ideas = BusinessIdea.objects.filter(submitted_by=request.user)
    
    # Time-based analytics (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_data = []
    
    for i in range(6):
        month_start = six_months_ago + timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        month_ideas = user_ideas.filter(
            submitted_at__gte=month_start,
            submitted_at__lt=month_end
        )
        
        completed_month = month_ideas.filter(status='COMPLETED')
        avg_score = completed_month.aggregate(avg=Avg('overall_score'))['avg']
        
        monthly_data.append({
            'month': month_start.strftime('%B %Y'),
            'ideas_submitted': month_ideas.count(),
            'analyses_completed': completed_month.count(),
            'average_score': round(avg_score, 1) if avg_score else 0,
        })
    
    # Industry performance
    industry_performance = user_ideas.filter(
        status='COMPLETED',
        overall_score__isnull=False
    ).values('industry').annotate(
        count=Count('industry'),
        avg_score=Avg('overall_score')
    ).order_by('-avg_score')
    
    # Top and bottom performing ideas
    completed_ideas = user_ideas.filter(
        status='COMPLETED',
        overall_score__isnull=False
    ).order_by('-overall_score')
    
    top_ideas = completed_ideas[:5]
    bottom_ideas = completed_ideas.reverse()[:5]
    
    # Agent performance from user's perspective
    user_reports = AgentReport.objects.filter(
        business_idea__submitted_by=request.user,
        status='COMPLETED'
    )
    
    agent_performance = user_reports.values('agent_type').annotate(
        count=Count('agent_type'),
        avg_score=Avg('agent_score'),
        avg_confidence=Avg('confidence')
    ).order_by('-avg_score')
    
    context = {
        'title': 'Analytics & Insights',
        'monthly_data': monthly_data,
        'industry_performance': list(industry_performance),
        'top_ideas': top_ideas,
        'bottom_ideas': bottom_ideas,
        'agent_performance': list(agent_performance),
        'total_ideas': user_ideas.count(),
        'completed_ideas': user_ideas.filter(status='COMPLETED').count(),
    }
    
    return render(request, 'dashboard/analytics.html', context)


# AJAX endpoint for real-time updates
@login_required
def idea_status_ajax(request, idea_id):
    """AJAX endpoint to get real-time status updates for an idea"""
    
    business_idea = get_object_or_404(
        BusinessIdea,
        id=idea_id,
        submitted_by=request.user
    )
    
    # Get agent reports progress
    agent_reports = AgentReport.objects.filter(business_idea=business_idea)
    total_agents = len(AgentReport.AGENT_TYPES)
    completed_reports = agent_reports.filter(status='COMPLETED').count()
    failed_reports = agent_reports.filter(status='FAILED').count()
    in_progress_reports = agent_reports.filter(status='IN_PROGRESS').count()
    
    progress_percentage = (completed_reports / total_agents * 100) if total_agents > 0 else 0
    
    # Agent status summary
    agent_status = {}
    for report in agent_reports:
        agent_status[report.agent_type] = {
            'status': report.status,
            'score': report.agent_score,
            'created_at': report.created_at.isoformat() if report.created_at else None,
        }
    
    # Add pending agents
    for agent_type, agent_name in AgentReport.AGENT_TYPES:
        if agent_type not in agent_status:
            agent_status[agent_type] = {
                'status': 'PENDING',
                'score': None,
                'created_at': None,
            }
    
    return JsonResponse({
        'status': business_idea.status,
        'overall_score': business_idea.overall_score,
        'recommendation': business_idea.recommendation,
        'progress_percentage': round(progress_percentage, 1),
        'completed_reports': completed_reports,
        'failed_reports': failed_reports,
        'in_progress_reports': in_progress_reports,
        'agent_status': agent_status,
        'is_complete': business_idea.status == 'COMPLETED',
        'last_updated': business_idea.updated_at.isoformat(),
    })


# Authentication views (using Django's built-in views with custom templates)
class CustomLoginView(auth_views.LoginView):
    template_name = 'dashboard/auth/login.html'
    success_url = '/dashboard/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sign In'
        return context
    
    def get_success_url(self):
        return self.success_url


class CustomLogoutView(auth_views.LogoutView):
    next_page = 'dashboard:home'


def register_view(request):
    """User registration view"""
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! You can now sign in.')
            return redirect('dashboard:login')
    else:
        form = UserCreationForm()
    
    context = {
        'title': 'Create Account',
        'form': form,
    }
    
    return render(request, 'dashboard/auth/register.html', context)
