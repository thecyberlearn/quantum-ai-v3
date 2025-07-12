# Development Guide - Enhanced with Agent Testing

## Quick Start

### Option 1: Use the Development Script (Recommended)
```bash
./run_dev.sh
```

### Option 2: Manual Startup
```bash
# Clear any interfering environment variables
unset DATABASE_URL

# Activate virtual environment
source venv/bin/activate

# Start server
python manage.py runserver
```

## Common Issues

### Issue: "Connection refused" Error with PostgreSQL
**Cause:** You have `DATABASE_URL` set as an environment variable pointing to PostgreSQL.

**Solution:**
```bash
# Check if DATABASE_URL is set
echo $DATABASE_URL

# Temporarily unset it
unset DATABASE_URL

# Start server
python manage.py runserver
```

**Permanent Fix:**
If `DATABASE_URL` keeps getting set, check these files:
- `~/.bashrc`
- `~/.bash_profile` 
- `~/.profile`
- `~/.zshrc`
- `~/.env` (global)

Remove any lines containing `DATABASE_URL=` unless you specifically need them.

### Issue: Database Tables Don't Exist
```bash
# Run migrations
python manage.py migrate

# Create admin user and populate data
python manage.py populate_agents --create-admin
```

### Issue: Admin Login Not Working
```bash
# Check if admin user exists
python manage.py backup_users --action info

# Create admin user
python manage.py create_user admin@example.com password123 --superuser
```

## Database Configuration

### Local Development (Default)
- **Engine:** SQLite
- **Location:** `db.sqlite3`
- **Setup:** None required

### Local Development with PostgreSQL (Optional)
1. **Set up PostgreSQL:**
   ```bash
   # Using Docker (easiest)
   docker run --name netcop-postgres \\
     -e POSTGRES_DB=netcop_hub \\
     -e POSTGRES_USER=netcop_user \\
     -e POSTGRES_PASSWORD=netcop_pass \\
     -p 5432:5432 -d postgres:15
   ```

2. **Enable in .env:**
   ```env
   USE_POSTGRESQL=True
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   python manage.py populate_agents --create-admin
   ```

### Railway Production
- **Engine:** PostgreSQL (automatic)
- **Configuration:** Via Railway's `DATABASE_URL`
- **Setup:** None required

## Environment Variables

### Required for Development
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

### Optional for Development
```env
# Force PostgreSQL (requires PostgreSQL setup)
USE_POSTGRESQL=True

# Or specify exact database URL
DATABASE_URL=postgresql://netcop_user:netcop_pass@localhost:5432/netcop_hub

# API Keys (for full functionality)
OPENWEATHER_API_KEY=your-key-here
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Development Workflow

### Daily Development
```bash
# Start development server
./run_dev.sh

# In another terminal - run commands
source venv/bin/activate
python manage.py check_db          # Check database status
python manage.py makemigrations    # Create migrations
python manage.py migrate           # Apply migrations
```

### Testing Changes
```bash
# Check for issues
python manage.py check

# Test migrations
python manage.py migrate --plan

# Create test data
python manage.py populate_agents --create-admin
```

### Debugging
```bash
# Check database configuration
python manage.py check_db

# Check migration status
python manage.py showmigrations

# Django shell
python manage.py shell
```

## File Structure

```
netcop_django/
├── run_dev.sh              # Development startup script
├── manage.py               # Django management
├── requirements.txt        # Python dependencies
├── .env                   # Local environment variables
├── db.sqlite3             # SQLite database (local)
├── docs/                  # Documentation
├── static/                # Static files
├── templates/             # Global templates
├── netcop_hub/            # Django project settings
├── core/                  # Main app (homepage, marketplace)
├── authentication/       # User management
├── wallet/               # Payment system
├── agent_base/           # Agent framework
├── weather_reporter/     # Weather agent
├── data_analyzer/        # Data analysis agent
├── job_posting_generator/ # Job posting agent
└── social_ads_generator/ # Social ads agent
```

## Useful Commands

```bash
# Development
./run_dev.sh                                    # Start dev server
python manage.py check_db                       # Check database
python manage.py migrate                        # Run migrations
python manage.py populate_agents --create-admin # Setup data

# User Management
python manage.py create_user email@example.com password123 --superuser
python manage.py backup_users --action info

# Database Management
python manage.py reset_database --action full --confirm
python manage.py fix_migrations --app data_analyzer

