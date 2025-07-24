import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.contrib import messages

from .models import EmailWriterRequest
from .processor import EmailWriterProcessor


def email_writer_detail(request):
    """Email Writer agent detail page"""
    context = {
        'agent_title': 'Email Writer',
        'agent_subtitle': 'Generate professional emails with AI-powered content creation',
        'page_title': 'Email Writer Agent - NetCop AI Hub'
    }
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                # Validate form data
                email_type = request.POST.get('email_type', '').strip()
                recipient = request.POST.get('recipient', '').strip()
                main_message = request.POST.get('main_message', '').strip()
                tone = request.POST.get('tone', 'professional')
                length = request.POST.get('length', 'medium')
                subject = request.POST.get('subject', '').strip()
                
                # Basic validation
                if not email_type or not recipient or not main_message:
                    return JsonResponse({
                        'error': 'Please fill in all required fields',
                        'success': False
                    })
                
                if len(main_message) < 10:
                    return JsonResponse({
                        'error': 'Main message must be at least 10 characters long',
                        'success': False
                    })
                
                # Initialize processor
                processor = EmailWriterProcessor()
                
                # Check wallet balance
                if not processor.check_wallet_balance(request.user):
                    return JsonResponse({
                        'error': f'Insufficient wallet balance. You need {processor.cost:.2f} AED.',
                        'success': False
                    })
                
                # Create request object
                email_request = EmailWriterRequest.objects.create(
                    user=request.user,
                    email_type=email_type,
                    recipient=recipient,
                    subject=subject,
                    main_message=main_message,
                    tone=tone,
                    length=length,
                    status='pending'
                )
                
                # Process the request
                try:
                    result = processor.process_request(email_request)
                    
                    if result.get('success'):
                        return JsonResponse({
                            'success': True,
                            'request_id': email_request.id,
                            'message': 'Email generation started successfully',
                            'wallet_balance': float(request.user.wallet_balance)
                        })
                    else:
                        return JsonResponse({
                            'error': result.get('error', 'Failed to process email generation'),
                            'success': False
                        })
                        
                except Exception as e:
                    return JsonResponse({
                        'error': f'Processing error: {str(e)}',
                        'success': False
                    })
                
            except Exception as e:
                return JsonResponse({
                    'error': f'Request error: {str(e)}',
                    'success': False
                })
        else:
            # Handle regular form submission (non-AJAX)
            messages.error(request, 'Please enable JavaScript for the best experience.')
    
    return render(request, 'email_writer/detail.html', context)


@require_http_methods(["GET"])
def email_writer_status(request, request_id):
    """Check status of email generation request"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        email_request = get_object_or_404(
            EmailWriterRequest, 
            id=request_id, 
            user=request.user
        )
        
        processor = EmailWriterProcessor()
        status_data = processor.get_request_status(email_request)
        
        # Add wallet balance to response
        status_data['wallet_balance'] = float(request.user.wallet_balance)
        
        # If completed, include the email content
        if status_data.get('status') == 'completed' and email_request.email_content:
            status_data['email_content'] = email_request.email_content
            status_data['email_type'] = email_request.get_email_type_display()
            status_data['recipient'] = email_request.recipient
            status_data['tone'] = email_request.get_tone_display()
            status_data['length'] = email_request.get_length_display()
            status_data['subject'] = email_request.subject
        
        return JsonResponse(status_data)
        
    except EmailWriterRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)