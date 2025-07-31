from django.urls import path
from . import views

app_name = 'agents'

urlpatterns = [
    # Web interface
    path('', views.agents_marketplace, name='marketplace'),
    
    # API endpoints - specific URLs first to avoid slug conflicts
    path('api/execute/', views.execute_agent, name='execute_agent'),
    path('api/executions/', views.execution_list, name='execution_list'),
    path('api/executions/<uuid:execution_id>/', views.execution_detail, name='execution_detail'),
    path('api/', views.agent_list, name='agent_list'),
    path('api/<slug:slug>/', views.agent_detail, name='agent_detail_api'),
    
    # Agent detail page (must be last to avoid conflicts)
    path('<slug:slug>/', views.agent_detail_view, name='detail'),
]