from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views import View
from agent_base.models import BaseAgent
from .models import FiveWhysAnalyzerRequest, FiveWhysAnalyzerResponse
from .processor import FiveWhysAnalyzerProcessor
import json
import uuid
import logging

logger = logging.getLogger(__name__)

# Constants for input validation
MAX_MESSAGE_LENGTH = 5000
MAX_PROBLEM_STATEMENT_LENGTH = 2000
MAX_CONTEXT_LENGTH = 3000
ALLOWED_ANALYSIS_DEPTHS = ['standard', 'detailed', 'comprehensive']


def validate_input_data(data, validation_type="chat"):
    """Validate and sanitize input data"""
    errors = []
    
    if validation_type == "chat":
        message = data.get('message', '').strip()
        if not message:
            errors.append("Message cannot be empty")
        elif len(message) > MAX_MESSAGE_LENGTH:
            errors.append(f"Message too long (max {MAX_MESSAGE_LENGTH} characters)")
        
        # Basic HTML/script tag detection
        if '<script' in message.lower() or '<iframe' in message.lower():
            errors.append("Invalid characters in message")
            
    elif validation_type == "report":
        problem_statement = data.get('problem_statement', '').strip()
        context_info = data.get('context_info', '').strip()
        analysis_depth = data.get('analysis_depth', 'standard')
        
        if not problem_statement:
            errors.append("Problem statement is required")
        elif len(problem_statement) > MAX_PROBLEM_STATEMENT_LENGTH:
            errors.append(f"Problem statement too long (max {MAX_PROBLEM_STATEMENT_LENGTH} characters)")
            
        if context_info and len(context_info) > MAX_CONTEXT_LENGTH:
            errors.append(f"Context information too long (max {MAX_CONTEXT_LENGTH} characters)")
            
        if analysis_depth not in ALLOWED_ANALYSIS_DEPTHS:
            errors.append("Invalid analysis depth")
    
    return errors


def get_safe_error_response(error, request_type="request"):
    """Return sanitized error message for production"""
    logger.error(f"5 Whys Analyzer {request_type} error: {str(error)}")
    
    # Return generic error messages in production
    if hasattr(error, '__class__'):
        error_type = error.__class__.__name__
        if 'DoesNotExist' in error_type:
            return 'Resource not found'
        elif 'ValidationError' in error_type:
            return 'Invalid input provided'
        elif 'PermissionDenied' in error_type:
            return 'Access denied'
        elif 'IntegrityError' in error_type:
            return 'Data conflict occurred'
    
    # Generic fallback
    return 'An error occurred while processing your request'


@login_required
def five_whys_analyzer_detail(request):
    """Detail page for 5 Whys Analysis Agent with chat interface"""
    try:
        agent = BaseAgent.objects.get(slug='five-whys-analyzer')
    except BaseAgent.DoesNotExist:
        messages.error(request, '5 Whys Analysis Agent agent not found.')
        return redirect('core:homepage')
    
    # Get user's active chat sessions
    active_sessions = FiveWhysAnalyzerRequest.objects.filter(
        user=request.user,
        chat_active=True
    ).order_by('-created_at')[:5]
    
    # Get user's completed reports
    completed_reports = FiveWhysAnalyzerRequest.objects.filter(
        user=request.user,
        report_generated=True
    ).order_by('-created_at')[:10]
    
    context = {
        'agent': agent,
        'active_sessions': active_sessions,
        'completed_reports': completed_reports
    }
    return render(request, 'five_whys_analyzer/detail.html', context)


