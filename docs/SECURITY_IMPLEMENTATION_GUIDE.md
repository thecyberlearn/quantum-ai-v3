# Security Implementation Guide

Comprehensive security requirements and implementation patterns for agent templates.

## Security Principles

### 1. Defense in Depth
- **Multiple layers of protection** at different levels
- **Input validation** at client and server side
- **Output encoding** for all dynamic content
- **Access control** at every endpoint

### 2. Least Privilege
- **Minimal permissions** for each component
- **Restricted access** to sensitive data
- **Limited functionality** exposure

### 3. Secure by Default
- **Safe defaults** for all configurations
- **Explicit security** rather than assumed
- **Fail-safe mechanisms** when security fails

## Input Validation and Sanitization

### Client-Side Input Validation
```javascript
// Input Sanitization Utilities
const InputValidator = {
    // Basic HTML sanitization
    sanitizeHTML(input) {
        return input
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#x27;')
            .replace(/\//g, '&#x2F;');
    },
    
    // File upload validation
    validateFile(file, allowedTypes = [], maxSize = 10 * 1024 * 1024) {
        const errors = [];
        
        // Check file type
        if (allowedTypes.length > 0) {
            const fileType = file.type.toLowerCase();
            const fileName = file.name.toLowerCase();
            
            const isValidType = allowedTypes.some(type => {
                if (type.includes('*')) {
                    return fileType.startsWith(type.replace('*', ''));
                }
                return fileType === type || fileName.endsWith(type);
            });
            
            if (!isValidType) {
                errors.push(`File type not allowed. Allowed types: ${allowedTypes.join(', ')}`);
            }
        }
        
        // Check file size
        if (file.size > maxSize) {
            errors.push(`File too large. Maximum size: ${(maxSize / (1024 * 1024)).toFixed(1)}MB`);
        }
        
        // Check for dangerous file extensions
        const dangerousExtensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.vbs', '.js', '.jar'];
        const fileName = file.name.toLowerCase();
        
        if (dangerousExtensions.some(ext => fileName.endsWith(ext))) {
            errors.push('Potentially dangerous file type detected');
        }
        
        return {
            isValid: errors.length === 0,
            errors
        };
    },
    
    // Text input validation
    validateText(input, options = {}) {
        const {
            required = false,
            minLength = 0,
            maxLength = Infinity,
            pattern = null,
            allowHTML = false
        } = options;
        
        const errors = [];
        
        // Check required
        if (required && (!input || input.trim().length === 0)) {
            errors.push('This field is required');
        }
        
        if (input && input.length > 0) {
            // Check length
            if (input.length < minLength) {
                errors.push(`Minimum length is ${minLength} characters`);
            }
            
            if (input.length > maxLength) {
                errors.push(`Maximum length is ${maxLength} characters`);
            }
            
            // Check pattern
            if (pattern && !pattern.test(input)) {
                errors.push('Invalid format');
            }
            
            // Check for HTML if not allowed
            if (!allowHTML && /<[^>]*>/.test(input)) {
                errors.push('HTML tags are not allowed');
            }
        }
        
        return {
            isValid: errors.length === 0,
            errors,
            sanitized: allowHTML ? input : this.sanitizeHTML(input)
        };
    },
    
    // Email validation
    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const isValid = emailRegex.test(email);
        
        return {
            isValid,
            errors: isValid ? [] : ['Please enter a valid email address'],
            sanitized: this.sanitizeHTML(email)
        };
    },
    
    // URL validation
    validateURL(url) {
        try {
            const urlObj = new URL(url);
            
            // Check for allowed protocols
            const allowedProtocols = ['http:', 'https:'];
            if (!allowedProtocols.includes(urlObj.protocol)) {
                return {
                    isValid: false,
                    errors: ['Only HTTP and HTTPS URLs are allowed'],
                    sanitized: ''
                };
            }
            
            return {
                isValid: true,
                errors: [],
                sanitized: urlObj.toString()
            };
        } catch (error) {
            return {
                isValid: false,
                errors: ['Please enter a valid URL'],
                sanitized: ''
            };
        }
    }
};
```

