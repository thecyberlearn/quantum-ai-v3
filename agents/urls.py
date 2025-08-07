from django.urls import path
from . import views

app_name = 'agents'

urlpatterns = [
    # Web interface
    path('', views.agents_marketplace, name='marketplace'),
    
    # Direct access routes
    path('career-navigator/', views.career_navigator_view, name='career_navigator'),
    path('career-navigator/access/', views.career_navigator_access, name='career_navigator_access'),
    path('ai-brand-strategist/', views.ai_brand_strategist_view, name='ai_brand_strategist'),
    path('ai-brand-strategist/access/', views.ai_brand_strategist_access, name='ai_brand_strategist_access'),
    path('lean-six-sigma-expert/', views.lean_six_sigma_expert_view, name='lean_six_sigma_expert'),
    path('lean-six-sigma-expert/access/', views.lean_six_sigma_expert_access, name='lean_six_sigma_expert_access'),
    path('swot-analysis-expert/', views.swot_analysis_expert_view, name='swot_analysis_expert'),
    path('swot-analysis-expert/access/', views.swot_analysis_expert_access, name='swot_analysis_expert_access'),
    
    # API endpoints - specific URLs first to avoid slug conflicts
    path('api/execute/', views.execute_agent, name='execute_agent'),
    path('api/executions/', views.execution_list, name='execution_list'),
    path('api/executions/<uuid:execution_id>/', views.execution_detail, name='execution_detail'),
    
    # Chat API endpoints
    path('api/chat/start/', views.start_chat_session, name='start_chat_session'),
    path('api/chat/send/', views.send_chat_message, name='send_chat_message'),
    path('api/chat/history/<str:session_id>/', views.get_chat_history, name='get_chat_history'),
    path('api/chat/session/<str:session_id>/status/', views.get_session_status, name='get_session_status'),
    path('api/chat/end/', views.end_chat_session, name='end_chat_session'),
    path('api/chat/export/<str:session_id>/', views.export_chat, name='export_chat'),
    
    path('api/', views.agent_list, name='agent_list'),
    path('api/<slug:slug>/', views.agent_detail, name='agent_detail_api'),
    
    # Generic direct access routes (must be before agent detail)
    path('<slug:slug>/access/', views.direct_access_handler, name='direct_access_handler'),
    path('<slug:slug>/display/', views.direct_access_display, name='direct_access_display'),
    
    # Agent detail page (must be last to avoid conflicts)
    path('<slug:slug>/', views.agent_detail_view, name='detail'),
]