# Debugging
python manage.py check                          # System check
python manage.py showmigrations                 # Migration status
python manage.py shell                          # Django shell
```

## Troubleshooting

### Server Won't Start
1. Check if `DATABASE_URL` is set: `echo $DATABASE_URL`
2. Unset it: `unset DATABASE_URL` 
3. Use the development script: `./run_dev.sh`

### Database Issues
1. Check configuration: `python manage.py check_db`
2. Run migrations: `python manage.py migrate`
3. Reset if needed: `python manage.py reset_database --action full --confirm`

### Import Errors
1. Activate virtual environment: `source venv/bin/activate`
2. Install requirements: `pip install -r requirements.txt`

### Permission Errors
1. Make script executable: `chmod +x run_dev.sh`
2. Check file permissions: `ls -la`

---

## 🧪 Agent Testing Procedures *(5 Whys Experience)*

Based on extensive debugging and the successful 5 Whys Analyzer implementation, here are comprehensive testing procedures for error-free agent development.

### Pre-Development Agent Testing Setup

```bash
# Agent validation environment setup
python manage.py shell -c "
from agent_base.models import BaseAgent
from django.template.loader import get_template
from django.urls import reverse
import os

def validate_agent_environment(agent_slug):
    print(f'🧪 Testing environment for {agent_slug}...')
    
    # Test 1: BaseAgent exists
    try:
        agent = BaseAgent.objects.get(slug=agent_slug)
        print(f'✅ BaseAgent found: {agent.name}')
    except BaseAgent.DoesNotExist:
        print(f'❌ BaseAgent not found for slug: {agent_slug}')
        return False
    
    # Test 2: URL resolution
    try:
        url = reverse('core:agent_detail', args=[agent_slug])
        print(f'✅ URL resolved: {url}')
    except Exception as e:
        print(f'❌ URL resolution failed: {e}')
        return False
    
    # Test 3: Template loading
    try:
        template = get_template(f'{agent_slug.replace(\"-\", \"_\")}/detail.html')
        print(f'✅ Template found: {template.origin.name}')
    except Exception as e:
        print(f'❌ Template not found: {e}')
        return False
    
    # Test 4: Environment variables (if needed)
    env_var = f'N8N_WEBHOOK_{agent_slug.upper().replace(\"-\", \"_\")}'
    if os.getenv(env_var):
        print(f'✅ Environment variable found: {env_var}')
    else:
        print(f'⚠️ Environment variable not set: {env_var}')
    
    print(f'🎯 Environment validation complete for {agent_slug}')
    return True

# Test your agent
validate_agent_environment('five-whys-analyzer')
"
```

### Agent Request Lifecycle Testing

```bash
# Test complete agent request lifecycle
python manage.py shell -c "
import uuid
from django.contrib.auth import get_user_model
from agent_base.models import BaseAgent
from five_whys_analyzer.models import FiveWhysAnalyzerRequest, FiveWhysAnalyzerResponse
from five_whys_analyzer.processor import FiveWhysAnalyzerProcessor
from decimal import Decimal

User = get_user_model()

def test_agent_lifecycle(agent_slug='five-whys-analyzer'):
    print(f'🧪 Testing complete lifecycle for {agent_slug}...')
    
    # Get test user
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        print('❌ No superuser found for testing')
        return False
    
    # Test 1: Agent exists and is active
    try:
        agent = BaseAgent.objects.get(slug=agent_slug, is_active=True)
        print(f'✅ Active agent found: {agent.name} (${agent.price})')
    except BaseAgent.DoesNotExist:
        print(f'❌ Active agent not found: {agent_slug}')
        return False
    
    # Test 2: User has sufficient balance
    if user.wallet_balance < agent.price:
        print(f'⚠️ User balance ({user.wallet_balance}) < agent price ({agent.price})')
        print('Adding test balance...')
        user.wallet_balance += Decimal('50.00')
        user.save()
    
    # Test 3: Create request object
    session_id = str(uuid.uuid4())
    try:
        request_obj = FiveWhysAnalyzerRequest.objects.create(
            user=user,
            agent=agent,
            session_id=session_id,
            cost=Decimal('8.00'),
            problem_statement='Test problem for validation',
            status='pending'
        )
        print(f'✅ Request created: {request_obj.id}')
    except Exception as e:
        print(f'❌ Request creation failed: {e}')
        return False
    
    # Test 4: Status transitions
    try:
        request_obj.status = 'processing'
        request_obj.save()
        print('✅ Status updated to processing')
        
        request_obj.status = 'completed'
        request_obj.save()
        print('✅ Status updated to completed')
    except Exception as e:
        print(f'❌ Status update failed: {e}')
        return False
    
    # Test 5: Response creation
    try:
        response_obj = FiveWhysAnalyzerResponse.objects.create(
            request=request_obj,
            success=True,
            final_report='Test report generated successfully',
            processing_time=2.5
        )
        print(f'✅ Response created: {response_obj.id}')
    except Exception as e:
        print(f'❌ Response creation failed: {e}')
        return False
    
    # Test 6: Cleanup
    response_obj.delete()
    request_obj.delete()
    print('✅ Test objects cleaned up')
    
    print(f'🎯 Lifecycle test completed successfully for {agent_slug}')
    return True