### Advanced HTML Sanitization
```javascript
// Advanced HTML Sanitization
const HTMLSanitizer = {
    // Allowed tags and attributes
    allowedTags: ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
    allowedAttributes: {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'width', 'height'],
        'all': ['class', 'id']
    },
    
    // Comprehensive sanitization
    sanitize(html) {
        if (!html || typeof html !== 'string') {
            return '';
        }
        
        // Create temporary container
        const temp = document.createElement('div');
        temp.innerHTML = html;
        
        // Remove dangerous elements
        this.removeDangerousElements(temp);
        
        // Sanitize allowed elements
        this.sanitizeAllowedElements(temp);
        
        return temp.innerHTML;
    },
    
    removeDangerousElements(container) {
        const dangerousTags = [
            'script', 'style', 'iframe', 'object', 'embed', 'form', 'input',
            'button', 'textarea', 'select', 'option', 'meta', 'link', 'base'
        ];
        
        dangerousTags.forEach(tag => {
            const elements = container.querySelectorAll(tag);
            elements.forEach(el => el.remove());
        });
        
        // Remove comments
        const walker = document.createTreeWalker(
            container,
            NodeFilter.SHOW_COMMENT,
            null,
            false
        );
        
        const comments = [];
        let node;
        while (node = walker.nextNode()) {
            comments.push(node);
        }
        
        comments.forEach(comment => comment.remove());
    },
    
    sanitizeAllowedElements(container) {
        const allElements = container.querySelectorAll('*');
        
        allElements.forEach(el => {
            const tagName = el.tagName.toLowerCase();
            
            // Remove disallowed tags
            if (!this.allowedTags.includes(tagName)) {
                el.remove();
                return;
            }
            
            // Clean attributes
            const allowedAttrs = [
                ...(this.allowedAttributes[tagName] || []),
                ...(this.allowedAttributes.all || [])
            ];
            
            // Remove dangerous attributes
            Array.from(el.attributes).forEach(attr => {
                const attrName = attr.name.toLowerCase();
                
                // Remove event handlers
                if (attrName.startsWith('on')) {
                    el.removeAttribute(attrName);
                    return;
                }
                
                // Remove javascript: URLs
                if (attr.value && attr.value.toLowerCase().includes('javascript:')) {
                    el.removeAttribute(attrName);
                    return;
                }
                
                // Remove data attributes (except specific ones)
                if (attrName.startsWith('data-') && !['data-id', 'data-value'].includes(attrName)) {
                    el.removeAttribute(attrName);
                    return;
                }
                
                // Remove non-allowed attributes
                if (!allowedAttrs.includes(attrName)) {
                    el.removeAttribute(attrName);
                }
            });
        });
    },
    
    // Safe content setting
    safeSetHTML(element, content) {
        if (!element || !content) return;
        
        const sanitizedContent = this.sanitize(content);
        element.innerHTML = sanitizedContent;
    },
    
    // Safe content appending
    safeAppendHTML(element, content) {
        if (!element || !content) return;
        
        const sanitizedContent = this.sanitize(content);
        element.insertAdjacentHTML('beforeend', sanitizedContent);
    }
};
```

## XSS Prevention

### Content Security Policy (CSP)
```html
<!-- Add to base template head -->
<meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    script-src 'self' 'unsafe-inline';
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
    font-src 'self' https://fonts.gstatic.com;
    img-src 'self' data: https:;
    connect-src 'self';
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'self';
">
```

### Django Template Security
```html
<!-- Django template security patterns -->

<!-- Always use autoescape -->
{% autoescape on %}
    {{ user_content }}
{% endautoescape %}

<!-- For JSON data -->
<script>
    const userData = {{ user_data|escapejs }};
</script>

<!-- For HTML content that must allow some tags -->
{% load custom_filters %}
{{ user_content|safe_html }}

<!-- For URLs -->
<a href="{{ user_url|urlencode }}">Link</a>

<!-- For attributes -->
<div class="{{ css_class|escape }}">Content</div>
```

