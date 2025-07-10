from django.db import models
from agent_base.models import BaseAgentRequest, BaseAgentResponse


class WeatherReporterRequest(BaseAgentRequest):
    """Request model for Weather Reporter agent"""
    location = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=[('current', 'Current Weather'), ('detailed', 'Detailed Report')], default='current')
    
    
    def __str__(self):
        return f"Weather Reporter Request - {self.user.email} - {self.created_at}"


class WeatherReporterResponse(BaseAgentResponse):
    """Response model for Weather Reporter agent"""
    request = models.OneToOneField(WeatherReporterRequest, on_delete=models.CASCADE, related_name='response')
    weather_data = models.JSONField(default=dict, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    description = models.CharField(max_length=200, blank=True)
    humidity = models.IntegerField(null=True, blank=True)
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    formatted_report = models.TextField(blank=True)
    
    
    def __str__(self):
        return f"Weather Reporter Response - {self.request.user.email} - {self.created_at}"