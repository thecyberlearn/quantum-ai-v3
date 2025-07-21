from django.apps import AppConfig


class {{ agent_name_camel }}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{{ agent_slug_underscore }}'