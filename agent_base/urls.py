from django.urls import path
from . import views

app_name = 'agent_base'

urlpatterns = [
    path('marketplace/', views.marketplace_view, name='marketplace'),
    path('api/agents/', views.agents_api_view, name='agents_api'),
]