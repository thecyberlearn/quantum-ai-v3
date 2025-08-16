"""
Security middleware for enhanced security headers and CSP.
"""

from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger('core.security')


class SecurityHeadersMiddleware:
    """
    Middleware to add comprehensive security headers to all responses.
    Implements Content Security Policy, security headers, and security monitoring.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def _needs_external_iframe_support(self, request):
        """
        Detect if this page needs external iframe support for CSP.
        Covers direct access agents, external wrapper pages, and future additions.
        """
        path = request.path
        
        # Direct access agent display pages
        if '/agents/' in path and path.endswith('/display/'):
            return True
        
        # External wrapper pages (events, forms, etc.)
        # Pattern: /<page_name>/ where page_name is in EXTERNAL_PAGES
        if path.count('/') == 2 and not path.startswith('/admin/') and not path.startswith('/auth/') and not path.startswith('/wallet/') and not path.startswith('/agents/'):
            # Import here to avoid circular imports
            from .views import EXTERNAL_PAGES
            page_name = path.strip('/')
            if page_name in EXTERNAL_PAGES:
                config = EXTERNAL_PAGES[page_name]
                # Only iframe and landing templates need CSP relaxation
                return config.get('template') in ['iframe', 'landing']
        
        return False

    def __call__(self, request):
        response = self.get_response(request)
        
        # Content Security Policy
        if not settings.DEBUG:
            # Check if this page needs external iframe support
            is_external_iframe_page = self._needs_external_iframe_support(request)
            
            if is_external_iframe_page:
                # Relaxed CSP for pages with external iframes (agents, events, forms, etc.)
                # Includes common external service domains for future-proofing
                csp_policy = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' https://js.stripe.com https://checkout.stripe.com "
                    "https://form.jotform.com https://www.jotform.com https://agent.jotform.com https://cdn.jotfor.ms "
                    "https://calendly.com https://assets.calendly.com "
                    "https://www.googletagmanager.com https://www.google-analytics.com "
                    "https://typeform.com https://*.typeform.com "
                    "https://airtable.com https://*.airtable.com "
                    "https://hubspot.com https://*.hubspot.com "
                    "https://zapier.com https://*.zapier.com; "
                    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com "
                    "https://form.jotform.com https://www.jotform.com https://agent.jotform.com https://cdn.jotfor.ms "
                    "https://calendly.com https://assets.calendly.com "
                    "https://typeform.com https://*.typeform.com "
                    "https://airtable.com https://*.airtable.com "
                    "https://hubspot.com https://*.hubspot.com "
                    "https://zapier.com https://*.zapier.com; "
                    "font-src 'self' https://fonts.gstatic.com "
                    "https://form.jotform.com https://www.jotform.com https://agent.jotform.com https://cdn.jotfor.ms "
                    "https://calendly.com https://assets.calendly.com "
                    "https://typeform.com https://*.typeform.com; "
                    "img-src 'self' data: https: blob:; "
                    "connect-src 'self' https: wss: ws:; "
                    "frame-src 'self' https: http:; "
                    "child-src 'self' https: http:; "
                    "object-src 'none'; "
                    "base-uri 'self'; "
                    "form-action 'self' https: http:; "
                    "frame-ancestors 'none';"
                )
            else:
                # Production CSP - Strict security for other pages
                csp_policy = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' https://js.stripe.com https://checkout.stripe.com; "
                    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                    "font-src 'self' https://fonts.gstatic.com; "
                    "img-src 'self' data: https: blob:; "
                    "connect-src 'self' https://api.stripe.com https://checkout.stripe.com; "
                    "frame-src 'self' https://js.stripe.com https://hooks.stripe.com; "
                    "object-src 'none'; "
                    "base-uri 'self'; "
                    "form-action 'self'; "
                    "frame-ancestors 'none'; "
                    "upgrade-insecure-requests;"
                )
        else:
            # Development CSP - More permissive for development tools
            csp_policy = (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https: blob:; "
                "connect-src 'self' ws: wss: https:; "
                "frame-src 'self' https: http:;"
            )
        
        response['Content-Security-Policy'] = csp_policy
        
        # Additional Security Headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=(), '
            'payment=(self "https://js.stripe.com"), '
            'usb=(), magnetometer=(), gyroscope=(), accelerometer=()'
        )
        
        # X-Frame-Options handling
        needs_iframe_support = is_external_iframe_page if not settings.DEBUG else self._needs_external_iframe_support(request)
        if needs_iframe_support:
            # Allow external iframe pages to be framed (they contain external iframes)
            response['X-Frame-Options'] = 'SAMEORIGIN'
        else:
            # Deny framing for all other pages
            response['X-Frame-Options'] = 'DENY'
        
        # Special handling for static assets (og-image, etc.)
        if request.path.startswith('/static/'):
            # Allow social media scrapers to access og-image and other static assets
            response['X-Frame-Options'] = 'SAMEORIGIN'
            response['Cache-Control'] = 'public, max-age=31536000'  # 1 year cache
            # Remove CSP for static assets to ensure accessibility
            if 'Content-Security-Policy' in response:
                del response['Content-Security-Policy']
        
        # Security for critical pages
        elif request.path.startswith('/admin/') or request.path.startswith('/wallet/'):
            response['X-Frame-Options'] = 'DENY'
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        # Log security events for monitoring
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Log administrative actions
            if request.path.startswith('/admin/') and request.method == 'POST':
                logger.info(f"Admin action by user {request.user.id} from IP {request.META.get('REMOTE_ADDR')}")
            
            # Log sensitive financial operations
            if request.path.startswith('/wallet/') and request.method == 'POST':
                logger.info(f"Wallet operation by user {request.user.id} from IP {request.META.get('REMOTE_ADDR')}")
            
            # Log agent executions
            if request.path.startswith('/agents/api/execute') and request.method == 'POST':
                logger.info(f"Agent execution by user {request.user.id} from IP {request.META.get('REMOTE_ADDR')}")
        
        # Log authentication failures
        if hasattr(request, 'user') and not request.user.is_authenticated:
            if request.path.startswith('/auth/') and request.method == 'POST':
                logger.warning(f"Failed authentication attempt from IP {request.META.get('REMOTE_ADDR')}")
        
        return response


class SecurityMonitoringMiddleware:
    """
    Middleware for security event monitoring and threat detection.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.suspicious_patterns = [
            '.env', 'wp-admin', 'phpmyadmin', '../', '<script', 'SELECT * FROM',
            'UNION SELECT', 'DROP TABLE', 'INSERT INTO', 'DELETE FROM',
            'etc/passwd', 'windows/system32', '../../../../', '../../../',
            'cmd.exe', '/bin/bash', 'eval(', 'exec(', 'system(',
            'base64_decode', 'shell_exec', 'file_get_contents',
            'fopen(', 'include(', 'require(', 'curl_exec',
            '<?php', '<%', '<jsp:', 'javascript:', 'vbscript:',
            'onload=', 'onerror=', 'onclick=', 'onfocus=',
            'document.cookie', 'document.location', 'window.location'
        ]
        
        # Track suspicious IPs for rate limiting
        self.suspicious_ips = set()
        self.failed_attempts = {}

    def __call__(self, request):
        # Check for suspicious patterns in URL and parameters
        self._check_suspicious_activity(request)
        
        response = self.get_response(request)
        
        # Log failed authentication attempts and track suspicious IPs
        if response.status_code == 401 or response.status_code == 403:
            self._log_security_event(request, 'auth_failure', f"Status: {response.status_code}")
            self._track_failed_attempt(request)
        
        # Log rate limit violations
        if hasattr(response, 'status_code') and response.status_code == 429:
            self._log_security_event(request, 'rate_limit_exceeded', f"Path: {request.path}")
        
        # Log suspicious response patterns
        if response.status_code == 500:
            self._log_security_event(request, 'server_error', f"Path: {request.path}")
        
        return response
    
    def _check_suspicious_activity(self, request):
        """Check for suspicious patterns in requests"""
        full_path = request.get_full_path()
        
        # Check URL for suspicious patterns
        for pattern in self.suspicious_patterns:
            if pattern.lower() in full_path.lower():
                self._log_security_event(
                    request, 
                    'suspicious_request', 
                    f"Pattern: {pattern}, Path: {full_path}"
                )
                break
        
        # Check for potential SQLi in parameters
        if request.GET:
            for key, value in request.GET.items():
                for pattern in ['SELECT', 'UNION', 'DROP', 'INSERT', 'DELETE']:
                    if pattern in str(value).upper():
                        self._log_security_event(
                            request,
                            'potential_sqli',
                            f"Parameter: {key}, Value: {value[:100]}"
                        )
                        break
    
    def _track_failed_attempt(self, request):
        """Track failed authentication attempts by IP"""
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = {'count': 0, 'last_attempt': None}
        
        self.failed_attempts[ip]['count'] += 1
        self.failed_attempts[ip]['last_attempt'] = timezone.now()
        
        # Mark IP as suspicious after 5 failed attempts
        if self.failed_attempts[ip]['count'] >= 5:
            self.suspicious_ips.add(ip)
            self._log_security_event(
                request, 
                'suspicious_ip_detected', 
                f"IP {ip} marked suspicious after {self.failed_attempts[ip]['count']} failed attempts"
            )
    
    def _log_security_event(self, request, event_type, details):
        """Log security events for monitoring"""
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous'
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:100]
        
        # Enhanced logging with more context
        logger.warning(
            f"Security Event: {event_type} - "
            f"IP: {ip} - "
            f"User: {user_id} - "
            f"Path: {request.path} - "
            f"Method: {request.method} - "
            f"UA: {user_agent} - "
            f"Referer: {request.META.get('HTTP_REFERER', 'none')[:100]} - "
            f"Details: {details}"
        )
        
        # Additional context for critical events
        if event_type in ['suspicious_request', 'potential_sqli', 'suspicious_ip_detected']:
            logger.critical(
                f"CRITICAL SECURITY ALERT: {event_type} - "
                f"IP: {ip} - User: {user_id} - {details}"
            )