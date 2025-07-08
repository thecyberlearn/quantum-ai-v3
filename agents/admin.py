from django.contrib import admin
from .models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category', 'price', 'is_active', 'rating', 'review_count')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'is_active')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category', 'icon')
        }),
        ('Pricing & Rating', {
            'fields': ('price', 'rating', 'review_count')
        }),
        ('Configuration', {
            'fields': ('is_active', 'n8n_webhook_url')
        }),
    )
    
    readonly_fields = ('created_at',)
