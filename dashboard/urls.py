"""
URL Configuration for Dashboard
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main pages
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Business ideas
    path('submit/', views.submit_idea_view, name='submit_idea'),
    path('ideas/', views.ideas_list_view, name='ideas_list'),
    path('ideas/<uuid:idea_id>/', views.idea_detail_view, name='idea_detail'),
    
    # Reports
    path('reports/<uuid:report_id>/', views.agent_report_detail_view, name='agent_report_detail'),
    
    # Analytics
    path('analytics/', views.analytics_view, name='analytics'),
    
    # AJAX endpoints
    path('ajax/idea-status/<uuid:idea_id>/', views.idea_status_ajax, name='idea_status_ajax'),
    
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
]
