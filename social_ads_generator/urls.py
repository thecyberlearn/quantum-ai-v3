from django.urls import path
from . import views

app_name = 'social_ads_generator'

urlpatterns = [
    path('', views.social_ads_generator_detail, name='detail'),
    path('status/<uuid:request_id>/', views.social_ads_generator_status, name='status'),
]