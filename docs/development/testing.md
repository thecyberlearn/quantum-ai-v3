# 🧪 Testing Guide

Comprehensive testing procedures for Quantum Tasks AI platform.

## 📋 Testing Overview

**Testing Levels:**
- 🔬 **Unit Tests** - Individual component testing
- 🔗 **Integration Tests** - Agent and system integration
- 🌐 **End-to-End Tests** - Full user workflow testing
- 🚀 **Deployment Tests** - Production deployment verification

---

## ⚡ Quick Testing

### Health Check
```bash
# Local development
curl http://localhost:8000/health/

# Production
curl https://quantum-ai.up.railway.app/health/

# Expected response
{
  "status": "healthy",
  "checks": {
    "database": {"status": "healthy"},
    "agents": {"status": "healthy", "active_count": 7}
  }
}
```

### Basic Functionality
```bash
# Django system check
python manage.py check

# Database connectivity
python manage.py check_db

# Admin access test
python manage.py check_admin
```

---

## 🔬 Unit Testing

### Running Individual Tests

```bash
# Test specific agent
python tests/test_weather_agent.py

# Test homepage functionality
python tests/test_homepage.py

# Test webhook agents
python tests/test_five_whys_webhook.py

# Test job posting generator
python tests/test_job_posting_webhook.py
```

### Django Test Suite

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test authentication
python manage.py test agent_base

# Run with verbosity
python manage.py test --verbosity=2

# Keep test database
python manage.py test --keepdb
```

### Writing Unit Tests

**Example Test Structure:**
```python
# tests/test_weather_agent.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from weather_reporter.models import WeatherReportAgentRequest

User = get_user_model()

class WeatherAgentTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user.add_balance(50, "Test balance")

    def test_weather_request_creation(self):
        """Test weather report request creation"""
        self.client.login(email='test@example.com', password='testpass123')
        
        response = self.client.post('/agents/weather-reporter/', {
            'city': 'London',
            'country_code': 'GB'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            WeatherReportAgentRequest.objects.filter(user=self.user).exists()
        )

    def test_insufficient_balance(self):
        """Test handling of insufficient wallet balance"""
        self.user.wallet_balance = 0
        self.user.save()
        
        self.client.login(email='test@example.com', password='testpass123')
        
        response = self.client.post('/agents/weather-reporter/', {
            'city': 'London',
            'country_code': 'GB'
        })
        
        self.assertContains(response, 'Insufficient balance')
```

---

## 🔗 Integration Testing

### Agent Integration Tests

**Webhook Agent Testing:**
```bash
# Test five whys analyzer
python tests/test_five_whys_webhook.py

# Test data analyzer
python tests/test_final_webhook.py

# Manual webhook test
python manage.py test_webhook
```

**API Agent Testing:**
```python
# Example: Weather API integration test
import requests
from django.test import TestCase
from django.conf import settings

class WeatherAPITestCase(TestCase):
    def test_openweather_api_connection(self):
        """Test OpenWeather API connectivity"""
        api_key = settings.OPENWEATHER_API_KEY
        if not api_key:
            self.skipTest("OpenWeather API key not configured")
        
        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather",
            params={
                'q': 'London,GB',
                'appid': api_key,
                'units': 'metric'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('main', data)
        self.assertIn('weather', data)
```

### Database Integration

```python
# Test database operations
from django.test import TransactionTestCase
from django.db import transaction

class DatabaseIntegrationTestCase(TransactionTestCase):
    def test_user_wallet_transactions(self):
        """Test wallet transaction integrity"""
        user = User.objects.create_user(
            username='test',
            email='test@example.com',
            password='pass'
        )
        
        initial_balance = user.wallet_balance
        
        # Test adding balance
        user.add_balance(100, "Test top-up")
        self.assertEqual(user.wallet_balance, initial_balance + 100)
        
        # Test deducting balance
        success = user.deduct_balance(50, "Test usage")
        self.assertTrue(success)
        self.assertEqual(user.wallet_balance, initial_balance + 50)
        
        # Test insufficient balance
        success = user.deduct_balance(1000, "Too much")
        self.assertFalse(success)
        self.assertEqual(user.wallet_balance, initial_balance + 50)
```

---

## 🌐 End-to-End Testing

### Manual Testing Workflows

**User Registration & Email Verification:**
1. Visit registration page: `/auth/register/`
2. Fill out form with valid data
3. Check email for verification link
4. Click verification link
5. Login with new credentials
6. Verify dashboard access

**Agent Usage Workflow:**
1. Login as verified user
2. Add money to wallet: `/wallet/`
3. Visit agent: `/agents/weather-reporter/`
4. Submit valid request
5. Verify balance deduction
6. Check results display
7. Verify transaction history

**Admin Workflow:**
1. Login to admin: `/admin/`
2. Check user management
3. Verify agent configuration
4. Review transaction logs
5. Test agent activation/deactivation

### Automated E2E Testing

**Using Django Test Client:**
```python
from django.test import TestCase, Client
from django.urls import reverse

class EndToEndTestCase(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_complete_user_journey(self):
        """Test complete user journey from registration to agent usage"""
        
        # 1. Register new user
        response = self.client.post('/auth/register/', {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after registration
        
        # 2. Verify user created
        user = User.objects.get(email='test@example.com')
        self.assertFalse(user.email_verified)
        
        # 3. Simulate email verification
        token = EmailVerificationToken.objects.get(user=user)
        response = self.client.get(f'/auth/verify-email/{token.token}/')
        self.assertEqual(response.status_code, 302)
        
        # 4. Login
        response = self.client.post('/auth/login/', {
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        })
        self.assertEqual(response.status_code, 302)
        
        # 5. Add wallet balance
        user.add_balance(100, "Test balance")
        
        # 6. Use weather agent
        response = self.client.post('/agents/weather-reporter/', {
            'city': 'London',
            'country_code': 'GB'
        })
        self.assertEqual(response.status_code, 200)
        
        # 7. Verify balance deducted
        user.refresh_from_db()
        self.assertLess(user.wallet_balance, 100)
```

---

## 🔧 Testing Utilities

### Test Data Setup

```python
# tests/utils.py
from django.contrib.auth import get_user_model
from agent_base.models import BaseAgent

User = get_user_model()

def create_test_user(email="test@example.com", balance=100):
    """Create a test user with wallet balance"""
    user = User.objects.create_user(
        username='testuser',
        email=email,
        password='testpass123'
    )
    user.email_verified = True
    user.save()
    
    if balance > 0:
        user.add_balance(balance, "Test balance")
    
    return user

def create_test_agent(name="Test Agent", price=10):
    """Create a test agent"""
    return BaseAgent.objects.create(
        name=name,
        slug=name.lower().replace(' ', '-'),
        description="Test agent for testing",
        category='utilities',
        price=price,
        agent_type='api'
    )
```

### Mock External Services

```python
# tests/mocks.py
from unittest.mock import patch, Mock
import json

class MockN8NResponse:
    """Mock N8N webhook response"""
    def __init__(self, success=True, data=None):
        self.status_code = 200 if success else 500
        self.data = data or {"result": "Test result"}
    
    def json(self):
        return self.data

@patch('requests.post')
def test_webhook_agent_with_mock(mock_post):
    """Test webhook agent with mocked N8N response"""
    mock_post.return_value = MockN8NResponse(
        success=True,
        data={"analysis": "Test analysis result"}
    )
    
    # Test code here
    # The webhook call will use the mocked response
```

### Environment Testing

```python
# tests/test_environment.py
from django.test import TestCase
from django.conf import settings

class EnvironmentTestCase(TestCase):
    def test_required_settings(self):
        """Test that required settings are configured"""
        required_settings = [
            'SECRET_KEY',
            'DATABASES',
            'INSTALLED_APPS'
        ]
        
        for setting in required_settings:
            self.assertTrue(
                hasattr(settings, setting),
                f"Required setting {setting} not found"
            )
    
    def test_external_api_keys(self):
        """Test external API key configuration"""
        if hasattr(settings, 'OPENWEATHER_API_KEY'):
            self.assertTrue(
                settings.OPENWEATHER_API_KEY,
                "OpenWeather API key is empty"
            )
```

---

## 🚀 Deployment Testing

### Pre-Deployment Tests

```bash
# 1. Run full test suite
python manage.py test --verbosity=2

# 2. Check deployment configuration
python manage.py check --deploy

# 3. Test with production-like settings
DEBUG=False python manage.py check

# 4. Verify static files
python manage.py collectstatic --dry-run

# 5. Test database migrations
python manage.py migrate --dry-run
```

### Post-Deployment Verification

```bash
# 1. Health check
curl https://quantum-ai.up.railway.app/health/

# 2. Test key endpoints
curl -I https://quantum-ai.up.railway.app/
curl -I https://quantum-ai.up.railway.app/marketplace/
curl -I https://quantum-ai.up.railway.app/admin/

# 3. Test static files
curl -I https://quantum-ai.up.railway.app/static/css/base.css

# 4. Test email functionality (manual)
# Register test user and verify email delivery

# 5. Test payment integration (manual)
# Use Stripe test cards to verify payment flow
```

### Performance Testing

```bash
# Load testing with curl
for i in {1..10}; do
  curl -o /dev/null -s -w "%{time_total}\n" https://quantum-ai.up.railway.app/
done

# Database performance
railway run python manage.py shell -c "
from django.test.utils import override_settings
from django.db import connection
from django.contrib.auth import get_user_model

User = get_user_model()
with connection.cursor() as cursor:
    cursor.execute('EXPLAIN ANALYZE SELECT * FROM authentication_user LIMIT 10')
    print(cursor.fetchall())
"
```

---

## 📊 Test Coverage

### Measuring Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
# Open htmlcov/index.html in browser
```

### Coverage Targets

**Minimum Coverage Goals:**
- **Models:** 90%+ (critical business logic)
- **Views:** 80%+ (user-facing functionality)
- **Processors:** 85%+ (agent business logic)
- **Utilities:** 95%+ (helper functions)

**Critical Areas (100% coverage):**
- User authentication
- Wallet transactions
- Payment processing
- Agent request handling

---

## 🐛 Debugging Tests

### Test Debugging

```python
# Add debugging to tests
import pdb; pdb.set_trace()  # Breakpoint

# Print debugging
print(f"User balance: {user.wallet_balance}")
print(f"Response: {response.content}")

# Use Django test client debugging
from django.test.utils import setup_test_environment
setup_test_environment(debug=True)
```

### Common Test Issues

**Database Issues:**
```bash
# Reset test database
python manage.py test --debug-mode

# Use different test database
python manage.py test --settings=netcop_hub.test_settings
```

**Mock Issues:**
```python
# Verify mock calls
mock_function.assert_called_once_with(expected_arg)

# Check mock call count
self.assertEqual(mock_function.call_count, 1)

# Reset mocks between tests
mock_function.reset_mock()
```

---

## 📚 Related Documentation

- [Setup Guide](./setup-guide.md) - Development environment setup
- [Agent Creation](./agent-creation.md) - Agent development testing
- [Troubleshooting](../operations/troubleshooting.md) - Debugging production issues
- [Database Management](../operations/database-management.md) - Database testing

---

**🎯 Testing Best Practices:**
- Write tests before implementing features (TDD)
- Test both success and failure scenarios
- Mock external services to avoid dependencies
- Use descriptive test names and docstrings
- Maintain test data isolation between tests
- Regular test suite maintenance and cleanup