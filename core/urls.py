from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.homepage_view, name='homepage'),
    path('marketplace/', views.marketplace_view, name='marketplace'),
    path('pricing/', views.pricing_view, name='pricing'),
    path('agents/<slug:agent_slug>/', views.agent_detail_view, name='agent_detail'),
    path('wallet/', views.wallet_view, name='wallet'),
    path('wallet/topup/', views.wallet_topup_view, name='wallet_topup'),
    path('stripe/webhook/', views.stripe_webhook_view, name='stripe_webhook'),
    path('api/agents/', views.agents_api_view, name='agents_api'),
]