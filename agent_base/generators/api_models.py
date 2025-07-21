from django.db import models
from decimal import Decimal
from agent_base.models import BaseAgentRequest, BaseAgentResponse


class {{ agent_name_camel }}Request(BaseAgentRequest):
    """{{ agent_name }} request tracking"""
    
    # Agent-specific request fields
    {% for field in request_fields %}{{ field.name }} = models.{{ field.type }}({{ field.args }})
    {% endfor %}
    
    class Meta:
        db_table = '{{ agent_slug_underscore }}_requests'
        verbose_name = '{{ agent_name }} Request'
        verbose_name_plural = '{{ agent_name }} Requests'


class {{ agent_name_camel }}Response(BaseAgentResponse):
    """{{ agent_name }} response storage"""
    
    request = models.OneToOneField(
        {{ agent_name_camel }}Request, 
        on_delete=models.CASCADE, 
        related_name='response'
    )
    
    # Agent-specific response fields
    {% for field in response_fields %}{{ field.name }} = models.{{ field.type }}({{ field.args }})
    {% endfor %}
    
    class Meta:
        db_table = '{{ agent_slug_underscore }}_responses'
        verbose_name = '{{ agent_name }} Response'
        verbose_name_plural = '{{ agent_name }} Responses'