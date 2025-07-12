from agent_base.processors import StandardWebhookProcessor
from django.utils import timezone
from django.conf import settings
from .models import FiveWhysAnalyzerRequest, FiveWhysAnalyzerResponse
import json
import uuid


class FiveWhysAnalyzerProcessor(StandardWebhookProcessor):
    """Dual-mode webhook processor for 5 Whys Analysis Agent - supports chat and report generation"""
    
    agent_slug = 'five-whys-analyzer'
    webhook_url = 'https://m8taq6tk.rpcld.cc/webhook/5-whys-web'
    agent_id = 'five-whys-001'
    
    def process_response(self, response_data, request_obj):
        """Required implementation of abstract method - delegates to specific handlers"""
        # This method is required by the base class but we handle responses 
        # differently in our dual-mode approach
        return self.process_report_response(response_data, request_obj)
    
    def process_request(self, **kwargs):
        """Handle both chat messages (free) and report generation (paid)"""
        message_type = kwargs.get('message_type', 'chat')
        
        if message_type == 'chat':
            return self.handle_chat_message(**kwargs)
        elif message_type == 'generate_report':
            return self.handle_report_generation(**kwargs)
        else:
            raise ValueError(f"Unknown message type: {message_type}")
    
    def handle_chat_message(self, **kwargs):
        """Handle free chat interactions - no wallet deduction"""
        user = kwargs.get('user')
        session_id = kwargs.get('session_id', str(uuid.uuid4()))
        user_message = kwargs.get('message', '')
        
        # Get the agent object
        from agent_base.models import BaseAgent
        try:
            agent = BaseAgent.objects.get(slug=self.agent_slug)
        except BaseAgent.DoesNotExist:
            raise Exception(f"Agent with slug '{self.agent_slug}' not found")
        
        # Get or create request object for this session
        request_obj, created = FiveWhysAnalyzerRequest.objects.get_or_create(
            user=user,
            session_id=session_id,
            chat_active=True,
            defaults={
                'agent': agent,
                'cost': 0,  # No cost for chat
                'status': 'pending'
            }
        )
        
        # Add user message to chat history
        chat_messages = request_obj.chat_messages
        chat_messages.append({
            'role': 'user',
            'message': user_message,
            'timestamp': timezone.now().isoformat()
        })
        request_obj.chat_messages = chat_messages
        request_obj.save()
        
        # Prepare chat payload for webhook
        chat_payload = {
            'message': {
                'text': f"Chat message: {user_message}. Provide helpful guidance about 5 Whys analysis. Do not generate the final report - just chat and help the user understand their problem."
            },
            'sessionId': session_id,
            'userId': str(user.id),
            'agentId': self.agent_id,
            'messageType': 'chat'
        }
        
        # Send to webhook
        response_data = self.make_request(chat_payload)
        
        # Process chat response (no wallet deduction)
        return self.process_chat_response(response_data, request_obj, user_message)
    
    def handle_report_generation(self, **kwargs):
        """Handle paid report generation - deduct wallet after success"""
        user = kwargs.get('user')
        session_id = kwargs.get('session_id')
        problem_statement = kwargs.get('problem_statement', '')
        context_info = kwargs.get('context_info', '')
        analysis_depth = kwargs.get('analysis_depth', 'standard')
        
        # Get the agent object
        from agent_base.models import BaseAgent
        try:
            agent = BaseAgent.objects.get(slug=self.agent_slug)
        except BaseAgent.DoesNotExist:
            raise Exception(f"Agent with slug '{self.agent_slug}' not found")
        
        # Get existing session or create new one
        try:
            request_obj = FiveWhysAnalyzerRequest.objects.get(
                user=user,
                session_id=session_id,
                chat_active=True
            )
        except FiveWhysAnalyzerRequest.DoesNotExist:
            # Create new request for report generation
            request_obj = FiveWhysAnalyzerRequest.objects.create(
                user=user,
                session_id=session_id,
                agent=agent,
                cost=8.0,  # Cost for report generation
                status='pending'
            )
        
        # Update request with report details
        request_obj.problem_statement = problem_statement
        request_obj.context_info = context_info
        request_obj.analysis_depth = analysis_depth
        request_obj.cost = 8.0  # Ensure cost is set for report
        request_obj.save()
        
        # Prepare report generation payload
        report_payload = {
            'message': {
                'text': f"Generate comprehensive 5 Whys analysis report.\nProblem: {problem_statement}\nContext: {context_info}\nDepth: {analysis_depth}\nChat History: {json.dumps(request_obj.chat_messages[-10:])}"
            },
            'sessionId': session_id,
            'userId': str(user.id),
            'agentId': self.agent_id,
            'messageType': 'report',
            'analysisDepth': analysis_depth
        }
        
        # Send to webhook
        response_data = self.make_request(report_payload)
        
        # Process report response (with wallet deduction)
        return self.process_report_response(response_data, request_obj)
    
    def process_chat_response(self, response_data, request_obj, user_message):
        """Process chat response - no wallet deduction"""
        try:
            # Extract chat response
            chat_response = response_data.get('output', response_data.get('message', 'I\'m here to help with 5 Whys analysis. What would you like to know?'))
            
            # Add assistant response to chat history
            chat_messages = request_obj.chat_messages
            chat_messages.append({
                'role': 'assistant',
                'message': chat_response,
                'timestamp': timezone.now().isoformat()
            })
            request_obj.chat_messages = chat_messages
            request_obj.status = 'completed'  # Chat message completed
            request_obj.save()
            
            # Get or create response object
            response_obj, created = FiveWhysAnalyzerResponse.objects.get_or_create(
                request=request_obj,
                defaults={
                    'success': True,
                    'processing_time': response_data.get('processing_time', 0)
                }
            )
            
            # Update response with chat data
            response_obj.chat_response = chat_response
            chat_history = response_obj.chat_history
            chat_history.append({
                'user_message': user_message,
                'assistant_response': chat_response,
                'timestamp': timezone.now().isoformat()
            })
            response_obj.chat_history = chat_history
            response_obj.save()
            
            print(f"{self.agent_slug}: Chat message processed - no wallet deduction")
            return response_obj
            
        except Exception as e:
            request_obj.status = 'failed'
            request_obj.save()
            raise Exception(f"Failed to process chat response: {e}")
    
    def process_report_response(self, response_data, request_obj):
        """Process report generation response - deduct wallet after success"""
        try:
            request_obj.status = 'processing'
            request_obj.save()
            
            # Extract report data
            final_report = response_data.get('output', response_data.get('report', ''))
            success = bool(final_report) and response_data.get('success', True)
            
            # Get or create response object
            response_obj, created = FiveWhysAnalyzerResponse.objects.get_or_create(
                request=request_obj,
                defaults={
                    'success': success,
                    'processing_time': response_data.get('processing_time', 0)
                }
            )
            
            if success:
                # Update with final report
                response_obj.final_report = final_report
                response_obj.report_metadata = {
                    'analysis_depth': request_obj.analysis_depth,
                    'generated_at': timezone.now().isoformat(),
                    'problem_statement': request_obj.problem_statement,
                    'context_info': request_obj.context_info
                }
                response_obj.save()
                
                # Mark request as report generated
                request_obj.report_generated = True
                request_obj.chat_active = False  # End chat session
                
                # ONLY deduct wallet balance after successful report generation
                request_obj.user.deduct_balance(
                    request_obj.cost,
                    f"5 Whys Analysis Agent - Final Report ({request_obj.analysis_depth})",
                    'five-whys-analyzer'
                )
                print(f"{self.agent_slug}: Wallet deducted {request_obj.cost} AED for successful report generation")
                
                request_obj.status = 'completed'
            else:
                request_obj.status = 'failed'
                response_obj.error_message = "Failed to generate report"
                response_obj.save()
            
            request_obj.processed_at = timezone.now()
            request_obj.save()
            
            return response_obj
            
        except Exception as e:
            request_obj.status = 'failed'
            request_obj.save()
            raise Exception(f"Failed to process report response: {e}")
    
    def prepare_message_text(self, **kwargs):
        """Legacy method for compatibility"""
        return kwargs.get('message', 'Process 5 Whys analysis')