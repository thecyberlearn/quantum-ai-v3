from django.urls import path
from . import views

app_name = 'email_writer'

urlpatterns = [
    path('', views.email_writer_detail, name='detail'),
    path('status/<int:request_id>/', views.email_writer_status, name='status'),
]