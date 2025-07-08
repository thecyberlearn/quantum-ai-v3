from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('pricing/', views.pricing, name='pricing'),
    path('debug/', views.debug_page, name='debug'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('agent/<slug:slug>/', views.agent_detail, name='agent_detail'),
    path('agent/<slug:slug>/process/', views.process_agent, name='process_agent'),
    path('profile/', views.profile, name='profile'),
    
    # API endpoints
    path('api/wallet/balance/', views.check_wallet_balance, name='api_wallet_balance'),
    path('api/chat/<slug:slug>/', views.chat_message, name='api_chat_message'),
]
