from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from agent_base.models import BaseAgent
from .models import FiveWhysAnalyzerRequest, FiveWhysAnalyzerResponse
from .processor import FiveWhysAnalyzerProcessor
import json
import uuid


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


@method_decorator(csrf_exempt, name='dispatch')
class FiveWhysAnalyzerChatView(View):
    """Handle chat messages - free interactions"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            # Parse request data
            data = json.loads(request.body)
            
            # Get session ID or create new one
            session_id = data.get('session_id', str(uuid.uuid4()))
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({'error': 'Message cannot be empty'}, status=400)
            
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
                'message_type': 'chat',
                'wallet_balance': float(request.user.wallet_balance)  # No change expected
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch') 
class FiveWhysAnalyzerReportView(View):
    """Generate final report - paid interaction"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            # Parse request data
            data = json.loads(request.body)
            
            # Get report parameters
            session_id = data.get('session_id')
            problem_statement = data.get('problem_statement', '').strip()
            context_info = data.get('context_info', '').strip()
            analysis_depth = data.get('analysis_depth', 'standard')
            
            if not session_id:
                return JsonResponse({'error': 'Session ID required'}, status=400)
            
            if not problem_statement:
                return JsonResponse({'error': 'Problem statement required'}, status=400)
            
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
            return JsonResponse({'error': '5 Whys Analysis Agent not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


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
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Legacy view for compatibility
@method_decorator(csrf_exempt, name='dispatch')
class FiveWhysAnalyzerProcessView(View):
    """Legacy process view - redirects to chat interface"""
    
    def post(self, request):
        return JsonResponse({
            'error': 'This endpoint is deprecated. Use the chat interface instead.',
            'redirect': '/agents/five-whys-analyzer/'
        }, status=410)