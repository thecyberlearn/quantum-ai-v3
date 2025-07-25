from django.db import models
from decimal import Decimal
from agent_base.models import BaseAgentRequest, BaseAgentResponse
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os


class DataAnalysisAgentRequest(BaseAgentRequest):
    """Data Analysis Agent request tracking"""
    
    # Agent-specific request fields  
    data_file = models.FileField(
        upload_to='uploads/data_analyzer/', 
        blank=True,
        help_text='PDF file for analysis'
    )
    analysis_type = models.CharField(
        max_length=50,
        choices=[
            ('summary', 'Summary Analysis'),
            ('detailed', 'Detailed Analysis'),
            ('statistical', 'Statistical Analysis'),
        ],
        default='summary'
    )
    # Legacy field (keeping for compatibility)
    input_text = models.TextField(blank=True, null=True)
    
    
    def delete(self, *args, **kwargs):
        """Custom delete method to clean up uploaded file"""
        # Delete the file before deleting the database record
        if self.data_file:
            try:
                if os.path.exists(self.data_file.path):
                    os.remove(self.data_file.path)
                    print(f"Deleted file during model deletion: {self.data_file.path}")
            except Exception as e:
                print(f"Warning - Failed to delete file during model deletion: {e}")
        
        # Call the parent delete method
        super().delete(*args, **kwargs)
    
    class Meta:
        db_table = 'data_analyzer_requests'
        verbose_name = 'Data Analysis Agent Request'
        verbose_name_plural = 'Data Analysis Agent Requests'


class DataAnalysisAgentResponse(BaseAgentResponse):
    """Data Analysis Agent response storage"""
    
    request = models.OneToOneField(
        DataAnalysisAgentRequest, 
        on_delete=models.CASCADE, 
        related_name='response'
    )
    
    # Agent-specific response fields
    analysis_results = models.JSONField(default=dict, blank=True)
    insights_summary = models.TextField(blank=True)
    report_text = models.TextField(blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    # Legacy field (keeping for compatibility)
    output_text = models.TextField(blank=True, null=True)
    
    
    class Meta:
        db_table = 'data_analyzer_responses'
        verbose_name = 'Data Analysis Agent Response'
        verbose_name_plural = 'Data Analysis Agent Responses'


@receiver(post_delete, sender=DataAnalysisAgentRequest)
def cleanup_data_file(sender, instance, **kwargs):
    """Signal handler to ensure uploaded files are deleted when request is deleted"""
    if instance.data_file:
        try:
            if os.path.exists(instance.data_file.path):
                os.remove(instance.data_file.path)
                print(f"Signal cleanup: Deleted file {instance.data_file.path}")
        except Exception as e:
            print(f"Signal cleanup warning - Failed to delete file: {e}")