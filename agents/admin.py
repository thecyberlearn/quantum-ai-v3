from django.contrib import admin
from .models import AgentCategory, Agent, AgentExecution, ChatSession, ChatMessage

@admin.register(AgentCategory)
class AgentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'agent_type', 'price', 'is_active', 'created_at']
    list_filter = ['category', 'agent_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'short_description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AgentExecution)
class AgentExecutionAdmin(admin.ModelAdmin):
    list_display = ['agent', 'user', 'status', 'fee_charged', 'created_at']
    list_filter = ['status', 'created_at', 'agent__category']
    search_fields = ['agent__name', 'user__email']
    readonly_fields = ['created_at', 'completed_at']

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'agent', 'user', 'status', 'fee_charged', 'created_at']
    list_filter = ['status', 'agent__category', 'created_at']
    search_fields = ['session_id', 'agent__name', 'user__email']
    readonly_fields = ['session_id', 'created_at', 'updated_at', 'completed_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'content_preview', 'timestamp']
    list_filter = ['message_type', 'timestamp']
    search_fields = ['session__session_id', 'content']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
