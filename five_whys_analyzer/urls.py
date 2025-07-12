from django.urls import path
from . import views

app_name = 'five_whys_analyzer'

urlpatterns = [
    path('', views.five_whys_analyzer_detail, name='detail'),
    path('chat/', views.FiveWhysAnalyzerChatView.as_view(), name='chat'),
    path('report/', views.FiveWhysAnalyzerReportView.as_view(), name='report'),
    path('session/<str:session_id>/', views.five_whys_analyzer_session, name='session'),
    # Legacy compatibility
    path('process/', views.FiveWhysAnalyzerProcessView.as_view(), name='process'),
]