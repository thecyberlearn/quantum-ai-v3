from django.contrib import admin
from .models import WorkflowRequest, WorkflowResponse, WorkflowAnalytics


@admin.register(WorkflowRequest)
class WorkflowRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'agent_slug', 'status', 'created_at']
    list_filter = ['status', 'agent_slug', 'created_at']
    search_fields = ['user__username', 'agent_slug', 'id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(WorkflowResponse)
class WorkflowResponseAdmin(admin.ModelAdmin):
    list_display = ['request', 'success', 'processing_time', 'created_at']
    list_filter = ['success', 'created_at']
    search_fields = ['request__id', 'request__user__username']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('request__user')


@admin.register(WorkflowAnalytics)
class WorkflowAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['agent_slug', 'user', 'success', 'processing_time', 'date']
    list_filter = ['success', 'agent_slug', 'date']
    search_fields = ['user__username', 'agent_slug']
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
