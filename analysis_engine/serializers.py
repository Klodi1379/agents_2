"""
Serializers for the Business Analysis API

These serializers handle the conversion between model instances and JSON
for the REST API endpoints.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    BusinessIdea, AgentReport, FinalAnalysisReport, 
    AnalysisTask, IdeaGenerationRequest
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user information"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class BusinessIdeaSerializer(serializers.ModelSerializer):
    """Serializer for business ideas with full details"""
    
    submitted_by = UserSerializer(read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    is_analysis_complete = serializers.ReadOnlyField()
    
    class Meta:
        model = BusinessIdea
        fields = [
            'id', 'title', 'description', 'industry', 'target_market',
            'estimated_budget', 'submitted_by', 'submitted_at', 'updated_at',
            'status', 'overall_score', 'recommendation', 'confidence_level',
            'progress_percentage', 'is_analysis_complete'
        ]
        read_only_fields = [
            'id', 'submitted_at', 'updated_at', 'overall_score', 
            'recommendation', 'confidence_level'
        ]


class BusinessIdeaCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new business ideas"""
    
    class Meta:
        model = BusinessIdea
        fields = [
            'title', 'description', 'industry', 'target_market', 'estimated_budget'
        ]
    
    def validate_title(self, value):
        """Validate that title is not empty and has reasonable length"""
        if not value or len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Title must be at least 5 characters long"
            )
        if len(value) > 255:
            raise serializers.ValidationError(
                "Title must be less than 255 characters"
            )
        return value.strip()
    
    def validate_description(self, value):
        """Validate that description provides sufficient detail"""
        if not value or len(value.strip()) < 20:
            raise serializers.ValidationError(
                "Description must be at least 20 characters long"
            )
        if len(value) > 5000:
            raise serializers.ValidationError(
                "Description must be less than 5000 characters"
            )
        return value.strip()
    
    def validate_estimated_budget(self, value):
        """Validate budget is reasonable"""
        if value is not None:
            if value < 0:
                raise serializers.ValidationError(
                    "Budget cannot be negative"
                )
            if value > 1000000000:  # 1 billion
                raise serializers.ValidationError(
                    "Budget seems unreasonably high"
                )
        return value


