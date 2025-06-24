"""
Django Admin Configuration for Analysis Engine

This provides a comprehensive admin interface for managing the AI company
business analysis system.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json
from .models import (
    BusinessIdea, AgentReport, FinalAnalysisReport, 
    AnalysisTask, IdeaGenerationRequest
)


@admin.register(BusinessIdea)
class BusinessIdeaAdmin(admin.ModelAdmin):
    """Admin interface for Business Ideas"""
    
    list_display = [
        'title', 'industry', 'status', 'overall_score', 
        'submitted_by', 'submitted_at', 'progress_display'
    ]
    list_filter = [
        'status', 'industry', 'recommendation', 'submitted_at'
    ]
    search_fields = ['title', 'description', 'submitted_by__username']
    readonly_fields = [
        'id', 'submitted_at', 'updated_at', 'overall_score', 
        'recommendation', 'confidence_level', 'progress_display',
        'reports_summary'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'description', 'industry', 'target_market')
        }),
        ('Business Details', {
            'fields': ('estimated_budget', 'submitted_by', 'submitted_at', 'updated_at')
        }),
        ('Analysis Status', {
            'fields': ('status', 'progress_display', 'overall_score', 'recommendation', 'confidence_level')
        }),
        ('Analysis Results', {
            'fields': ('reports_summary',),
            'classes': ('collapse',)
        })
    )
    date_hierarchy = 'submitted_at'
    ordering = ['-submitted_at']
    
    def progress_display(self, obj):
        """Display analysis progress as a progress bar"""
        progress = obj.progress_percentage
        if progress == 100:
            color = 'green'
        elif progress > 50:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<div style="width: 100px; background: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}px; background: {}; height: 20px; border-radius: 3px; '
            'text-align: center; color: white; font-size: 12px; line-height: 20px;">'
            '{}%</div></div>',
            progress, color, int(progress)
        )
    progress_display.short_description = 'Progress'
    
    def reports_summary(self, obj):
        """Display summary of agent reports"""
        reports = obj.agent_reports.all()
        if not reports:
            return "No reports yet"
        
        html = "<table style='width: 100%;'>"
        html += "<tr><th>Agent</th><th>Status</th><th>Score</th><th>Created</th></tr>"
        
        for report in reports:
            status_color = {
                'COMPLETED': 'green',
                'FAILED': 'red',
                'IN_PROGRESS': 'orange',
                'PENDING': 'gray'
            }.get(report.status, 'gray')
            
            html += f"""
            <tr>
                <td>{report.get_agent_type_display()}</td>
                <td><span style="color: {status_color};">{report.status}</span></td>
                <td>{report.agent_score or 'N/A'}</td>
                <td>{report.created_at.strftime('%Y-%m-%d %H:%M')}</td>
            </tr>
            """
        
        html += "</table>"
        return mark_safe(html)
    reports_summary.short_description = 'Agent Reports Summary'


@admin.register(AgentReport)
class AgentReportAdmin(admin.ModelAdmin):
    """Admin interface for Agent Reports"""
    
    list_display = [
        'business_idea_title', 'agent_type', 'status', 'agent_score',
        'confidence', 'created_at', 'execution_time_display'
    ]
    list_filter = [
        'agent_type', 'status', 'llm_model_used', 'created_at'
    ]
    search_fields = [
        'business_idea__title', 'business_idea__description', 'report_content'
    ]
    readonly_fields = [
        'business_idea', 'created_at', 'structured_data_display',
        'token_usage', 'cost_estimate', 'execution_time'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('business_idea', 'agent_type', 'status', 'created_at')
        }),
        ('Analysis Results', {
            'fields': ('agent_score', 'confidence', 'report_content')
        }),
        ('Execution Details', {
            'fields': ('llm_model_used', 'execution_time', 'token_usage', 'cost_estimate'),
            'classes': ('collapse',)
        }),
        ('Structured Data', {
            'fields': ('structured_data_display',),
            'classes': ('collapse',)
        }),
        ('Errors', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        })
    )
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def business_idea_title(self, obj):
        """Display business idea title as a link"""
        url = reverse('admin:analysis_engine_businessidea_change', 
                     args=[obj.business_idea.id])
        return format_html('<a href="{}">{}</a>', url, obj.business_idea.title)
    business_idea_title.short_description = 'Business Idea'
    
    def execution_time_display(self, obj):
        """Display execution time in a readable format"""
        if obj.execution_time:
            total_seconds = obj.execution_time.total_seconds()
            if total_seconds < 60:
                return f"{total_seconds:.1f}s"
            else:
                minutes = int(total_seconds // 60)
                seconds = total_seconds % 60
                return f"{minutes}m {seconds:.1f}s"
        return "N/A"
    execution_time_display.short_description = 'Execution Time'
    
    def structured_data_display(self, obj):
        """Display structured data in a readable format"""
        if obj.structured_data:
            return format_html(
                '<pre style="background: #f8f8f8; padding: 10px; border-radius: 5px; font-size: 12px;">{}</pre>',
                json.dumps(obj.structured_data, indent=2)
            )
        return "No structured data"
    structured_data_display.short_description = 'Structured Data'


@admin.register(FinalAnalysisReport)
class FinalAnalysisReportAdmin(admin.ModelAdmin):
    """Admin interface for Final Analysis Reports"""
    
    list_display = [
        'business_idea_title', 'overall_score', 'final_recommendation',
        'confidence_level', 'created_at', 'total_cost'
    ]
    list_filter = [
        'final_recommendation', 'generated_by_agent', 'created_at'
    ]
    search_fields = [
        'business_idea__title', 'executive_summary', 'key_findings'
    ]
    readonly_fields = [
        'business_idea', 'created_at', 'key_findings_display',
        'recommendations_display', 'financial_projections_display'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('business_idea', 'created_at', 'generated_by_agent')
        }),
        ('Executive Summary', {
            'fields': ('executive_summary', 'overall_score', 'final_recommendation', 'confidence_level')
        }),
        ('Detailed Analysis', {
            'fields': ('market_analysis', 'risk_assessment', 'technical_feasibility'),
            'classes': ('collapse',)
        }),
        ('Scores', {
            'fields': ('market_score', 'financial_score', 'technical_score', 'risk_score'),
            'classes': ('collapse',)
        }),
        ('Structured Data', {
            'fields': ('key_findings_display', 'recommendations_display', 'financial_projections_display'),
            'classes': ('collapse',)
        }),
        ('Cost Information', {
            'fields': ('total_cost',),
            'classes': ('collapse',)
        })
    )
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def business_idea_title(self, obj):
        """Display business idea title as a link"""
        url = reverse('admin:analysis_engine_businessidea_change', 
                     args=[obj.business_idea.id])
        return format_html('<a href="{}">{}</a>', url, obj.business_idea.title)
    business_idea_title.short_description = 'Business Idea'
    
    def key_findings_display(self, obj):
        """Display key findings as a formatted list"""
        if obj.key_findings:
            findings = '\n'.join([f"• {finding}" for finding in obj.key_findings])
            return format_html('<pre>{}</pre>', findings)
        return "No key findings"
    key_findings_display.short_description = 'Key Findings'
    
    def recommendations_display(self, obj):
        """Display recommendations as a formatted list"""
        if obj.recommendations:
            recs = '\n'.join([f"• {rec}" for rec in obj.recommendations])
            return format_html('<pre>{}</pre>', recs)
        return "No recommendations"
    recommendations_display.short_description = 'Recommendations'
    
    def financial_projections_display(self, obj):
        """Display financial projections in a readable format"""
        if obj.financial_projections:
            return format_html(
                '<pre style="background: #f8f8f8; padding: 10px; border-radius: 5px; font-size: 12px;">{}</pre>',
                json.dumps(obj.financial_projections, indent=2)
            )
        return "No financial projections"
    financial_projections_display.short_description = 'Financial Projections'


@admin.register(AnalysisTask)
class AnalysisTaskAdmin(admin.ModelAdmin):
    """Admin interface for Analysis Tasks"""
    
    list_display = [
        'business_idea_short', 'agent_type', 'status', 'created_at',
        'duration_display', 'task_id_short'
    ]
    list_filter = ['status', 'agent_type', 'created_at']
    search_fields = ['business_idea__title', 'task_id', 'agent_type']
    readonly_fields = [
        'task_id', 'created_at', 'started_at', 'completed_at', 'duration_display'
    ]
    fieldsets = (
        ('Task Information', {
            'fields': ('business_idea', 'agent_type', 'task_id', 'status')
        }),
        ('Timing', {
            'fields': ('created_at', 'started_at', 'completed_at', 'duration_display')
        }),
        ('Results', {
            'fields': ('result', 'error_message'),
            'classes': ('collapse',)
        })
    )
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def business_idea_short(self, obj):
        """Display shortened business idea title"""
        title = obj.business_idea.title
        if len(title) > 30:
            return title[:30] + "..."
        return title
    business_idea_short.short_description = 'Business Idea'
    
    def task_id_short(self, obj):
        """Display shortened task ID"""
        return obj.task_id[:8] + "..." if len(obj.task_id) > 8 else obj.task_id
    task_id_short.short_description = 'Task ID'
    
    def duration_display(self, obj):
        """Display task duration"""
        if obj.completed_at and obj.started_at:
            duration = obj.completed_at - obj.started_at
            total_seconds = duration.total_seconds()
            if total_seconds < 60:
                return f"{total_seconds:.1f}s"
            else:
                minutes = int(total_seconds // 60)
                seconds = total_seconds % 60
                return f"{minutes}m {seconds:.1f}s"
        return "N/A"
    duration_display.short_description = 'Duration'


@admin.register(IdeaGenerationRequest)
class IdeaGenerationRequestAdmin(admin.ModelAdmin):
    """Admin interface for Idea Generation Requests"""
    
    list_display = [
        'id_short', 'industry_focus', 'innovation_level', 'status',
        'ideas_count', 'requested_by', 'created_at'
    ]
    list_filter = [
        'industry_focus', 'innovation_level', 'status', 'created_at'
    ]
    search_fields = [
        'target_audience', 'technology_preferences', 'requested_by__username'
    ]
    readonly_fields = [
        'id', 'created_at', 'completed_at', 'ideas_count', 'generated_ideas_display'
    ]
    fieldsets = (
        ('Request Information', {
            'fields': ('id', 'requested_by', 'created_at', 'status')
        }),
        ('Generation Parameters', {
            'fields': ('industry_focus', 'innovation_level', 'budget_range', 
                      'target_audience', 'geographic_focus')
        }),
        ('Constraints', {
            'fields': ('technology_preferences', 'avoid_sectors'),
            'classes': ('collapse',)
        }),
        ('Results', {
            'fields': ('ideas_count', 'completed_at', 'generated_ideas_display'),
            'classes': ('collapse',)
        })
    )
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def id_short(self, obj):
        """Display shortened ID"""
        return str(obj.id)[:8] + "..."
    id_short.short_description = 'ID'
    
    def generated_ideas_display(self, obj):
        """Display generated ideas in a readable format"""
        if obj.generated_ideas:
            html = ""
            for i, idea in enumerate(obj.generated_ideas[:5]):  # Show first 5
                html += f"<div style='margin-bottom: 10px; padding: 10px; background: #f8f8f8; border-radius: 5px;'>"
                html += f"<strong>Idea {i+1}:</strong> {idea.get('title', 'Untitled')}<br>"
                html += f"<small>{idea.get('description', 'No description')[:200]}...</small>"
                html += "</div>"
            
            if len(obj.generated_ideas) > 5:
                html += f"<p><em>... and {len(obj.generated_ideas) - 5} more ideas</em></p>"
            
            return mark_safe(html)
        return "No ideas generated yet"
    generated_ideas_display.short_description = 'Generated Ideas'


# Custom admin site configuration
admin.site.site_header = "AI Company Administration"
admin.site.site_title = "AI Company Admin"
admin.site.index_title = "Business Analysis Management"
