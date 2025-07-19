# Template Architecture Patterns

Technical reference for implementing optimized Django templates with modern frontend patterns.

## Overview

This document provides detailed technical specifications for the template architecture used in optimized agents. The patterns ensure consistent UI/UX, maintainable code, and optimal performance.

## Core Architecture Principles

### 1. Widget-Based Component System
- **Modular Design**: Each UI component is self-contained
- **Reusable Patterns**: Components can be easily replicated across agents
- **Consistent Styling**: All components follow the same design system
- **Responsive Layout**: Components adapt to different screen sizes

### 2. Self-Contained Styles
- **No External Dependencies**: All styles are embedded in the template
- **CSS Custom Properties**: Centralized design tokens for consistency
- **Optimized Performance**: Reduced HTTP requests and faster loading
- **Maintainable Code**: Easy to update and modify styles

### 3. Security-First JavaScript
- **HTML Sanitization**: All dynamic content is sanitized
- **XSS Prevention**: Input validation and output encoding
- **Safe DOM Manipulation**: Controlled content insertion
- **Event Management**: Proper listener cleanup and memory management

## Template Structure

### Base Template Integration
```html
{% extends 'base.html' %}
{% load static %}

{% block title %}Agent Name - NetCop AI Hub{% endblock %}

{% block extra_css %}
<style>
/* Agent-specific optimized styles */
</style>
{% endblock %}

{% block content %}
<!-- Agent content -->
{% endblock %}

{% block extra_js %}
<script>
/* Agent-specific JavaScript */
</script>
{% endblock %}
```

### Layout Grid System
```html
<div class="agent-container">
    <div class="agent-grid">
        <!-- Main Content Area -->
        <div class="agent-main">
            <div class="agent-header">
                <h1>{{ agent.name }}</h1>
                <p>{{ agent.description }}</p>
            </div>
            
            <div class="agent-form">
                <!-- Form components -->
            </div>
            
            <div class="agent-output">
                <!-- Output display -->
            </div>
        </div>
        
        <!-- Sidebar Widgets -->
        <div class="agent-sidebar">
            <!-- Widget components -->
        </div>
    </div>
</div>
```

## CSS Architecture

### Design System Variables
```css
:root {
    /* Color Palette */
    --primary: #000000;
    --surface: #ffffff;
    --surface-variant: #f8fafc;
    --background: #f3f4f6;
    --outline: #e4e7eb;
    --outline-variant: #e1e4e7;
    --on-surface: #1a1a1a;
    --on-surface-variant: #6b7280;
    --success: #10b981;
    --error: #ef4444;
    --warning: #f59e0b;
    --info: #3b82f6;
    
    /* Border Radius */
    --radius-xs: 4px;
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    --radius-2xl: 24px;
    --radius-full: 9999px;
    
    /* Spacing Scale */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    --spacing-2xl: 48px;
    --spacing-3xl: 64px;
    
    /* Typography */
    --font-size-xs: 0.75rem;
    --font-size-sm: 0.875rem;
    --font-size-base: 1rem;
    --font-size-lg: 1.125rem;
    --font-size-xl: 1.25rem;
    --font-size-2xl: 1.5rem;
    --font-size-3xl: 1.875rem;
    
    /* Font Weights */
    --font-weight-normal: 400;
    --font-weight-medium: 500;
    --font-weight-semibold: 600;
    --font-weight-bold: 700;
    
    /* Line Heights */
    --line-height-tight: 1.25;
    --line-height-normal: 1.5;
    --line-height-relaxed: 1.75;
    
    /* Shadows */
    --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 8px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 20px rgba(0, 0, 0, 0.15);
    --shadow-xl: 0 20px 40px rgba(0, 0, 0, 0.2);
    
    /* Transitions */
    --transition-fast: 0.15s ease;
    --transition-base: 0.2s ease;
    --transition-slow: 0.3s ease;
    
    /* Z-Index Scale */
    --z-dropdown: 1000;
    --z-sticky: 1020;
    --z-fixed: 1030;
    --z-modal-backdrop: 1040;
    --z-modal: 1050;
    --z-popover: 1060;
    --z-tooltip: 1070;
}
```