class AgentReportSerializer(serializers.ModelSerializer):
    """Serializer for individual agent reports"""
    
    agent_type_display = serializers.CharField(source='get_agent_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    execution_time_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = AgentReport
        fields = [
            'id', 'business_idea', 'agent_type', 'agent_type_display',
            'report_content', 'structured_data', 'agent_score', 'confidence',
            'created_at', 'execution_time', 'execution_time_seconds',
            'llm_model_used', 'token_usage', 'cost_estimate',
            'status', 'status_display', 'error_message'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_execution_time_seconds(self, obj):
        """Convert execution time to seconds"""
        if obj.execution_time:
            return obj.execution_time.total_seconds()
        return None


class AgentReportSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for agent report summaries"""
    
    agent_type_display = serializers.CharField(source='get_agent_type_display', read_only=True)
    
    class Meta:
        model = AgentReport
        fields = [
            'id', 'agent_type', 'agent_type_display', 'agent_score',
            'confidence', 'status', 'created_at'
        ]


class FinalAnalysisReportSerializer(serializers.ModelSerializer):
    """Serializer for final analysis reports"""
    
    business_idea = BusinessIdeaSerializer(read_only=True)
    final_recommendation_display = serializers.CharField(
        source='get_final_recommendation_display', 
        read_only=True
    )
    
    class Meta:
        model = FinalAnalysisReport
        fields = [
            'id', 'business_idea', 'executive_summary', 'key_findings',
            'recommendations', 'market_analysis', 'financial_projections',
            'risk_assessment', 'technical_feasibility', 'market_score',
            'financial_score', 'technical_score', 'risk_score', 'overall_score',
            'final_recommendation', 'final_recommendation_display',
            'confidence_level', 'created_at', 'generated_by_agent', 'total_cost'
        ]
        read_only_fields = ['id', 'created_at']


class AnalysisTaskSerializer(serializers.ModelSerializer):
    """Serializer for analysis tasks"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    agent_type_display = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalysisTask
        fields = [
            'id', 'business_idea', 'task_id', 'agent_type', 'agent_type_display',
            'status', 'status_display', 'result', 'error_message',
            'created_at', 'started_at', 'completed_at', 'duration'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_agent_type_display(self, obj):
        """Get display name for agent type"""
        if obj.agent_type:
            agent_types = dict(AgentReport.AGENT_TYPES)
            return agent_types.get(obj.agent_type, obj.agent_type)
        return "Orchestrator"
    
    def get_duration(self, obj):
        """Calculate task duration"""
        if obj.completed_at and obj.started_at:
            return (obj.completed_at - obj.started_at).total_seconds()
        elif obj.started_at:
            from django.utils import timezone
            return (timezone.now() - obj.started_at).total_seconds()
        return None


class IdeaGenerationRequestSerializer(serializers.ModelSerializer):
    """Serializer for idea generation requests"""
    
    requested_by = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    innovation_level_display = serializers.CharField(
        source='get_innovation_level_display', 
        read_only=True
    )
    
    class Meta:
        model = IdeaGenerationRequest
        fields = [
            'id', 'industry_focus', 'budget_range', 'target_audience',
            'innovation_level', 'innovation_level_display', 'geographic_focus',
            'technology_preferences', 'avoid_sectors', 'status', 'status_display',
            'generated_ideas', 'ideas_count', 'requested_by', 'created_at',
            'completed_at'
        ]
        read_only_fields = [
            'id', 'generated_ideas', 'ideas_count', 'created_at', 'completed_at'
        ]
    
    def validate_budget_range(self, value):
        """Validate budget range format"""
        if value and not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Budget range should include some numerical information"
            )
        return value


class BusinessIdeaListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing business ideas"""
    
    progress_percentage = serializers.ReadOnlyField()
    submitted_by_username = serializers.CharField(source='submitted_by.username', read_only=True)
    
    class Meta:
        model = BusinessIdea
        fields = [
            'id', 'title', 'industry', 'status', 'overall_score',
            'recommendation', 'submitted_at', 'progress_percentage',
            'submitted_by_username'
        ]


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    
    total_ideas = serializers.IntegerField()
    recent_ideas_count = serializers.IntegerField()
    completed_analyses = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    average_score = serializers.FloatField(allow_null=True)
    status_distribution = serializers.ListField()
    top_performing_ideas = BusinessIdeaListSerializer(many=True)


class AgentPerformanceSerializer(serializers.Serializer):
    """Serializer for agent performance metrics"""
    
    agent_name = serializers.CharField()
    total_reports = serializers.IntegerField()
    average_score = serializers.FloatField(allow_null=True)
    average_confidence = serializers.FloatField(allow_null=True)
    average_execution_time = serializers.FloatField(allow_null=True)


class PlatformMetricsSerializer(serializers.Serializer):
    """Serializer for platform-wide metrics"""
    
    total_ideas = serializers.IntegerField()
    completed_analyses = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    average_score = serializers.FloatField(allow_null=True)
    industry_distribution = serializers.ListField()
    agent_performance = serializers.DictField()


class AnalysisStatusSerializer(serializers.Serializer):
    """Serializer for detailed analysis status"""
    
    business_idea = BusinessIdeaSerializer()
    progress = serializers.DictField()
    agent_reports = AgentReportSummarySerializer(many=True)
    final_report = FinalAnalysisReportSerializer(allow_null=True)
    is_complete = serializers.BooleanField()
    last_updated = serializers.DateTimeField()


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses"""
    
    detail = serializers.CharField()
    error_code = serializers.CharField(required=False)
    errors = serializers.DictField(required=False)


class SuccessResponseSerializer(serializers.Serializer):
    """Serializer for success responses"""
    
    detail = serializers.CharField()
    data = serializers.DictField(required=False)