### JavaScript XSS Prevention
```javascript
// XSS Prevention Utilities
const XSSProtection = {
    // Escape content for HTML context
    escapeHTML(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },
    
    // Escape content for JavaScript context
    escapeJS(str) {
        return str
            .replace(/\\/g, '\\\\')
            .replace(/'/g, "\\'")
            .replace(/"/g, '\\"')
            .replace(/\r/g, '\\r')
            .replace(/\n/g, '\\n')
            .replace(/\t/g, '\\t')
            .replace(/\f/g, '\\f')
            .replace(/\v/g, '\\v')
            .replace(/\0/g, '\\0');
    },
    
    // Escape content for CSS context
    escapeCSS(str) {
        return str.replace(/[<>"'&]/g, function(match) {
            return '\\' + match.charCodeAt(0).toString(16) + ' ';
        });
    },
    
    // Escape content for URL context
    escapeURL(str) {
        return encodeURIComponent(str);
    },
    
    // Safe DOM manipulation
    safeSetText(element, text) {
        if (element && typeof text === 'string') {
            element.textContent = text;
        }
    },
    
    safeSetAttribute(element, name, value) {
        if (element && typeof name === 'string' && typeof value === 'string') {
            // Prevent dangerous attributes
            const dangerousAttrs = ['onclick', 'onload', 'onerror', 'onmouseover'];
            if (dangerousAttrs.includes(name.toLowerCase())) {
                return false;
            }
            
            element.setAttribute(name, value);
            return true;
        }
        return false;
    }
};
```

## CSRF Protection

### Django CSRF Implementation
```python
# Django settings for CSRF protection
CSRF_COOKIE_SECURE = True  # Use HTTPS only
CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript access
CSRF_COOKIE_SAMESITE = 'Strict'  # Prevent cross-site requests
CSRF_TRUSTED_ORIGINS = ['https://yourdomain.com']
```

### JavaScript CSRF Handling
```javascript
// CSRF Token Management
const CSRFManager = {
    // Get CSRF token from cookie
    getTokenFromCookie() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        return null;
    },
    
    // Get CSRF token from form
    getTokenFromForm() {
        const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
        return tokenInput ? tokenInput.value : null;
    },
    
    // Get CSRF token from meta tag
    getTokenFromMeta() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.getAttribute('content') : null;
    },
    
    // Get CSRF token (try multiple sources)
    getToken() {
        return this.getTokenFromForm() || 
               this.getTokenFromCookie() || 
               this.getTokenFromMeta();
    },
    
    // Add CSRF token to headers
    addToHeaders(headers = {}) {
        const token = this.getToken();
        if (token) {
            headers['X-CSRFToken'] = token;
        }
        return headers;
    },
    
    // Add CSRF token to FormData
    addToFormData(formData) {
        const token = this.getToken();
        if (token) {
            formData.append('csrfmiddlewaretoken', token);
        }
        return formData;
    }
};

// Usage with fetch
async function secureRequest(url, options = {}) {
    const headers = CSRFManager.addToHeaders(options.headers || {});
    
    return fetch(url, {
        ...options,
        headers,
        credentials: 'same-origin'  // Include cookies
    });
}
```

## File Upload Security

