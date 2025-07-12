from django.db import models
from decimal import Decimal
from agent_base.models import BaseAgentRequest, BaseAgentResponse
import uuid


class FiveWhysAnalyzerRequest(BaseAgentRequest):
    """5 Whys Analysis Agent request tracking with chat support"""
    
    # Chat session management
    session_id = models.CharField(max_length=100, default=uuid.uuid4, db_index=True)
    
    # Chat interaction tracking
    chat_messages = models.JSONField(default=list, help_text="Store chat history as list of messages")
    
    # Final report fields (only filled when report is generated)
    problem_statement = models.TextField(blank=True, help_text="Main problem to analyze")
    context_info = models.TextField(blank=True, help_text="Additional context information")
    analysis_depth = models.CharField(
        max_length=20, 
        blank=True,
        choices=[
            ('standard', 'Standard 5 Whys'),
            ('detailed', 'Extended Analysis'),
            ('comprehensive', 'Comprehensive Report')
        ],
        default='standard'
    )
    
    # Chat vs Report tracking
    report_generated = models.BooleanField(default=False, help_text="Has final report been generated and paid for")
    chat_active = models.BooleanField(default=True, help_text="Is chat session still active")
    
    # Legacy field for compatibility
    input_text = models.TextField(blank=True)
    
    class Meta:
        db_table = 'five_whys_analyzer_requests'
        verbose_name = '5 Whys Analysis Agent Request'
        verbose_name_plural = '5 Whys Analysis Agent Requests'
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user', 'chat_active']),
        ]


class FiveWhysAnalyzerResponse(BaseAgentResponse):
    """5 Whys Analysis Agent response storage"""
    
    request = models.OneToOneField(
        FiveWhysAnalyzerRequest, 
        on_delete=models.CASCADE, 
        related_name='response'
    )
    
    # Chat responses (free interactions)
    chat_response = models.TextField(blank=True, help_text="Latest chat response")
    chat_history = models.JSONField(default=list, help_text="Full chat response history")
    
    # Final report (paid interaction)
    final_report = models.TextField(blank=True, help_text="Generated 5 Whys analysis report")
    report_metadata = models.JSONField(default=dict, help_text="Report generation metadata")
    
    # Legacy fields for compatibility
    output_text = models.TextField(blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'five_whys_analyzer_responses'
        verbose_name = '5 Whys Analysis Agent Response'
        verbose_name_plural = '5 Whys Analysis Agent Responses'