# Run the test
test_agent_lifecycle()
"
```

### Wallet Integration Testing

```bash
# Test wallet integration patterns (5 Whys delayed deduction pattern)
python manage.py shell -c "
from django.contrib.auth import get_user_model
from agent_base.models import BaseAgent
from decimal import Decimal

User = get_user_model()

def test_wallet_integration():
    print('🧪 Testing wallet integration patterns...')
    
    user = User.objects.filter(is_superuser=True).first()
    agent = BaseAgent.objects.filter(is_active=True).first()
    
    if not user or not agent:
        print('❌ Missing test user or agent')
        return False
    
    # Record initial balance
    initial_balance = user.wallet_balance
    print(f'Initial balance: {initial_balance}')
    
    # Test 1: Balance check (5 Whys pattern)
    if user.wallet_balance >= agent.price:
        print('✅ Sufficient balance for processing')
    else:
        print('❌ Insufficient balance')
        return False
    
    # Test 2: Delayed deduction simulation
    print('🔄 Simulating processing...')
    processing_success = True  # Simulate success
    
    if processing_success:
        # Only deduct after success (5 Whys pattern)
        user.deduct_balance(
            agent.price,
            f'Test deduction for {agent.name}',
            agent.slug
        )
        print(f'✅ Balance deducted after success: {user.wallet_balance}')
        
        # Verify deduction
        expected_balance = initial_balance - agent.price
        if user.wallet_balance == expected_balance:
            print('✅ Wallet deduction verified correct')
        else:
            print(f'❌ Wallet deduction incorrect: expected {expected_balance}, got {user.wallet_balance}')
            return False
    else:
        print('✅ No deduction for failed processing (correct behavior)')
    
    # Test 3: Restore balance for other tests
    user.wallet_balance = initial_balance
    user.save()
    print(f'🔄 Balance restored to: {user.wallet_balance}')
    
    print('🎯 Wallet integration test completed successfully')
    return True

test_wallet_integration()
"
```

### Template and URL Testing

```bash
# Test template loading and URL routing (common 5 Whys issues)
python manage.py shell -c "
from django.template.loader import get_template
from django.urls import reverse
from django.test import RequestFactory
from django.contrib.auth import get_user_model

User = get_user_model()

def test_template_and_urls():
    print('🧪 Testing templates and URLs...')
    
    # Test template loading for all agents
    agents = ['weather_reporter', 'five_whys_analyzer']
    
    for agent in agents:
        try:
            template = get_template(f'{agent}/detail.html')
            print(f'✅ Template loaded for {agent}: {template.origin.name}')
        except Exception as e:
            print(f'❌ Template failed for {agent}: {e}')
    
    # Test URL resolution
    url_tests = [
        ('core:homepage', []),
        ('core:marketplace', []),
        ('core:wallet', []),
        ('core:agent_detail', ['weather-reporter']),
        ('core:agent_detail', ['five-whys-analyzer']),
    ]
    
    for url_name, args in url_tests:
        try:
            url = reverse(url_name, args=args)
            print(f'✅ URL resolved {url_name}: {url}')
        except Exception as e:
            print(f'❌ URL failed {url_name}: {e}')
    
    print('🎯 Template and URL testing completed')

test_template_and_urls()
"
```

### Error Handling Testing

```bash
# Test error handling patterns (5 Whys comprehensive error handling)
python manage.py shell -c "
from five_whys_analyzer.processor import FiveWhysAnalyzerProcessor
from agent_base.models import BaseAgent
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

def test_error_handling():
    print('🧪 Testing error handling patterns...')
    
    processor = FiveWhysAnalyzerProcessor()
    user = User.objects.filter(is_superuser=True).first()
    
    # Test 1: Missing session_id
    try:
        result = processor.handle_chat_message(
            user=user,
            message='Test message'
            # No session_id - should auto-generate
        )
        print('✅ Missing session_id handled gracefully')
    except Exception as e:
        print(f'❌ Missing session_id caused error: {e}')
    
    # Test 2: Missing user
    try:
        result = processor.handle_chat_message(
            session_id=str(uuid.uuid4()),
            message='Test message'
            # No user - should raise clear error
        )
        print('❌ Missing user should have raised error')
    except Exception as e:
        print(f'✅ Missing user properly handled: {type(e).__name__}')
    
    # Test 3: Invalid message type
    try:
        result = processor.process_request(
            user=user,
            message_type='invalid_type'
        )
        print('❌ Invalid message type should have raised error')
    except ValueError as e:
        print(f'✅ Invalid message type properly handled: {e}')
    except Exception as e:
        print(f'❌ Unexpected error type: {e}')
    
    print('🎯 Error handling testing completed')