### Client-Side File Validation
```javascript
// Secure File Upload Handler
const SecureFileUpload = {
    // Allowed file types
    allowedTypes: {
        'image': ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'],
        'document': ['application/pdf', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        'data': ['text/csv', 'application/json', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
    },
    
    // Maximum file sizes (in bytes)
    maxSizes: {
        'image': 5 * 1024 * 1024,      // 5MB
        'document': 10 * 1024 * 1024,  // 10MB
        'data': 25 * 1024 * 1024       // 25MB
    },
    
    // Validate file
    validateFile(file, category = 'document') {
        const errors = [];
        
        // Check file exists
        if (!file || !file.name) {
            errors.push('No file selected');
            return { isValid: false, errors };
        }
        
        // Check file size
        const maxSize = this.maxSizes[category];
        if (file.size > maxSize) {
            errors.push(`File too large. Maximum size: ${(maxSize / (1024 * 1024)).toFixed(1)}MB`);
        }
        
        // Check file type
        const allowedTypes = this.allowedTypes[category];
        if (!allowedTypes.includes(file.type)) {
            errors.push(`Invalid file type. Allowed types: ${allowedTypes.join(', ')}`);
        }
        
        // Check file name
        const fileName = file.name.toLowerCase();
        const dangerousExtensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.vbs', '.js', '.jar', '.php', '.asp', '.aspx'];
        
        if (dangerousExtensions.some(ext => fileName.endsWith(ext))) {
            errors.push('Potentially dangerous file type detected');
        }
        
        // Check for null bytes
        if (file.name.includes('\0')) {
            errors.push('Invalid file name');
        }
        
        // Check file name length
        if (file.name.length > 255) {
            errors.push('File name too long');
        }
        
        return {
            isValid: errors.length === 0,
            errors
        };
    },
    
    // Secure file upload
    async uploadFile(file, endpoint, category = 'document') {
        // Validate file
        const validation = this.validateFile(file, category);
        if (!validation.isValid) {
            throw new Error(validation.errors.join(', '));
        }
        
        // Create FormData
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', category);
        
        // Add CSRF token
        CSRFManager.addToFormData(formData);
        
        // Upload with progress tracking
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    this.updateProgress(percentComplete);
                }
            });
            
            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (error) {
                        reject(new Error('Invalid response format'));
                    }
                } else {
                    reject(new Error(`Upload failed: ${xhr.status}`));
                }
            });
            
            xhr.addEventListener('error', () => {
                reject(new Error('Upload failed'));
            });
            
            xhr.addEventListener('timeout', () => {
                reject(new Error('Upload timeout'));
            });
            
            xhr.timeout = 30000; // 30 second timeout
            xhr.open('POST', endpoint);
            xhr.send(formData);
        });
    },
    
    updateProgress(percent) {
        const progressBar = document.querySelector('.upload-progress');
        if (progressBar) {
            progressBar.style.width = `${percent}%`;
        }
    }
};
```

## Content Filtering

### Input Content Filtering
```javascript
// Content Filter for User Input
const ContentFilter = {
    // Profanity and inappropriate content filter
    inappropriateTerms: [
        // Add terms as needed (consider using external service)
    ],
    
    // Spam detection patterns
    spamPatterns: [
        /(.)\1{4,}/g,                    // Repeated characters
        /http[s]?:\/\/[^\s]+/gi,         // URLs
        /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g, // Phone numbers
        /[A-Z]{3,}/g,                    // Excessive caps
        /(.{1,})\1{3,}/g                 // Repeated words/phrases
    ],
    
    // Filter content
    filterContent(content) {
        if (!content || typeof content !== 'string') {
            return { isValid: true, filtered: content, warnings: [] };
        }
        
        const warnings = [];
        let filtered = content;
        
        // Check for inappropriate terms
        const inappropriateFound = this.inappropriateTerms.some(term => 
            content.toLowerCase().includes(term.toLowerCase())
        );
        
        if (inappropriateFound) {
            warnings.push('Content contains inappropriate language');
        }
        
        // Check for spam patterns
        let spamScore = 0;
        this.spamPatterns.forEach(pattern => {
            const matches = content.match(pattern);
            if (matches) {
                spamScore += matches.length;
            }
        });
        
        if (spamScore > 3) {
            warnings.push('Content appears to be spam');
        }
        
        // Check content length
        if (content.length > 10000) {
            warnings.push('Content is very long');
        }
        
        // Basic content sanitization
        filtered = content.trim();
        
        return {
            isValid: warnings.length === 0,
            filtered,
            warnings,
            spamScore
        };
    },
    
    // Rate limiting for content submission
    submissionTimes: new Map(),
    
    checkRateLimit(userId, maxSubmissions = 5, timeWindow = 60000) {
        const now = Date.now();
        const userSubmissions = this.submissionTimes.get(userId) || [];
        
        // Remove old submissions
        const recentSubmissions = userSubmissions.filter(time => 
            now - time < timeWindow
        );
        
        if (recentSubmissions.length >= maxSubmissions) {
            return {
                allowed: false,
                message: 'Too many submissions. Please wait before submitting again.'
            };
        }
        
        // Add current submission
        recentSubmissions.push(now);
        this.submissionTimes.set(userId, recentSubmissions);
        
        return {
            allowed: true,
            remaining: maxSubmissions - recentSubmissions.length
        };
    }
};
```