### Component Architecture
```css
/* Base Component Styles */
.component {
    /* Use design system variables */
    background: var(--surface);
    border: 1px solid var(--outline);
    border-radius: var(--radius-md);
    padding: var(--spacing-md);
    transition: var(--transition-base);
}

/* Widget Base Class */
.widget {
    @extend .component;
    margin-bottom: var(--spacing-md);
    box-shadow: var(--shadow-sm);
}

.widget:hover {
    box-shadow: var(--shadow-md);
}

.widget-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-md);
}

.widget-title {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--on-surface);
    margin: 0;
}

.widget-content {
    color: var(--on-surface-variant);
    line-height: var(--line-height-normal);
}
```

### Grid System
```css
/* Responsive Grid Layout */
.agent-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--spacing-lg);
}

.agent-grid {
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: var(--spacing-xl);
    align-items: start;
}

/* Responsive Breakpoints */
@media (max-width: 768px) {
    .agent-grid {
        grid-template-columns: 1fr;
        gap: var(--spacing-lg);
    }
    
    .agent-sidebar {
        order: -1; /* Move sidebar to top on mobile */
    }
}

@media (max-width: 480px) {
    .agent-container {
        padding: var(--spacing-md);
    }
    
    .agent-grid {
        gap: var(--spacing-md);
    }
}
```

### Form Component Patterns
```css
/* Form Base Styles */
.form-group {
    margin-bottom: var(--spacing-lg);
}

.form-label {
    display: block;
    font-weight: var(--font-weight-medium);
    color: var(--on-surface);
    margin-bottom: var(--spacing-sm);
}

.form-control {
    width: 100%;
    padding: var(--spacing-md);
    border: 1px solid var(--outline);
    border-radius: var(--radius-sm);
    font-size: var(--font-size-base);
    background: var(--surface);
    color: var(--on-surface);
    transition: var(--transition-base);
}

.form-control:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1);
}

.form-control.is-invalid {
    border-color: var(--error);
}

.form-control.is-valid {
    border-color: var(--success);
}

/* Form Validation Styles */
.form-error {
    color: var(--error);
    font-size: var(--font-size-sm);
    margin-top: var(--spacing-xs);
}

.form-help {
    color: var(--on-surface-variant);
    font-size: var(--font-size-sm);
    margin-top: var(--spacing-xs);
}

/* Required Field Indicator */
.required::after {
    content: " *";
    color: var(--error);
}
```

### Button Component System
```css
/* Button Base */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-sm) var(--spacing-md);
    border: 1px solid transparent;
    border-radius: var(--radius-sm);
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-medium);
    line-height: var(--line-height-tight);
    text-decoration: none;
    cursor: pointer;
    transition: var(--transition-base);
    user-select: none;
    white-space: nowrap;
}

.btn:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1);
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Button Variants */
.btn-primary {
    background: var(--primary);
    color: var(--surface);
}

.btn-primary:hover:not(:disabled) {
    background: color-mix(in srgb, var(--primary) 90%, black);
}

.btn-secondary {
    background: var(--surface-variant);
    color: var(--on-surface);
}

.btn-secondary:hover:not(:disabled) {
    background: color-mix(in srgb, var(--surface-variant) 90%, black);
}

.btn-outline {
    background: transparent;
    color: var(--primary);
    border-color: var(--primary);
}

.btn-outline:hover:not(:disabled) {
    background: var(--primary);
    color: var(--surface);
}

/* Button Sizes */
.btn-sm {
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: var(--font-size-sm);
}

.btn-lg {
    padding: var(--spacing-md) var(--spacing-lg);
    font-size: var(--font-size-lg);
}

/* Button States */
.btn-loading {
    position: relative;
    color: transparent;
}

.btn-loading::after {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    width: 16px;
    height: 16px;
    margin: -8px 0 0 -8px;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
```

## JavaScript Architecture

### Module Pattern
```javascript
// Agent Module Pattern
const AgentModule = (function() {
    'use strict';
    
    // Private variables
    let isInitialized = false;
    let eventListeners = [];
    let config = {};
    
    // Private methods
    function init() {
        if (isInitialized) return;
        
        setupEventListeners();
        setupFormValidation();
        setupWalletIntegration();
        setupAccessibility();
        
        isInitialized = true;
    }
    
    function setupEventListeners() {
        // Event listener setup with cleanup tracking
    }
    
    function setupFormValidation() {
        // Form validation setup
    }
    
    function setupWalletIntegration() {
        // Wallet integration setup
    }
    
    function setupAccessibility() {
        // Accessibility enhancements
    }
    
    // Public API
    return {
        init: init,
        destroy: function() {
            // Cleanup method
            eventListeners.forEach(({element, event, handler}) => {
                if (element) {
                    element.removeEventListener(event, handler);
                }
            });
            eventListeners = [];
            isInitialized = false;
        },
        
        // Public methods
        submitForm: function(formData) {
            // Form submission logic
        },
        
        updateWalletBalance: function(newBalance) {
            // Wallet balance update logic
        },
        
        showError: function(message) {
            // Error display logic
        },
        
        showSuccess: function(message) {
            // Success display logic
        }
    };
})();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    AgentModule.init();
});
```