test_error_handling()
"
```

### Performance and Index Testing

```bash
# Test database performance and indexes (5 Whys optimization patterns)
python manage.py shell -c "
from django.db import connection
from five_whys_analyzer.models import FiveWhysAnalyzerRequest
from django.contrib.auth import get_user_model
import uuid
import time

User = get_user_model()

def test_performance():
    print('🧪 Testing database performance...')
    
    user = User.objects.first()
    if not user:
        print('❌ No user found for testing')
        return
    
    # Test 1: Session lookup performance
    session_id = str(uuid.uuid4())
    
    start_time = time.time()
    try:
        request = FiveWhysAnalyzerRequest.objects.filter(
            user=user,
            session_id=session_id,
            chat_active=True
        ).first()
        end_time = time.time()
        print(f'✅ Session lookup completed in {(end_time - start_time)*1000:.2f}ms')
    except Exception as e:
        print(f'❌ Session lookup failed: {e}')
    
    # Test 2: Index usage check
    with connection.cursor() as cursor:
        cursor.execute('EXPLAIN QUERY PLAN SELECT * FROM five_whys_analyzer_requests WHERE session_id = ?', [session_id])
        plan = cursor.fetchall()
        
        # Check if index is being used
        plan_text = str(plan).lower()
        if 'index' in plan_text:
            print('✅ Database index being used for session_id queries')
        else:
            print('⚠️ No index detected for session_id queries')
    
    print('🎯 Performance testing completed')

test_performance()
"
```

### Agent Integration Testing Commands

```bash
# Complete agent validation script
python manage.py shell -c "
def run_complete_agent_test(agent_slug):
    print(f'🚀 Running complete agent test for {agent_slug}')
    print('='*50)
    
    tests = [
        ('Environment', lambda: validate_agent_environment(agent_slug)),
        ('Lifecycle', lambda: test_agent_lifecycle(agent_slug)),
        ('Wallet', lambda: test_wallet_integration()),
        ('Templates & URLs', lambda: test_template_and_urls()),
        ('Error Handling', lambda: test_error_handling()),
        ('Performance', lambda: test_performance()),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f'\\n🧪 Running {test_name} test...')
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f'✅ {test_name} test PASSED')
            else:
                print(f'❌ {test_name} test FAILED')
        except Exception as e:
            print(f'❌ {test_name} test ERROR: {e}')
            results.append((test_name, False))
    
    print(f'\\n🎯 Test Summary for {agent_slug}:')
    print('='*30)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = '✅ PASS' if result else '❌ FAIL'
        print(f'{test_name}: {status}')
    
    print(f'\\nOverall: {passed}/{total} tests passed')
    if passed == total:
        print('🎉 All tests passed! Agent is ready for production.')
    else:
        print('⚠️ Some tests failed. Please review and fix issues.')

# Run for 5 Whys Analyzer
run_complete_agent_test('five-whys-analyzer')
"
```

### 5 Whys Debugging Workflow

When issues arise during agent development, follow this debugging workflow learned from 5 Whys experience:

```bash
# 1. Basic validation
python manage.py check
python manage.py showmigrations [agent_name]

# 2. Template validation
python manage.py shell -c "
from django.template.loader import get_template
template = get_template('[agent_name]/detail.html')
print('Template found:', template.origin.name)
"

# 3. URL validation
python manage.py shell -c "
from django.urls import reverse
url = reverse('core:agent_detail', args=['[agent-slug]'])
print('URL resolved:', url)
"

# 4. Model validation
python manage.py shell -c "
from [agent_name].models import *
from agent_base.models import BaseAgent
agent = BaseAgent.objects.get(slug='[agent-slug]')
print('Agent found:', agent.name)
"

# 5. Processor validation
python manage.py shell -c "
from [agent_name].processor import [AgentName]Processor
processor = [AgentName]Processor()
print('Processor initialized successfully')
"
```

### Production Readiness Checklist

Based on 5 Whys success patterns, verify these before deploying:

- [ ] **Template Loading**: Templates load without server restart
- [ ] **URL Routing**: All URLs resolve correctly with namespaces
- [ ] **Database**: Migrations applied, indexes created
- [ ] **Wallet Integration**: Delayed deduction pattern implemented
- [ ] **Error Handling**: Comprehensive try-catch blocks
- [ ] **Session Management**: UUID-based sessions (if applicable)
- [ ] **Status Tracking**: Request lifecycle properly managed
- [ ] **Environment Variables**: All required variables validated
- [ ] **Performance**: Database queries optimized with indexes
- [ ] **Testing**: Complete test suite passes

**🎯 Following these testing procedures ensures the same level of reliability achieved with the 5 Whys Analyzer.**

Happy coding! 🎉