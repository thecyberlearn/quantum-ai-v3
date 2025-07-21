from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.homepage_view, name='homepage'),
    path('pricing/', views.pricing_view, name='pricing'),
]