### State Management Pattern
```javascript
// Simple State Management
const AgentState = {
    // Initial state
    data: {
        isLoading: false,
        walletBalance: 0,
        formData: {},
        results: null,
        errors: []
    },
    
    // State update method
    setState(newState) {
        this.data = { ...this.data, ...newState };
        this.render();
    },
    
    // Get current state
    getState() {
        return { ...this.data };
    },
    
    // Render method
    render() {
        // Update UI based on state
        this.updateLoadingState();
        this.updateWalletDisplay();
        this.updateFormState();
        this.updateResultsDisplay();
        this.updateErrorDisplay();
    },
    
    updateLoadingState() {
        const submitBtn = document.getElementById('submitBtn');
        const loadingState = document.getElementById('loadingState');
        
        if (this.data.isLoading) {
            submitBtn.classList.add('btn-loading');
            submitBtn.disabled = true;
            loadingState.style.display = 'block';
        } else {
            submitBtn.classList.remove('btn-loading');
            submitBtn.disabled = false;
            loadingState.style.display = 'none';
        }
    },
    
    updateWalletDisplay() {
        const walletElement = document.getElementById('walletBalance');
        if (walletElement) {
            walletElement.textContent = this.data.walletBalance.toFixed(2);
        }
    },
    
    updateFormState() {
        // Update form based on state
    },
    
    updateResultsDisplay() {
        const resultsContainer = document.getElementById('results');
        if (this.data.results && resultsContainer) {
            // Display results safely
            safeSetHTML(resultsContainer, this.data.results);
        }
    },
    
    updateErrorDisplay() {
        const errorContainer = document.getElementById('errorContainer');
        if (errorContainer) {
            errorContainer.innerHTML = '';
            this.data.errors.forEach(error => {
                const errorElement = document.createElement('div');
                errorElement.className = 'alert alert-error';
                errorElement.textContent = error;
                errorContainer.appendChild(errorElement);
            });
        }
    }
};
```

### Event Management Pattern
```javascript
// Event Management Utility
const EventManager = {
    listeners: new Map(),
    
    add(element, event, handler, options = {}) {
        const key = `${element.id || 'unknown'}-${event}`;
        
        // Store reference for cleanup
        if (!this.listeners.has(key)) {
            this.listeners.set(key, []);
        }
        
        this.listeners.get(key).push({
            element,
            event,
            handler,
            options
        });
        
        // Add event listener
        element.addEventListener(event, handler, options);
    },
    
    remove(element, event, handler) {
        const key = `${element.id || 'unknown'}-${event}`;
        const listeners = this.listeners.get(key);
        
        if (listeners) {
            const index = listeners.findIndex(l => 
                l.element === element && 
                l.event === event && 
                l.handler === handler
            );
            
            if (index > -1) {
                listeners.splice(index, 1);
                element.removeEventListener(event, handler);
            }
        }
    },
    
    removeAll() {
        this.listeners.forEach(listeners => {
            listeners.forEach(({element, event, handler}) => {
                element.removeEventListener(event, handler);
            });
        });
        
        this.listeners.clear();
    },
    
    delegate(parent, selector, event, handler) {
        const delegateHandler = (e) => {
            const target = e.target.closest(selector);
            if (target) {
                handler.call(target, e);
            }
        };
        
        this.add(parent, event, delegateHandler);
        return delegateHandler;
    }
};
```

## Performance Optimization Patterns

### Lazy Loading
```javascript
// Lazy Loading Implementation
const LazyLoader = {
    observers: new Map(),
    
    init() {
        if ('IntersectionObserver' in window) {
            this.createObserver();
        } else {
            // Fallback for older browsers
            this.loadAllContent();
        }
    },
    
    createObserver() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadContent(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: '50px'
        });
        
        // Observe elements with lazy loading
        document.querySelectorAll('[data-lazy]').forEach(el => {
            observer.observe(el);
        });
    },
    
    loadContent(element) {
        const src = element.dataset.lazy;
        if (src) {
            if (element.tagName === 'IMG') {
                element.src = src;
            } else {
                // Load other content types
                fetch(src)
                    .then(response => response.text())
                    .then(html => {
                        safeSetHTML(element, html);
                    });
            }
        }
    },
    
    loadAllContent() {
        document.querySelectorAll('[data-lazy]').forEach(el => {
            this.loadContent(el);
        });
    }
};
```

