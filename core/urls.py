from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage_view, name='homepage'),
    path('agents/<slug:agent_slug>/', views.agent_detail_view, name='agent_detail'),
    path('agents/<slug:agent_slug>/use/', views.use_agent_view, name='use_agent'),
    path('wallet/', views.wallet_view, name='wallet'),
    path('wallet/topup/', views.wallet_topup_view, name='wallet_topup'),
    path('stripe/webhook/', views.stripe_webhook_view, name='stripe_webhook'),
    path('api/agents/', views.agents_api_view, name='agents_api'),
]