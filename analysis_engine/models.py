from django.db import models
import uuid
from django.contrib.auth.models import User


class BusinessIdea(models.Model):
    """Core model representing a business idea to be analyzed"""
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Metadata
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Business Context
    INDUSTRY_CHOICES = [
        ('TECH', 'Technology'),
        ('HEALTHCARE', 'Healthcare'),
        ('FINANCE', 'Finance'),
        ('EDUCATION', 'Education'),
        ('RETAIL', 'Retail'),
        ('MANUFACTURING', 'Manufacturing'),
        ('SERVICES', 'Services'),
        ('OTHER', 'Other'),
    ]
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES, default='OTHER')
    target_market = models.CharField(max_length=255, blank=True)
    estimated_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Analysis Status
    STATUS_CHOICES = [
        ('PENDING', 'Pending Analysis'),
        ('QUEUE', 'In Queue'),
        ('ANALYZING', 'Being Analyzed'),
        ('COMPLETED', 'Analysis Complete'),
        ('FAILED', 'Analysis Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Results Summary
    overall_score = models.IntegerField(null=True, blank=True, help_text="Overall viability score 1-100")
    recommendation = models.CharField(max_length=50, blank=True)
    confidence_level = models.CharField(max_length=20, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['industry']),
            models.Index(fields=['overall_score']),
        ]

    def __str__(self):
        return f"{self.title} ({self.status})"

    @property
    def is_analysis_complete(self):
        return self.status == 'COMPLETED'
    
    @property
    def progress_percentage(self):
        """Calculate analysis progress based on completed reports"""
        total_agents = AgentReport.AGENT_TYPES.__len__()
        completed_reports = self.agent_reports.count()
        return (completed_reports / total_agents) * 100 if total_agents > 0 else 0


class AgentReport(models.Model):
    """Individual analysis report from each AI agent"""
    
    AGENT_TYPES = [
        ('CEO', 'Chief Executive Officer'),
        ('MARKET_RESEARCH', 'Market Research Analyst'),
        ('FINANCIAL', 'Financial Analyst'),
        ('MARKETING', 'Marketing Strategist'),
        ('TECH_LEAD', 'Technical Lead'),
        ('RISK_ANALYST', 'Risk Analyst'),
        ('LEGAL', 'Legal Advisor'),
        ('HR', 'Human Resources'),
        ('OPERATIONS', 'Operations Manager'),
    ]
    
    # Relationships
    business_idea = models.ForeignKey(BusinessIdea, related_name='agent_reports', on_delete=models.CASCADE)
    agent_type = models.CharField(max_length=20, choices=AGENT_TYPES)
    
    # Report Content
    report_content = models.TextField()
    structured_data = models.JSONField(default=dict, blank=True)  # For machine-readable data
    agent_score = models.IntegerField(null=True, blank=True, help_text="Agent's individual score 1-100")
    confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Execution Details
    created_at = models.DateTimeField(auto_now_add=True)
    execution_time = models.DurationField(null=True, blank=True)
    llm_model_used = models.CharField(max_length=50, blank=True)
    token_usage = models.IntegerField(null=True, blank=True)
    cost_estimate = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('RETRYING', 'Retrying'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['business_idea', 'agent_type']
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['agent_type', 'status']),
            models.Index(fields=['business_idea', 'status']),
        ]

    def __str__(self):
        return f"{self.get_agent_type_display()} report for {self.business_idea.title}"


class FinalAnalysisReport(models.Model):
    """Comprehensive final report combining all agent analyses"""
    
    business_idea = models.OneToOneField(BusinessIdea, on_delete=models.CASCADE, related_name='final_report')
    
    # Executive Summary
    executive_summary = models.TextField()
    key_findings = models.JSONField(default=list)  # List of key insights
    recommendations = models.JSONField(default=list)  # List of recommendations
    
    # Detailed Analysis
    market_analysis = models.TextField(blank=True)
    financial_projections = models.JSONField(default=dict)
    risk_assessment = models.TextField(blank=True)
    technical_feasibility = models.TextField(blank=True)
    
    # Scoring
    market_score = models.IntegerField(null=True, blank=True)
    financial_score = models.IntegerField(null=True, blank=True)
    technical_score = models.IntegerField(null=True, blank=True)
    risk_score = models.IntegerField(null=True, blank=True)
    overall_score = models.IntegerField(null=True, blank=True)
    
    # Decision
    RECOMMENDATION_CHOICES = [
        ('PROCEED', 'Proceed with Implementation'),
        ('PROCEED_CAUTION', 'Proceed with Caution'),
        ('MODIFY', 'Modify and Re-evaluate'),
        ('DELAY', 'Delay Implementation'),
        ('REJECT', 'Do Not Proceed'),
    ]
    final_recommendation = models.CharField(max_length=20, choices=RECOMMENDATION_CHOICES, blank=True)
    confidence_level = models.CharField(max_length=20, blank=True)
    
    # Generation Details
    created_at = models.DateTimeField(auto_now_add=True)
    generated_by_agent = models.CharField(max_length=50, default='CEO')
    total_cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Final Report: {self.business_idea.title}"


class AnalysisTask(models.Model):
    """Track background tasks for analysis processing"""
    
    business_idea = models.ForeignKey(BusinessIdea, on_delete=models.CASCADE, related_name='analysis_tasks')
    task_id = models.CharField(max_length=255, unique=True)  # Celery task ID
    agent_type = models.CharField(max_length=20, choices=AgentReport.AGENT_TYPES, blank=True)
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('STARTED', 'Started'),
        ('SUCCESS', 'Success'),
        ('FAILURE', 'Failure'),
        ('RETRY', 'Retry'),
        ('REVOKED', 'Revoked'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    result = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Task {self.task_id} - {self.agent_type} for {self.business_idea.title}"


class IdeaGenerationRequest(models.Model):
    """Request for AI to generate new business ideas"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Request Parameters
    industry_focus = models.CharField(max_length=20, choices=BusinessIdea.INDUSTRY_CHOICES, blank=True)
    budget_range = models.CharField(max_length=50, blank=True)
    target_audience = models.CharField(max_length=255, blank=True)
    innovation_level = models.CharField(max_length=20, choices=[
        ('LOW', 'Incremental Innovation'),
        ('MEDIUM', 'Moderate Innovation'),
        ('HIGH', 'Disruptive Innovation'),
    ], default='MEDIUM')
    
    # Additional Constraints
    geographic_focus = models.CharField(max_length=100, blank=True)
    technology_preferences = models.TextField(blank=True)
    avoid_sectors = models.TextField(blank=True)
    
    # Request Status
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('GENERATING', 'Generating Ideas'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ], default='PENDING')
    
    # Results
    generated_ideas = models.JSONField(default=list)
    ideas_count = models.IntegerField(default=0)
    
    # Metadata
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Idea Generation Request {self.id}"
