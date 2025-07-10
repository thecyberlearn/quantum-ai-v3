from agent_base.processors import StandardAPIProcessor
from django.utils import timezone
from .models import WeatherReporterRequest, WeatherReporterResponse
import json


class WeatherReporterProcessor(StandardAPIProcessor):
    """API processor for Weather Reporter agent"""
    
    agent_slug = 'weather-reporter'
    api_base_url = 'https://api.openweathermap.org/data/2.5/weather'
    api_key_env = 'OPENWEATHER_API_KEY'
    auth_method = 'query'
    
    def get_endpoint(self, **kwargs):
        """Get the OpenWeather API endpoint with location"""
        location = kwargs.get('location', 'London')
        return f"{self.api_base_url}?q={location}&units=metric"
    
    def prepare_request_data(self, **kwargs):
        """Prepare API request data"""
        return {
            'location': kwargs.get('location', 'London'),
            'report_type': kwargs.get('report_type', 'current'),
        }
    
    def should_use_get(self, **kwargs):
        """Use GET for weather API"""
        return True
    
    def format_weather_report(self, weather_data, report_type):
        """Format weather data into readable report"""
        if not weather_data or 'main' not in weather_data:
            return "Weather data unavailable"
        
        location = weather_data.get('name', 'Unknown')
        country = weather_data.get('sys', {}).get('country', '')
        temp = weather_data.get('main', {}).get('temp', 0)
        feels_like = weather_data.get('main', {}).get('feels_like', 0)
        humidity = weather_data.get('main', {}).get('humidity', 0)
        pressure = weather_data.get('main', {}).get('pressure', 0)
        description = weather_data.get('weather', [{}])[0].get('description', 'Unknown')
        wind_speed = weather_data.get('wind', {}).get('speed', 0)
        wind_deg = weather_data.get('wind', {}).get('deg', 0)
        
        if report_type == 'detailed':
            report = f"""🌤️ Weather Report for {location}, {country}

🌡️ Temperature: {temp}°C (feels like {feels_like}°C)
☁️ Conditions: {description.title()}
💨 Wind: {wind_speed} m/s at {wind_deg}°
💧 Humidity: {humidity}%
🔽 Pressure: {pressure} hPa

Weather data provided by OpenWeatherMap"""
        else:
            report = f"🌤️ {location}: {temp}°C, {description.title()}, {humidity}% humidity"
        
        return report
    
    def process_response(self, response_data, request_obj):
        """Process the weather API response"""
        try:
            # Update request status
            request_obj.status = 'processing'
            request_obj.save()
            
            # Extract weather data
            weather_data = response_data.copy()
            if 'processing_time' in weather_data:
                del weather_data['processing_time']
            if 'success' in weather_data:
                del weather_data['success']
            
            # Extract specific fields
            temperature = None
            description = ""
            humidity = None
            wind_speed = None
            
            if 'main' in weather_data:
                temperature = weather_data['main'].get('temp')
                humidity = weather_data['main'].get('humidity')
            
            if 'weather' in weather_data and len(weather_data['weather']) > 0:
                description = weather_data['weather'][0].get('description', '')
            
            if 'wind' in weather_data:
                wind_speed = weather_data['wind'].get('speed')
            
            # Format report
            formatted_report = self.format_weather_report(weather_data, request_obj.report_type)
            
            # Create response object
            response_obj = WeatherReporterResponse.objects.create(
                request=request_obj,
                success=response_data.get('success', True),
                processing_time=response_data.get('processing_time', 0),
                weather_data=weather_data,
                temperature=temperature,
                description=description,
                humidity=humidity,
                wind_speed=wind_speed,
                formatted_report=formatted_report,
            )
            
            # Update request as completed
            request_obj.status = 'completed'
            request_obj.processed_at = timezone.now()
            request_obj.save()
            
            return response_obj
            
        except Exception as e:
            # Handle error
            request_obj.status = 'failed'
            request_obj.save()
            
            # Create error response
            error_response = WeatherReporterResponse.objects.create(
                request=request_obj,
                success=False,
                error_message=str(e),
                processing_time=response_data.get('processing_time', 0)
            )
            
            raise Exception(f"Failed to process Weather Reporter response: {e}")