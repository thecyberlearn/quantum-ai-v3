from django.db import models
from django.contrib.auth import get_user_model
import uuid
import json

User = get_user_model()


class WorkflowRequest(models.Model):
    """Universal model for all agent workflow requests"""
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workflow_requests')
    agent_slug = models.CharField(max_length=100, db_index=True)  # e.g., 'social-ads-generator'
    input_data = models.JSONField(default=dict)  # All form data as JSON
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['agent_slug', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.agent_slug} - {self.user.username} ({self.created_at})"


class WorkflowResponse(models.Model):
    """Universal model for all agent workflow responses"""
    request = models.OneToOneField(WorkflowRequest, on_delete=models.CASCADE, related_name='response')
    output_data = models.JSONField(default=dict)  # N8N response as JSON
    processing_time = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in seconds
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    n8n_session_id = models.CharField(max_length=100, blank=True)  # Track N8N session
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.request.agent_slug} Response - {status}"
    
    @property
    def formatted_output(self):
        """Format output data for display"""
        if not self.output_data:
            return "No output data"
        
        # Handle different output formats based on agent type
        if isinstance(self.output_data, dict):
            if 'output' in self.output_data:
                return self.output_data['output']
            elif 'result' in self.output_data:
                return self.output_data['result']
        
        return json.dumps(self.output_data, indent=2)


class WorkflowAnalytics(models.Model):
    """Track workflow usage analytics"""
    agent_slug = models.CharField(max_length=100, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    processing_time = models.DecimalField(max_digits=5, decimal_places=2)  # in seconds
    success = models.BooleanField()
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['agent_slug', 'date']),
            models.Index(fields=['user', 'date']),
        ]
    
    def __str__(self):
        return f"{self.agent_slug} - {self.date}"
