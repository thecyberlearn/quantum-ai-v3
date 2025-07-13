from django.urls import path
from . import views

app_name = 'weather_reporter'

urlpatterns = [
    path('', views.weather_reporter_detail, name='detail'),
    path('process/', views.WeatherReporterProcessView.as_view(), name='process'),
    path('status/<uuid:request_id>/', views.weather_reporter_status, name='status'),
    path('result/<uuid:request_id>/', views.weather_reporter_result, name='result'),
]