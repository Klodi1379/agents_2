from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('analysis_engine.urls')),
    path('agents/', include('agent_system.urls')),
    path('', include('dashboard.urls')),  # Dashboard URLs at root level
    # Redirect old dashboard/ URLs to root for compatibility
    path('dashboard/', RedirectView.as_view(url='/', permanent=False)),
    # Handle Django's default auth URLs
    path('accounts/profile/', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('accounts/login/', RedirectView.as_view(url='/login/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
