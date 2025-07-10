from django.apps import AppConfig


class WeatherReporterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'weather_reporter'
    verbose_name = 'Weather Reporter Agent'