from agent_base.processors import StandardAPIProcessor
from django.utils import timezone
from django.conf import settings
from .models import {{ agent_name_camel }}Request, {{ agent_name_camel }}Response
import json


class {{ agent_name_camel }}Processor(StandardAPIProcessor):
    """Weather API processor for {{ agent_name }} agent"""
    
    agent_slug = '{{ agent_slug }}'
    api_base_url = '{{ api_base_url }}'
    api_key_env = '{{ api_key_env }}'
    auth_method = '{{ auth_method }}'
    
    def prepare_request_data(self, **kwargs):
        """Prepare weather API request data"""
        return {
            'q': kwargs.get('location', ''),
            'units': 'metric',
            'appid': self.get_api_key()
        }
    
    def should_use_get(self, **kwargs):
        """Use GET method for weather API calls"""
        return True
    
    def build_url(self, **kwargs):
        """Build the complete weather API URL"""
        location = kwargs.get('location', '')
        base_url = self.api_base_url
        if '?' not in base_url:
            base_url += '?'
        return base_url
    
    def process_response(self, response_data, request_obj):
        """Process the weather API response"""
        try:
            request_obj.status = 'processing'
            request_obj.save()
            
            # Extract weather data
            weather_data = response_data if response_data else {}
            temperature = self.get_nested_value(response_data, 'main.temp')
            description = self.get_nested_value(response_data, 'weather.0.description') or ''
            humidity = self.get_nested_value(response_data, 'main.humidity')
            wind_speed = self.get_nested_value(response_data, 'wind.speed')
            
            # Generate formatted report
            formatted_report = self.generate_weather_report(
                weather_data, 
                request_obj.location, 
                request_obj.report_type
            )
            
            # Determine success based on weather data availability
            success = bool(weather_data.get('main')) and temperature is not None
            
            # Create response object
            response_obj = {{ agent_name_camel }}Response.objects.create(
                request=request_obj,
                success=success,
                processing_time=0,
                weather_data=weather_data,
                temperature=temperature,
                description=description.title() if description else '',
                humidity=humidity,
                wind_speed=wind_speed,
                formatted_report=formatted_report,
            )
            
            # Only deduct wallet balance after successful processing
            if success:
                request_obj.user.deduct_balance(
                    request_obj.cost,
                    f"{{ agent_name }} - Weather for {request_obj.location}",
                    '{{ agent_slug }}'
                )
                print(f"{self.agent_slug}: Wallet deducted {request_obj.cost} AED for successful processing")
            
            # Update request as completed
            request_obj.status = 'completed' if success else 'failed'
            request_obj.processed_at = timezone.now()
            request_obj.save()
            
            return response_obj
            
        except Exception as e:
            # Handle error
            request_obj.status = 'failed'
            request_obj.save()
            
            # Create error response
            error_response = {{ agent_name_camel }}Response.objects.create(
                request=request_obj,
                success=False,
                error_message=str(e),
                processing_time=0
            )
            
            raise Exception(f"Failed to process weather response: {e}")
    
    def generate_weather_report(self, weather_data, location, report_type):
        """Generate formatted weather report"""
        if not weather_data or 'main' not in weather_data:
            return f"Unable to get weather data for {location}"
        
        temp = weather_data.get('main', {}).get('temp', 'N/A')
        description = weather_data.get('weather', [{}])[0].get('description', 'N/A')
        humidity = weather_data.get('main', {}).get('humidity', 'N/A')
        wind_speed = weather_data.get('wind', {}).get('speed', 'N/A')
        feels_like = weather_data.get('main', {}).get('feels_like', 'N/A')
        
        if report_type == 'current':
            return f"Current weather in {location}: {description.title()}, {temp}°C"
        else:
            return f"""Weather Report for {location}:
            
🌡️ Temperature: {temp}°C (feels like {feels_like}°C)
🌤️ Conditions: {description.title()}
💧 Humidity: {humidity}%
💨 Wind Speed: {wind_speed} m/s"""
    
    def get_nested_value(self, data, path):
        """Get nested value from dictionary using dot notation"""
        if not path or not isinstance(data, dict):
            return None
        
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list) and key.isdigit() and int(key) < len(value):
                value = value[int(key)]
            else:
                return None
        
        return value