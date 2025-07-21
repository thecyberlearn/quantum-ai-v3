from django.urls import path
from . import views

app_name = '{{ agent_slug_underscore }}'

urlpatterns = [
    path('', views.{{ agent_slug_underscore }}_detail, name='detail'),
    path('process/', views.{{ agent_name_camel }}ProcessView.as_view(), name='process'),
    path('result/<uuid:request_id>/', views.{{ agent_slug_underscore }}_result, name='result'),
]