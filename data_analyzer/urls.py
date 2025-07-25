from django.urls import path
from . import views

app_name = 'data_analyzer'

urlpatterns = [
    path('', views.data_analyzer_detail, name='detail'),
    path('status/<uuid:request_id>/', views.data_analyzer_status, name='status'),
    path('result/<uuid:request_id>/', views.data_analyzer_result, name='result'),
]