from django.contrib import admin
from .models import BaseAgent


@admin.register(BaseAgent)
class BaseAgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'cost_per_request', 'created_at']
    list_filter = ['is_active', 'agent_type', 'created_at']
    search_fields = ['name', 'slug', 'description']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'agent_type')
        }),
        ('Configuration', {
            'fields': ('is_active', 'cost_per_request', 'icon_name')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('agent_type',)
        return self.readonly_fields