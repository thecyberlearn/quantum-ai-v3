from django.apps import AppConfig


class AgentBaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agent_base'
    verbose_name = 'Agent Base Framework'