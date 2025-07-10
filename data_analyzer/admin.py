from django.contrib import admin
from .models import DataAnalysisAgentRequest, DataAnalysisAgentResponse


@admin.register(DataAnalysisAgentRequest)
class DataAnalysisAgentRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'created_at', 'cost']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['id', 'created_at', 'processed_at']
    ordering = ['-created_at']


@admin.register(DataAnalysisAgentResponse)
class DataAnalysisAgentResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'request', 'success', 'created_at']
    list_filter = ['success', 'created_at']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']