## Secure Communication

### API Security
```javascript
// Secure API Communication
const SecureAPI = {
    // Base configuration
    config: {
        baseURL: '/api/v1',
        timeout: 30000,
        retryAttempts: 3,
        retryDelay: 1000
    },
    
    // Make secure request
    async request(endpoint, options = {}) {
        const url = `${this.config.baseURL}${endpoint}`;
        
        // Default security headers
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...options.headers
        };
        
        // Add CSRF token
        CSRFManager.addToHeaders(headers);
        
        const config = {
            method: 'GET',
            headers,
            credentials: 'same-origin',
            timeout: this.config.timeout,
            ...options
        };
        
        let lastError;
        
        // Retry logic
        for (let attempt = 0; attempt < this.config.retryAttempts; attempt++) {
            try {
                const response = await this.makeRequest(url, config);
                
                // Check if response is valid
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                // Validate response content type
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error('Invalid response content type');
                }
                
                const data = await response.json();
                
                // Validate response structure
                if (!this.validateResponse(data)) {
                    throw new Error('Invalid response structure');
                }
                
                return data;
                
            } catch (error) {
                lastError = error;
                
                // Don't retry on client errors
                if (error.status && error.status >= 400 && error.status < 500) {
                    throw error;
                }
                
                // Wait before retry
                if (attempt < this.config.retryAttempts - 1) {
                    await this.delay(this.config.retryDelay * (attempt + 1));
                }
            }
        }
        
        throw lastError;
    },
    
    // Make actual request with timeout
    async makeRequest(url, config) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), config.timeout);
        
        try {
            const response = await fetch(url, {
                ...config,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            return response;
            
        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    },
    
    // Validate response structure
    validateResponse(data) {
        // Basic response validation
        if (!data || typeof data !== 'object') {
            return false;
        }
        
        // Check for required fields
        const requiredFields = ['status', 'data'];
        return requiredFields.every(field => field in data);
    },
    
    // Delay utility
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },
    
    // Secure file upload
    async uploadFile(endpoint, file, additionalData = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Add additional data
        Object.entries(additionalData).forEach(([key, value]) => {
            formData.append(key, value);
        });
        
        // Add CSRF token
        CSRFManager.addToFormData(formData);
        
        return this.request(endpoint, {
            method: 'POST',
            body: formData,
            headers: {
                // Don't set Content-Type for FormData
            }
        });
    }
};
```

## Error Handling Security

