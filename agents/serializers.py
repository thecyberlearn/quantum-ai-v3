from rest_framework import serializers
from .models import AgentExecution

class AgentExecutionSerializer(serializers.ModelSerializer):
    # Note: agent field will contain the database Agent record for foreign key compatibility
    # The actual agent data comes from files via AgentFileService
    
    class Meta:
        model = AgentExecution
        fields = [
            'id', 'agent', 'input_data', 'output_data', 'status',
            'fee_charged', 'error_message', 'execution_time',
            'created_at', 'completed_at'
        ]