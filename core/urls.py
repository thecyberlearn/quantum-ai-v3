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
    path('wallet/top-up/success/', views.wallet_topup_success_view, name='wallet_topup_success'),
    path('wallet/top-up/cancel/', views.wallet_topup_cancel_view, name='wallet_topup_cancel'),
    path('wallet/demo/', views.wallet_demo_view, name='wallet_demo'),
    path('wallet/demo/test-payment/', views.wallet_demo_test_payment, name='wallet_demo_test_payment'),
    path('wallet/demo/check-balance/', views.wallet_demo_check_balance, name='wallet_demo_check_balance'),
    path('stripe/webhook/', views.stripe_webhook_view, name='stripe_webhook'),
    path('webhook-test/', views.webhook_test_view, name='webhook_test'),
    path('simple-webhook-test/', views.simple_webhook_test, name='simple_webhook_test'),
    path('webhook-logs/', views.get_webhook_logs, name='webhook_logs'),
    path('api/agents/', views.agents_api_view, name='agents_api'),
]