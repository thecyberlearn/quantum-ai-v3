from django.db import models
import uuid

class AgentCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or emoji")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Agent(models.Model):
    AGENT_TYPE_CHOICES = [
        ('form', 'Form-based'),
        ('chat', 'Chat-based'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    category = models.ForeignKey(AgentCategory, on_delete=models.CASCADE, related_name='agents')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    agent_type = models.CharField(max_length=10, choices=AGENT_TYPE_CHOICES, default='form', help_text="Agent interaction type")
    form_schema = models.JSONField(help_text="JSON schema for agent input form", null=True, blank=True)
    webhook_url = models.URLField(help_text="n8n webhook URL for execution")
    message_limit = models.IntegerField(default=50, help_text="Maximum messages per chat session (for chat agents)")
    access_url_name = models.CharField(max_length=100, blank=True, default='', help_text="URL name for direct access agents")
    display_url_name = models.CharField(max_length=100, blank=True, default='', help_text="URL name for agent display page")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class AgentExecution(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='executions')
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    input_data = models.JSONField()
    output_data = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    fee_charged = models.DecimalField(max_digits=10, decimal_places=2)
    webhook_response = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    execution_time = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.agent.name} - {self.user.email} - {self.status}"

class ChatSession(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
        ('abandoned', 'Abandoned'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=100, unique=True, help_text="Unique session identifier")
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='chat_sessions')
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    context_data = models.JSONField(default=dict, help_text="Session context and progress tracking")
    fee_charged = models.DecimalField(max_digits=10, decimal_places=2)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Session expiration time (30 minutes from last activity)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Set expires_at to 30 minutes from now if not set
        if not self.expires_at:
            from django.utils import timezone
            from datetime import timedelta
            self.expires_at = timezone.now() + timedelta(minutes=30)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.agent.name} - {self.user.email} - {self.session_id}"
    
    def is_expired(self):
        from django.utils import timezone
        if not self.expires_at:
            return False  # Sessions without expiration date are considered active
        return timezone.now() > self.expires_at
    
    def extend_session(self):
        """Extend session by 30 minutes from now"""
        from django.utils import timezone
        from datetime import timedelta
        self.expires_at = timezone.now() + timedelta(minutes=30)
        self.updated_at = timezone.now()
        self.save()

class ChatMessage(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('user', 'User Message'),
        ('agent', 'Agent Response'),
        ('system', 'System Message'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, help_text="Additional message data like webhook responses")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.session.session_id} - {self.message_type} - {self.timestamp}"
