from agent_base.processors import StandardAPIProcessor
from django.utils import timezone
from .models import WeatherReporterRequest, WeatherReporterResponse
import json
import re
import urllib.parse


class WeatherReporterProcessor(StandardAPIProcessor):
    """API processor for Weather Reporter agent"""
    
    agent_slug = 'weather-reporter'
    api_base_url = 'https://api.openweathermap.org/data/2.5/weather'
    api_key_env = 'OPENWEATHER_API_KEY'
    auth_method = 'query'
    
    def sanitize_location(self, location):
        """Sanitize and validate location input"""
        if not location:
            return 'London'  # Default fallback
        
        # Remove leading/trailing whitespace
        location = location.strip()
        
        # Length validation (max 100 characters)
        if len(location) > 100:
            location = location[:100]
        
        # Character whitelist: letters, numbers, spaces, hyphens, commas, periods, apostrophes
        # This allows city names like "New York", "São Paulo", "O'Connor", etc.
        allowed_pattern = re.compile(r'^[a-zA-Z0-9\s\-,.\'\u00C0-\u017F]+$')
        
        if not allowed_pattern.match(location):
            # Remove disallowed characters (keep only safe characters)
            location = re.sub(r'[^a-zA-Z0-9\s\-,.\'\u00C0-\u017F]', '', location)
        
        # Remove multiple spaces and clean up
        location = re.sub(r'\s+', ' ', location).strip()
        
        # Final validation - must have at least one alphanumeric character
        if not re.search(r'[a-zA-Z0-9]', location):
            return 'London'  # Fallback if no valid characters remain
        
        return location
    
    def get_endpoint(self, **kwargs):
        """Get the OpenWeather API endpoint with location"""
        location = kwargs.get('location', 'London')
        location = self.sanitize_location(location)
        
        # URL encode the location to prevent injection
        location_encoded = urllib.parse.quote(location)
        return f"{self.api_base_url}?q={location_encoded}&units=metric"
    
    def prepare_request_data(self, **kwargs):
        """Prepare API request data"""
        location = self.sanitize_location(kwargs.get('location', 'London'))
        report_type = kwargs.get('report_type', 'current')
        
        # Validate report_type
        valid_report_types = ['current', 'detailed', 'forecast']
        if report_type not in valid_report_types:
            report_type = 'current'
        
        return {
            'location': location,
            'report_type': report_type,
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
            
            # Check if response already exists (to avoid duplicate creation)
            if hasattr(request_obj, 'response'):
                print(f"{self.agent_slug}: Response already exists for request {request_obj.id}")
                return request_obj.response
            
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
            
            # Determine success
            success = response_data.get('success', True) and bool(weather_data.get('main'))
            
            # Create response object
            response_obj = WeatherReporterResponse.objects.create(
                request=request_obj,
                success=success,
                processing_time=response_data.get('processing_time', 0),
                weather_data=weather_data,
                temperature=temperature,
                description=description,
                humidity=humidity,
                wind_speed=wind_speed,
                formatted_report=formatted_report,
            )
            
            # Only deduct wallet balance after successful processing
            if success:
                request_obj.user.deduct_balance(
                    request_obj.cost,
                    f"Weather Reporter - {request_obj.location}",
                    'weather-reporter'
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
            
            # Check if response already exists (to avoid duplicate creation in error handling)
            if hasattr(request_obj, 'response'):
                print(f"{self.agent_slug}: Error occurred but response already exists for request {request_obj.id}")
                request_obj.response.success = False
                request_obj.response.error_message = str(e)
                request_obj.response.save()
                return request_obj.response
            
            # Create error response only if one doesn't exist
            try:
                error_response = WeatherReporterResponse.objects.create(
                    request=request_obj,
                    success=False,
                    error_message=str(e),
                    processing_time=response_data.get('processing_time', 0)
                )
                return error_response
            except Exception as create_error:
                print(f"{self.agent_slug}: Could not create error response: {create_error}")
                # Return None or re-raise the original error
                raise Exception(f"Failed to process Weather Reporter response: {e}")