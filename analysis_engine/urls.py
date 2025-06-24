"""
URL Configuration for Analysis Engine API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'business-ideas', views.BusinessIdeaViewSet, basename='businessidea')
router.register(r'agent-reports', views.AgentReportViewSet, basename='agentreport')
router.register(r'idea-generation', views.IdeaGenerationViewSet, basename='ideageneration')
router.register(r'analytics', views.AnalyticsViewSet, basename='analytics')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
