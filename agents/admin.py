from django.contrib import admin
from .models import AgentCategory, Agent, AgentExecution

@admin.register(AgentCategory)
class AgentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'short_description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AgentExecution)
class AgentExecutionAdmin(admin.ModelAdmin):
    list_display = ['agent', 'user', 'status', 'fee_charged', 'created_at']
    list_filter = ['status', 'created_at', 'agent__category']
    search_fields = ['agent__name', 'user__email']
    readonly_fields = ['created_at', 'completed_at']
