from django.db import models
from decimal import Decimal
from agent_base.models import BaseAgentRequest, BaseAgentResponse


class JobPostingGeneratorRequest(BaseAgentRequest):
    """Job Posting Generator request tracking"""
    
    # Required job details
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    job_description = models.TextField()
    seniority_level = models.CharField(
        max_length=20,
        choices=[
            ('entry', 'Entry Level (0-2 years)'),
            ('mid', 'Mid Level (2-5 years)'),
            ('senior', 'Senior Level (5-8 years)'),
            ('lead', 'Lead/Principal (8+ years)'),
            ('executive', 'Executive/C-Level'),
        ]
    )
    contract_type = models.CharField(
        max_length=20,
        choices=[
            ('full-time', 'Full-time'),
            ('part-time', 'Part-time'),
            ('contract', 'Contract'),
            ('freelance', 'Freelance'),
            ('internship', 'Internship'),
        ]
    )
    location = models.CharField(max_length=200)
    
    # Optional fields
    language = models.CharField(
        max_length=20,
        choices=[
            ('English', 'English'),
            ('Arabic', 'Arabic (العربية)'),
            ('Spanish', 'Spanish (Español)'),
            ('French', 'French (Français)'),
            ('German', 'German (Deutsch)'),
        ],
        default='English'
    )
    company_website = models.URLField(blank=True)
    how_to_apply = models.TextField(blank=True)
    
    
    class Meta:
        db_table = 'job_posting_generator_requests'
        verbose_name = 'Job Posting Generator Request'
        verbose_name_plural = 'Job Posting Generator Requests'


class JobPostingGeneratorResponse(BaseAgentResponse):
    """Job Posting Generator response storage"""
    
    request = models.OneToOneField(
        JobPostingGeneratorRequest, 
        on_delete=models.CASCADE, 
        related_name='response'
    )
    
    # Agent-specific response fields
    job_posting_content = models.TextField(blank=True)
    formatted_posting = models.TextField(blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    
    
    class Meta:
        db_table = 'job_posting_generator_responses'
        verbose_name = 'Job Posting Generator Response'
        verbose_name_plural = 'Job Posting Generator Responses'