### Secure Error Display
```javascript
// Secure Error Handling
const SecureErrorHandler = {
    // Error types
    errorTypes: {
        VALIDATION: 'validation',
        AUTHENTICATION: 'authentication',
        AUTHORIZATION: 'authorization',
        SERVER: 'server',
        NETWORK: 'network',
        RATE_LIMIT: 'rate_limit'
    },
    
    // Handle errors securely
    handleError(error, context = {}) {
        console.error('Error occurred:', error, context);
        
        // Determine error type
        const errorType = this.categorizeError(error);
        
        // Get user-friendly message
        const userMessage = this.getUserMessage(errorType, error);
        
        // Log error for monitoring (don't expose sensitive info)
        this.logError(errorType, error, context);
        
        // Display error to user
        this.displayError(userMessage, errorType);
        
        // Handle specific error types
        switch (errorType) {
            case this.errorTypes.AUTHENTICATION:
                this.handleAuthError();
                break;
            case this.errorTypes.RATE_LIMIT:
                this.handleRateLimitError();
                break;
            case this.errorTypes.VALIDATION:
                this.handleValidationError(error);
                break;
        }
    },
    
    // Categorize error
    categorizeError(error) {
        if (error.status === 401) return this.errorTypes.AUTHENTICATION;
        if (error.status === 403) return this.errorTypes.AUTHORIZATION;
        if (error.status === 429) return this.errorTypes.RATE_LIMIT;
        if (error.status >= 400 && error.status < 500) return this.errorTypes.VALIDATION;
        if (error.status >= 500) return this.errorTypes.SERVER;
        if (error.name === 'NetworkError') return this.errorTypes.NETWORK;
        return this.errorTypes.SERVER;
    },
    
    // Get user-friendly message
    getUserMessage(errorType, error) {
        const messages = {
            [this.errorTypes.VALIDATION]: 'Please check your input and try again.',
            [this.errorTypes.AUTHENTICATION]: 'Please log in to continue.',
            [this.errorTypes.AUTHORIZATION]: 'You do not have permission to perform this action.',
            [this.errorTypes.SERVER]: 'Something went wrong. Please try again later.',
            [this.errorTypes.NETWORK]: 'Network connection error. Please check your connection.',
            [this.errorTypes.RATE_LIMIT]: 'Too many requests. Please wait before trying again.'
        };
        
        return messages[errorType] || 'An unexpected error occurred.';
    },
    
    // Log error for monitoring
    logError(errorType, error, context) {
        const logData = {
            type: errorType,
            message: error.message,
            status: error.status,
            timestamp: new Date().toISOString(),
            context: this.sanitizeContext(context)
        };
        
        // Send to monitoring service (implement as needed)
        // this.sendToMonitoring(logData);
    },
    
    // Sanitize context for logging
    sanitizeContext(context) {
        const sanitized = { ...context };
        
        // Remove sensitive information
        const sensitiveKeys = ['password', 'token', 'key', 'secret'];
        sensitiveKeys.forEach(key => {
            if (sanitized[key]) {
                sanitized[key] = '[REDACTED]';
            }
        });
        
        return sanitized;
    },
    
    // Display error to user
    displayError(message, type) {
        const errorContainer = document.getElementById('errorContainer');
        if (!errorContainer) return;
        
        const errorElement = document.createElement('div');
        errorElement.className = `alert alert-error alert-${type}`;
        errorElement.innerHTML = `
            <span class="alert-icon">⚠️</span>
            <span class="alert-message">${this.escapeHTML(message)}</span>
            <button type="button" class="alert-close" onclick="this.parentElement.remove()">
                &times;
            </button>
        `;
        
        errorContainer.appendChild(errorElement);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorElement.parentNode) {
                errorElement.remove();
            }
        }, 5000);
    },
    
    // Handle authentication errors
    handleAuthError() {
        // Redirect to login page
        setTimeout(() => {
            window.location.href = '/login/';
        }, 2000);
    },
    
    // Handle rate limit errors
    handleRateLimitError() {
        // Disable submit buttons temporarily
        const submitButtons = document.querySelectorAll('[type="submit"]');
        submitButtons.forEach(button => {
            button.disabled = true;
            setTimeout(() => {
                button.disabled = false;
            }, 60000); // 1 minute
        });
    },
    
    // Handle validation errors
    handleValidationError(error) {
        if (error.details && typeof error.details === 'object') {
            Object.entries(error.details).forEach(([field, messages]) => {
                this.showFieldError(field, messages);
            });
        }
    },
    
    // Show field-specific error
    showFieldError(fieldName, messages) {
        const field = document.getElementById(fieldName);
        if (!field) return;
        
        field.classList.add('is-invalid');
        
        const errorElement = document.getElementById(`${fieldName}-error`);
        if (errorElement) {
            errorElement.textContent = Array.isArray(messages) ? messages.join(', ') : messages;
        }
    },
    
    // Escape HTML for safe display
    escapeHTML(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
};
```