### Resource Optimization
```javascript
// Resource Management
const ResourceManager = {
    cache: new Map(),
    
    // Cache frequently used data
    cache(key, data, ttl = 300000) { // 5 minutes default
        this.cache.set(key, {
            data,
            timestamp: Date.now(),
            ttl
        });
    },
    
    // Get cached data
    get(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < cached.ttl) {
            return cached.data;
        }
        
        // Remove expired cache
        this.cache.delete(key);
        return null;
    },
    
    // Clear expired cache
    cleanup() {
        const now = Date.now();
        for (const [key, cached] of this.cache) {
            if (now - cached.timestamp >= cached.ttl) {
                this.cache.delete(key);
            }
        }
    },
    
    // Preload resources
    preload(urls) {
        urls.forEach(url => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = url;
            link.as = 'fetch';
            document.head.appendChild(link);
        });
    }
};
```

## Integration Patterns

### Django Template Integration
```html
<!-- Dynamic Content with Security -->
<div class="widget" data-widget="wallet">
    <h3>💰 Your Wallet</h3>
    <div class="wallet-balance">
        <span class="balance-amount" id="walletBalance">{{ user.wallet_balance|floatformat:2 }}</span>
        <span class="balance-currency">AED</span>
    </div>
    <a href="{% url 'wallet_topup' %}" class="btn btn-primary btn-sm">
        Top Up Wallet
    </a>
</div>

<!-- Form with CSRF and Validation -->
<form id="agentForm" method="post" enctype="multipart/form-data" class="agent-form">
    {% csrf_token %}
    
    <!-- Dynamic form fields -->
    {% for field in form %}
        <div class="form-group">
            <label for="{{ field.id_for_label }}" class="form-label">
                {{ field.label }}
                {% if field.field.required %}
                    <span class="required" aria-label="required">*</span>
                {% endif %}
            </label>
            
            {{ field }}
            
            {% if field.help_text %}
                <div class="form-help">{{ field.help_text }}</div>
            {% endif %}
            
            {% if field.errors %}
                <div class="form-error">
                    {% for error in field.errors %}
                        {{ error }}
                    {% endfor %}
                </div>
            {% endif %}
        </div>
    {% endfor %}
    
    <button type="submit" class="btn btn-primary" id="submitBtn">
        Generate Content
    </button>
</form>
```

### API Integration Pattern
```javascript
// API Communication
const ApiClient = {
    baseURL: '/api/v1',
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
                ...options.headers
            },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    },
    
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },
    
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async uploadFile(endpoint, formData) {
        return this.request(endpoint, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCSRFToken()
                // Don't set Content-Type for FormData
            },
            body: formData
        });
    }
};
```

## Testing Integration

### Component Testing
```javascript
// Component Test Utilities
const TestUtils = {
    // Create test element
    createElement(tag, attributes = {}, content = '') {
        const element = document.createElement(tag);
        
        Object.entries(attributes).forEach(([key, value]) => {
            element.setAttribute(key, value);
        });
        
        if (content) {
            element.textContent = content;
        }
        
        return element;
    },
    
    // Simulate user interaction
    fireEvent(element, eventType, options = {}) {
        const event = new Event(eventType, {
            bubbles: true,
            cancelable: true,
            ...options
        });
        
        element.dispatchEvent(event);
    },
    
    // Wait for async operations
    waitFor(condition, timeout = 5000) {
        return new Promise((resolve, reject) => {
            const startTime = Date.now();
            
            const check = () => {
                if (condition()) {
                    resolve();
                } else if (Date.now() - startTime > timeout) {
                    reject(new Error('Timeout waiting for condition'));
                } else {
                    setTimeout(check, 100);
                }
            };
            
            check();
        });
    },
    
    // Clean up test DOM
    cleanup() {
        document.querySelectorAll('[data-testid]').forEach(el => {
            el.remove();
        });
    }
};
```

This architecture ensures consistent, maintainable, and performant templates across all agents while providing the flexibility to customize specific features as needed.