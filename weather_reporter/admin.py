from django.contrib import admin
from .models import WeatherReporterRequest, WeatherReporterResponse


@admin.register(WeatherReporterRequest)
class WeatherReporterRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'agent', 'status', 'cost', 'created_at']
    list_filter = ['status', 'created_at', 'agent']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['id', 'created_at', 'processed_at']


@admin.register(WeatherReporterResponse)
class WeatherReporterResponseAdmin(admin.ModelAdmin):
    list_display = ['request', 'success', 'processing_time', 'created_at']
    list_filter = ['success', 'created_at']
    readonly_fields = ['id', 'created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('request__user')