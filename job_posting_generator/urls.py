from django.urls import path
from . import views

app_name = 'job_posting_generator'

urlpatterns = [
    path('', views.job_posting_generator_detail, name='detail'),
    path('status/<uuid:request_id>/', views.job_posting_generator_result, name='status'),
]