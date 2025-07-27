from django.contrib import admin
from .models import BaseAgent


@admin.register(BaseAgent)
class BaseAgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'price', 'agent_type', 'created_at']
    list_display_links = ['name', 'slug']  # Make these clickable for editing
    list_filter = ['is_active', 'agent_type', 'category', 'created_at']
    search_fields = ['name', 'slug', 'description']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    ordering = ['name']
    list_editable = ['is_active', 'price']  # Allow quick editing in list view
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category', 'agent_type'),
            'description': 'Core agent information and classification'
        }),
        ('Pricing & Display', {
            'fields': ('price', 'icon', 'is_active'),
            'description': 'Pricing and visual configuration'
        }),
        ('Statistics', {
            'fields': ('rating', 'review_count'),
            'classes': ('collapse',),
            'description': 'Agent performance metrics'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Creation and modification dates'
        }),
    )
    
    actions = ['activate_agents', 'deactivate_agents', 'reset_ratings']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('agent_type',)
        return self.readonly_fields
    
    def price_display(self, obj):
        return f"{obj.price} AED"
    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price'
    
    def activate_agents(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} agents were successfully activated.')
    activate_agents.short_description = "Activate selected agents"
    
    def deactivate_agents(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} agents were successfully deactivated.')
    deactivate_agents.short_description = "Deactivate selected agents"
    
    def reset_ratings(self, request, queryset):
        updated = queryset.update(rating=4.5, review_count=0)
        self.message_user(request, f'{updated} agents had their ratings reset.')
    reset_ratings.short_description = "Reset ratings to default"
    
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True
    
    def has_view_permission(self, request, obj=None):
        return True