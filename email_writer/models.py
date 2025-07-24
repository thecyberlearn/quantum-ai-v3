from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class EmailWriterRequest(models.Model):
    """Email Writer agent request model"""
    
    # Base request fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=3.00)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Email content fields
    email_type = models.CharField(
        max_length=50,
        choices=[
            ('business', 'Business Email'),
            ('follow_up', 'Follow-up Email'),
            ('complaint', 'Complaint Email'),
            ('thank_you', 'Thank You Email'),
            ('introduction', 'Introduction Email'),
            ('meeting_request', 'Meeting Request'),
            ('apology', 'Apology Email'),
            ('announcement', 'Announcement'),
        ],
        help_text="Type of email to generate"
    )
    
    recipient = models.CharField(
        max_length=200,
        help_text="Who the email is being sent to"
    )
    
    subject = models.CharField(
        max_length=200,
        blank=True,
        help_text="Email subject (optional - can be auto-generated)"
    )
    
    main_message = models.TextField(
        help_text="Main content/purpose of the email"
    )
    
    tone = models.CharField(
        max_length=30,
        choices=[
            ('professional', 'Professional'),
            ('friendly', 'Friendly'),
            ('formal', 'Formal'),
            ('casual', 'Casual'),
        ],
        default='professional',
        help_text="Tone of the email"
    )
    
    length = models.CharField(
        max_length=20,
        choices=[
            ('short', 'Short (1-2 paragraphs)'),
            ('medium', 'Medium (3-4 paragraphs)'),
            ('long', 'Long (5+ paragraphs)'),
        ],
        default='medium',
        help_text="Desired length of the email"
    )
    
    # Result fields
    email_content = models.TextField(
        blank=True,
        help_text="Generated email content"
    )
    
    class Meta:
        verbose_name = "Email Writer Request"
        verbose_name_plural = "Email Writer Requests"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Email Writer - {self.email_type} for {self.recipient}"