## Security Testing

### Security Test Suite
```javascript
// Security Testing Utilities
const SecurityTests = {
    // Test XSS prevention
    testXSSPrevention() {
        const xssPayloads = [
            '<script>alert("XSS")</script>',
            'javascript:alert("XSS")',
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
            '"><script>alert("XSS")</script>'
        ];
        
        xssPayloads.forEach(payload => {
            const result = HTMLSanitizer.sanitize(payload);
            console.assert(
                !result.includes('<script>') && !result.includes('javascript:'),
                `XSS payload not properly sanitized: ${payload}`
            );
        });
    },
    
    // Test input validation
    testInputValidation() {
        const testCases = [
            { input: '', expected: false, message: 'Empty input should be invalid' },
            { input: 'a'.repeat(1000), expected: false, message: 'Long input should be invalid' },
            { input: '<script>alert("test")</script>', expected: false, message: 'Script tags should be invalid' },
            { input: 'Valid input', expected: true, message: 'Valid input should pass' }
        ];
        
        testCases.forEach(({ input, expected, message }) => {
            const result = InputValidator.validateText(input, { required: true, maxLength: 100 });
            console.assert(result.isValid === expected, message);
        });
    },
    
    // Test file upload security
    testFileUploadSecurity() {
        const maliciousFiles = [
            { name: 'test.exe', type: 'application/exe' },
            { name: 'script.js', type: 'text/javascript' },
            { name: 'test.php', type: 'application/php' },
            { name: 'normal.txt', type: 'text/plain' }
        ];
        
        maliciousFiles.forEach(file => {
            const mockFile = new File(['test'], file.name, { type: file.type });
            const result = SecureFileUpload.validateFile(mockFile);
            
            const shouldBeValid = file.name === 'normal.txt';
            console.assert(
                result.isValid === shouldBeValid,
                `File ${file.name} validation failed`
            );
        });
    },
    
    // Run all security tests
    runAllTests() {
        console.log('Running security tests...');
        
        this.testXSSPrevention();
        this.testInputValidation();
        this.testFileUploadSecurity();
        
        console.log('Security tests completed.');
    }
};
```

## Security Monitoring

### Security Event Logging
```javascript
// Security Event Logger
const SecurityLogger = {
    // Log security events
    logEvent(eventType, details = {}) {
        const event = {
            type: eventType,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            url: window.location.href,
            details: this.sanitizeDetails(details)
        };
        
        // Send to security monitoring service
        this.sendToSecurityService(event);
        
        // Log to console for development
        console.log('Security event:', event);
    },
    
    // Sanitize details for logging
    sanitizeDetails(details) {
        const sanitized = { ...details };
        
        // Remove sensitive information
        const sensitiveKeys = ['password', 'token', 'key', 'secret', 'creditCard'];
        sensitiveKeys.forEach(key => {
            if (sanitized[key]) {
                sanitized[key] = '[REDACTED]';
            }
        });
        
        return sanitized;
    },
    
    // Send to security monitoring service
    sendToSecurityService(event) {
        // Implement based on your monitoring solution
        // fetch('/api/security-events', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify(event)
        // });
    },
    
    // Log suspicious activity
    logSuspiciousActivity(description, details = {}) {
        this.logEvent('suspicious_activity', {
            description,
            ...details
        });
    },
    
    // Log failed authentication
    logFailedAuth(username, details = {}) {
        this.logEvent('failed_authentication', {
            username,
            ...details
        });
    },
    
    // Log XSS attempt
    logXSSAttempt(payload, field) {
        this.logEvent('xss_attempt', {
            payload: payload.substring(0, 100), // Limit length
            field
        });
    }
};
```

This comprehensive security guide ensures that all agent implementations follow security best practices and prevent common vulnerabilities.