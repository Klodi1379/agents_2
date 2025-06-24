"""
API Views for Business Analysis Engine

This module provides REST API endpoints for submitting business ideas,
tracking analysis progress, and retrieving results.
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import BusinessIdea, AgentReport, FinalAnalysisReport, IdeaGenerationRequest
from .serializers import (
    BusinessIdeaSerializer, BusinessIdeaCreateSerializer,
    AgentReportSerializer, FinalAnalysisReportSerializer,
    IdeaGenerationRequestSerializer
)
from .tasks import orchestrate_business_analysis, generate_business_ideas

logger = logging.getLogger(__name__)


class BusinessIdeaViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing business ideas and their analysis.
    """
    queryset = BusinessIdea.objects.all().order_by('-submitted_at')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BusinessIdeaCreateSerializer
        return BusinessIdeaSerializer
    
    def perform_create(self, serializer):
        """Create a new business idea and trigger analysis"""
        business_idea = serializer.save(submitted_by=self.request.user)
        
        # Trigger the analysis workflow
        try:
            orchestrate_business_analysis.delay(str(business_idea.id))
            logger.info(f"Analysis triggered for business idea: {business_idea.title}")
        except Exception as e:
            logger.error(f"Failed to trigger analysis for {business_idea.title}: {str(e)}")
            # Don't fail the creation, just log the error
    
    @action(detail=True, methods=['get'])
    def analysis_status(self, request, pk=None):
        """Get detailed analysis status for a business idea"""
        business_idea = self.get_object()
        
        # Get all agent reports
        agent_reports = AgentReport.objects.filter(business_idea=business_idea)
        
        # Calculate progress
        total_agents = len(AgentReport.AGENT_TYPES)
        completed_reports = agent_reports.filter(status='COMPLETED').count()
        failed_reports = agent_reports.filter(status='FAILED').count()
        in_progress_reports = agent_reports.filter(status='IN_PROGRESS').count()
        
        progress_percentage = (completed_reports / total_agents) * 100 if total_agents > 0 else 0
        
        # Get final report if available
        final_report = None
        try:
            final_report = FinalAnalysisReport.objects.get(business_idea=business_idea)
        except FinalAnalysisReport.DoesNotExist:
            pass
        
        return Response({
            'business_idea': BusinessIdeaSerializer(business_idea).data,
            'progress': {
                'percentage': round(progress_percentage, 1),
                'total_agents': total_agents,
                'completed': completed_reports,
                'failed': failed_reports,
                'in_progress': in_progress_reports,
            },
            'agent_reports': AgentReportSerializer(agent_reports, many=True).data,
            'final_report': FinalAnalysisReportSerializer(final_report).data if final_report else None,
            'is_complete': business_idea.status == 'COMPLETED',
            'last_updated': business_idea.updated_at,
        })
    
    @action(detail=True, methods=['get'])
    def agent_reports(self, request, pk=None):
        """Get all agent reports for a business idea"""
        business_idea = self.get_object()
        reports = AgentReport.objects.filter(business_idea=business_idea).order_by('created_at')
        
        return Response({
            'business_idea_id': str(business_idea.id),
            'business_idea_title': business_idea.title,
            'reports': AgentReportSerializer(reports, many=True).data
        })
    
    @action(detail=True, methods=['get'])
    def final_report(self, request, pk=None):
        """Get the final analysis report"""
        business_idea = self.get_object()
        
        try:
            final_report = FinalAnalysisReport.objects.get(business_idea=business_idea)
            return Response(FinalAnalysisReportSerializer(final_report).data)
        except FinalAnalysisReport.DoesNotExist:
            return Response(
                {'detail': 'Final report not yet available'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def reanalyze(self, request, pk=None):
        """Trigger re-analysis of a business idea"""
        business_idea = self.get_object()
        
        if business_idea.status in ['ANALYZING', 'QUEUE']:
            return Response(
                {'detail': 'Analysis already in progress'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset status and trigger new analysis
        business_idea.status = 'PENDING'
        business_idea.save()
        
        # Delete existing reports to start fresh
        AgentReport.objects.filter(business_idea=business_idea).delete()
        FinalAnalysisReport.objects.filter(business_idea=business_idea).delete()
        
        # Trigger new analysis
        try:
            orchestrate_business_analysis.delay(str(business_idea.id))
            return Response({'detail': 'Re-analysis triggered successfully'})
        except Exception as e:
            logger.error(f"Failed to trigger re-analysis for {business_idea.title}: {str(e)}")
            return Response(
                {'detail': 'Failed to trigger re-analysis'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics"""
        user_ideas = self.queryset.filter(submitted_by=request.user)
        
        # Recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_ideas = user_ideas.filter(submitted_at__gte=thirty_days_ago)
        
        # Status distribution
        status_distribution = user_ideas.values('status').annotate(count=Count('status'))
        
        # Average scores
        completed_ideas = user_ideas.filter(status='COMPLETED', overall_score__isnull=False)
        avg_score = completed_ideas.aggregate(avg_score=Avg('overall_score'))['avg_score']
        
        # Top performing ideas
        top_ideas = completed_ideas.order_by('-overall_score')[:5]
        
        return Response({
            'total_ideas': user_ideas.count(),
            'recent_ideas_count': recent_ideas.count(),
            'completed_analyses': user_ideas.filter(status='COMPLETED').count(),
            'in_progress': user_ideas.filter(status='ANALYZING').count(),
            'average_score': round(avg_score, 1) if avg_score else None,
            'status_distribution': list(status_distribution),
            'top_performing_ideas': BusinessIdeaSerializer(top_ideas, many=True).data,
        })


class AgentReportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing agent reports.
    """
    queryset = AgentReport.objects.all().order_by('-created_at')
    serializer_class = AgentReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter reports by user's business ideas"""
        user_ideas = BusinessIdea.objects.filter(submitted_by=self.request.user)
        return self.queryset.filter(business_idea__in=user_ideas)
    
    @action(detail=False, methods=['get'])
    def by_agent_type(self, request):
        """Get reports grouped by agent type"""
        agent_type = request.query_params.get('agent_type')
        if not agent_type:
            return Response(
                {'detail': 'agent_type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reports = self.get_queryset().filter(agent_type=agent_type)
        return Response(AgentReportSerializer(reports, many=True).data)
    
    @action(detail=False, methods=['get'])
    def performance_metrics(self, request):
        """Get performance metrics for agents"""
        metrics = {}
        
        for agent_type, agent_name in AgentReport.AGENT_TYPES:
            agent_reports = self.get_queryset().filter(
                agent_type=agent_type,
                status='COMPLETED'
            )
            
            if agent_reports.exists():
                avg_score = agent_reports.aggregate(avg_score=Avg('agent_score'))['avg_score']
                avg_confidence = agent_reports.aggregate(avg_conf=Avg('confidence'))['avg_conf']
                total_reports = agent_reports.count()
                
                metrics[agent_type] = {
                    'agent_name': agent_name,
                    'total_reports': total_reports,
                    'average_score': round(avg_score, 1) if avg_score else None,
                    'average_confidence': round(float(avg_confidence), 1) if avg_confidence else None,
                }
        
        return Response(metrics)


class IdeaGenerationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for generating new business ideas using AI.
    """
    queryset = IdeaGenerationRequest.objects.all().order_by('-created_at')
    serializer_class = IdeaGenerationRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter requests by user"""
        return self.queryset.filter(requested_by=self.request.user)
    
    def perform_create(self, serializer):
        """Create a new idea generation request and trigger generation"""
        request_obj = serializer.save(requested_by=self.request.user)
        
        # Trigger the idea generation
        try:
            generate_business_ideas.delay(str(request_obj.id))
            logger.info(f"Idea generation triggered for request: {request_obj.id}")
        except Exception as e:
            logger.error(f"Failed to trigger idea generation: {str(e)}")
    
    @action(detail=True, methods=['post'])
    def analyze_generated_idea(self, request, pk=None):
        """Convert a generated idea into a full business idea for analysis"""
        generation_request = self.get_object()
        idea_index = request.data.get('idea_index', 0)
        
        if not generation_request.generated_ideas:
            return Response(
                {'detail': 'No generated ideas available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if idea_index >= len(generation_request.generated_ideas):
            return Response(
                {'detail': 'Invalid idea index'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        generated_idea = generation_request.generated_ideas[idea_index]
        
        # Create a new BusinessIdea for analysis
        business_idea = BusinessIdea.objects.create(
            title=generated_idea.get('title', 'Generated Business Idea'),
            description=generated_idea.get('description', ''),
            industry=generation_request.industry_focus or 'OTHER',
            target_market=generation_request.target_audience or '',
            submitted_by=request.user
        )
        
        # Trigger analysis
        try:
            orchestrate_business_analysis.delay(str(business_idea.id))
            return Response({
                'detail': 'Business idea created and analysis triggered',
                'business_idea_id': str(business_idea.id)
            })
        except Exception as e:
            logger.error(f"Failed to trigger analysis for generated idea: {str(e)}")
            return Response(
                {'detail': 'Failed to trigger analysis'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for analytics and reporting across the platform.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def platform_metrics(self, request):
        """Get platform-wide analytics (admin users only)"""
        if not request.user.is_staff:
            return Response(
                {'detail': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Platform-wide statistics
        total_ideas = BusinessIdea.objects.count()
        completed_analyses = BusinessIdea.objects.filter(status='COMPLETED').count()
        avg_score = BusinessIdea.objects.filter(
            status='COMPLETED',
            overall_score__isnull=False
        ).aggregate(avg=Avg('overall_score'))['avg']
        
        # Industry distribution
        industry_dist = BusinessIdea.objects.values('industry').annotate(
            count=Count('industry')
        ).order_by('-count')
        
        # Agent performance
        agent_performance = {}
        for agent_type, agent_name in AgentReport.AGENT_TYPES:
            reports = AgentReport.objects.filter(
                agent_type=agent_type,
                status='COMPLETED'
            )
            if reports.exists():
                agent_performance[agent_type] = {
                    'name': agent_name,
                    'total_reports': reports.count(),
                    'avg_score': reports.aggregate(avg=Avg('agent_score'))['avg'],
                    'avg_execution_time': reports.aggregate(
                        avg=Avg('execution_time')
                    )['avg'].total_seconds() if reports.aggregate(
                        avg=Avg('execution_time')
                    )['avg'] else 0,
                }
        
        return Response({
            'total_ideas': total_ideas,
            'completed_analyses': completed_analyses,
            'completion_rate': (completed_analyses / total_ideas * 100) if total_ideas > 0 else 0,
            'average_score': round(avg_score, 1) if avg_score else None,
            'industry_distribution': list(industry_dist),
            'agent_performance': agent_performance,
        })
    
    @action(detail=False, methods=['get'])
    def user_analytics(self, request):
        """Get analytics for the current user"""
        user_ideas = BusinessIdea.objects.filter(submitted_by=request.user)
        
        # Time series data (last 6 months)
        six_months_ago = timezone.now() - timedelta(days=180)
        monthly_data = []
        
        for i in range(6):
            month_start = six_months_ago + timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            month_ideas = user_ideas.filter(
                submitted_at__gte=month_start,
                submitted_at__lt=month_end
            )
            
            monthly_data.append({
                'month': month_start.strftime('%Y-%m'),
                'ideas_submitted': month_ideas.count(),
                'analyses_completed': month_ideas.filter(status='COMPLETED').count(),
                'avg_score': month_ideas.filter(
                    status='COMPLETED',
                    overall_score__isnull=False
                ).aggregate(avg=Avg('overall_score'))['avg'] or 0,
            })
        
        return Response({
            'monthly_activity': monthly_data,
            'total_ideas': user_ideas.count(),
            'best_performing_idea': user_ideas.filter(
                status='COMPLETED'
            ).order_by('-overall_score').first(),
            'recent_activity': user_ideas.order_by('-submitted_at')[:5],
        })