class FiveWhysAnalyzerChatView(View):
    """Handle chat messages - free interactions"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            # Parse request data
            data = json.loads(request.body)
            
            # Validate input data
            validation_errors = validate_input_data(data, "chat")
            if validation_errors:
                return JsonResponse({'error': '; '.join(validation_errors)}, status=400)
            
            # Get session ID or create new one
            session_id = data.get('session_id', str(uuid.uuid4()))
            user_message = data.get('message', '').strip()
            
            # Process chat message (no wallet deduction)
            processor = FiveWhysAnalyzerProcessor()
            result = processor.handle_chat_message(
                user=request.user,
                session_id=session_id,
                message=user_message
            )
            
            return JsonResponse({
                'success': True,
                'session_id': session_id,
                'response': result.chat_response,
                'message_type': 'chat'
            })
            
        except Exception as e:
            error_message = get_safe_error_response(e, "chat")
            return JsonResponse({'error': error_message}, status=500)


class FiveWhysAnalyzerReportView(View):
    """Generate final report - paid interaction"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            # Parse request data
            data = json.loads(request.body)
            
            # Validate input data
            validation_errors = validate_input_data(data, "report")
            if validation_errors:
                return JsonResponse({'error': '; '.join(validation_errors)}, status=400)
            
            # Get report parameters
            session_id = data.get('session_id')
            problem_statement = data.get('problem_statement', '').strip()
            context_info = data.get('context_info', '').strip()
            analysis_depth = data.get('analysis_depth', 'standard')
            
            if not session_id:
                return JsonResponse({'error': 'Session ID required'}, status=400)
            
            # Get agent for price checking
            agent = BaseAgent.objects.get(slug='five-whys-analyzer')
            
            # Check wallet balance
            if not request.user.has_sufficient_balance(agent.price):
                return JsonResponse({'error': 'Insufficient wallet balance'}, status=400)
            
            # Process report generation (wallet deduction after success)
            processor = FiveWhysAnalyzerProcessor()
            result = processor.handle_report_generation(
                user=request.user,
                session_id=session_id,
                problem_statement=problem_statement,
                context_info=context_info,
                analysis_depth=analysis_depth
            )
            
            # Refresh user to get updated wallet balance
            request.user.refresh_from_db()
            
            return JsonResponse({
                'success': True,
                'session_id': session_id,
                'report': result.final_report,
                'message_type': 'report',
                'analysis_depth': analysis_depth,
                'wallet_balance': float(request.user.wallet_balance)
            })
            
        except BaseAgent.DoesNotExist:
            logger.error("5 Whys Analysis Agent not found in database")
            return JsonResponse({'error': 'Service temporarily unavailable'}, status=404)
        except Exception as e:
            error_message = get_safe_error_response(e, "report")
            return JsonResponse({'error': error_message}, status=500)


@login_required
def five_whys_analyzer_session(request, session_id):
    """Get chat session data"""
    try:
        session_request = FiveWhysAnalyzerRequest.objects.get(
            session_id=session_id,
            user=request.user
        )
        
        session_data = {
            'session_id': session_id,
            'chat_messages': session_request.chat_messages,
            'chat_active': session_request.chat_active,
            'report_generated': session_request.report_generated,
            'problem_statement': session_request.problem_statement,
            'context_info': session_request.context_info,
            'analysis_depth': session_request.analysis_depth
        }
        
        # Add final report if generated
        if session_request.report_generated and hasattr(session_request, 'response'):
            session_data['final_report'] = session_request.response.final_report
            session_data['report_metadata'] = session_request.response.report_metadata
        
        return JsonResponse({
            'success': True,
            'session': session_data
        })
        
    except FiveWhysAnalyzerRequest.DoesNotExist:
        logger.warning(f"Session {session_id} not found for user {request.user.id}")
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        error_message = get_safe_error_response(e, "session")
        return JsonResponse({'error': error_message}, status=500)


# Legacy view for compatibility
class FiveWhysAnalyzerProcessView(View):
    """Legacy process view - redirects to chat interface"""
    
    def post(self, request):
        return JsonResponse({
            'error': 'This endpoint is deprecated. Use the chat interface instead.',
            'redirect': '/agents/five-whys-analyzer/'
        }, status=410)