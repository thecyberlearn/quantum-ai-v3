from django.contrib import admin
from .models import FiveWhysAnalyzerRequest, FiveWhysAnalyzerResponse


@admin.register(FiveWhysAnalyzerRequest)
class FiveWhysAnalyzerRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_id', 'status', 'report_generated', 'chat_active', 'created_at', 'cost']
    list_filter = ['status', 'report_generated', 'chat_active', 'analysis_depth', 'created_at']
    search_fields = ['user__email', 'user__username', 'session_id', 'problem_statement']
    readonly_fields = ['id', 'created_at', 'processed_at', 'session_id']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'user', 'session_id', 'status', 'created_at', 'processed_at')
        }),
        ('Chat Session', {
            'fields': ('chat_active', 'chat_messages')
        }),
        ('Report Generation', {
            'fields': ('report_generated', 'problem_statement', 'context_info', 'analysis_depth', 'cost')
        }),
    )


@admin.register(FiveWhysAnalyzerResponse)
class FiveWhysAnalyzerResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'request', 'success', 'created_at']
    list_filter = ['success', 'created_at']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'request', 'success', 'created_at', 'processing_time', 'error_message')
        }),
        ('Chat Response', {
            'fields': ('chat_response', 'chat_history')
        }),
        ('Final Report', {
            'fields': ('final_report', 'report_metadata')
        }),
    )