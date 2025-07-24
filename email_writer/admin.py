from django.contrib import admin
from .models import EmailWriterRequest


@admin.register(EmailWriterRequest)
class EmailWriterRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'email_type', 'recipient', 'tone', 'status', 'created_at']
    list_filter = ['email_type', 'tone', 'length', 'status', 'created_at']
    search_fields = ['user__username', 'recipient', 'main_message']
    readonly_fields = ['id', 'created_at', 'processed_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('id', 'user', 'status', 'cost', 'created_at', 'processed_at')
        }),
        ('Email Details', {
            'fields': ('email_type', 'recipient', 'subject', 'main_message', 'tone', 'length')
        }),
        ('Results', {
            'fields': ('email_content',),
            'classes': ('collapse',)
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # editing an existing object
            readonly.extend(['user', 'email_type', 'recipient', 'main_message'])
        return readonly