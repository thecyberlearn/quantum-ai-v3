from rest_framework import serializers
from .models import Agent, AgentCategory, AgentExecution

class AgentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentCategory
        fields = ['id', 'name', 'slug', 'description', 'icon']

class AgentSerializer(serializers.ModelSerializer):
    category = AgentCategorySerializer(read_only=True)
    
    class Meta:
        model = Agent
        fields = [
            'id', 'name', 'slug', 'short_description', 'description',
            'category', 'price', 'form_schema', 'created_at'
        ]

class AgentExecutionSerializer(serializers.ModelSerializer):
    agent = AgentSerializer(read_only=True)
    
    class Meta:
        model = AgentExecution
        fields = [
            'id', 'agent', 'input_data', 'output_data', 'status',
            'fee_charged', 'error_message', 'execution_time',
            'created_at', 'completed_at'
        ]