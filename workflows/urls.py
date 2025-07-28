from django.urls import path, re_path
from . import views

app_name = 'workflows'

urlpatterns = [
    # Universal agent handler - matches any agent slug
    re_path(r'^(?P<agent_slug>[\w-]+)/$', views.workflow_handler, name='agent'),
    
    # API endpoints
    path('api/process/', views.process_workflow_api, name='process_api'),
    path('api/status/<uuid:request_id>/', views.workflow_status, name='status'),
    
    # User workflow management
    path('history/', views.user_workflows, name='history'),
    path('analytics/', views.workflow_analytics, name='analytics'),
]