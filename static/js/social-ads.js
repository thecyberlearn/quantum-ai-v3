/**
 * Social Ads Generator - Agent-Specific JavaScript
 * Handles unique functionality for Social Ads Generator agent
 */

class SocialAdsProcessor extends WorkflowsCore {
    constructor() {
        super();
        this.agentSlug = 'social-ads-generator';
        this.webhookUrl = 'http://localhost:5678/webhook/2dc234d8-7217-454a-83e9-81afe5b4fe2d';
        this.price = 5.0; // Will be overridden by template data
        this.sessionId = this.constructor.generateSessionId();
        
        // Initialize on page load
        this.initialize();
    }
    
    initialize() {
        // Set data attributes from page
        const priceElement = document.body.getAttribute('data-agent-price');
        if (priceElement) {
            this.price = parseFloat(priceElement);
        }
        
        // Initialize form submission
        const form = document.getElementById('agentForm');
        if (form) {
            form.addEventListener('submit', this.handleFormSubmission.bind(this));
        }
        
        // Initialize form validation
        this.initializeFormValidation();
        
        // Set initial radio selection if any exist
        const firstRadio = document.querySelector('.radio-card');
        if (firstRadio && !document.querySelector('.radio-card.selected')) {
            firstRadio.classList.add('selected');
            const input = firstRadio.querySelector('input[type="radio"]');
            if (input) input.checked = true;
        }
    }
    
    /**
     * Handle form submission with hybrid N8N/Django approach
     */
    async handleFormSubmission(e) {
        e.preventDefault();
        
        if (!this.isFormValid()) {
            this.constructor.showToast('Please fill in all required fields correctly', 'error');
            return;
        }
        
        // Check authentication and balance
        if (!this.constructor.checkAuthentication()) return;
        if (!this.constructor.checkBalance(this.price)) return;
        
        // Show processing status and disable submit button
        this.constructor.showProcessing('Generating your social ads...');
        
        const submitBtn = document.getElementById('generateBtn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = '⏳ Generating...';
        }
        
        try {
            // Try direct N8N integration for better performance (with Django fallback)
            const useDirectN8N = true; // Feature flag for direct integration
            
            if (useDirectN8N) {
                await this.processViaDirectN8N(e.target);
            } else {
                await this.processViaDjango(e.target);
            }
        } catch (error) {
            console.error('Form submission error:', error);
            this.constructor.hideProcessing();
            this.constructor.showToast('❌ Connection error. Please try again.', 'error');
            this.resetSubmitButton();
        }
    }
    
    /**
     * Direct N8N processing for better performance
     */
    async processViaDirectN8N(form) {
        try {
            const formData = new FormData(form);
            
            // Extract form data
            const description = formData.get('description').trim();
            const platform = formData.get('social_platform');
            const emoji = formData.get('include_emoji');
            const language = formData.get('language');
            
            // Create message for N8N
            const messageText = `Create compelling social media ads for: ${description}. Target platform: ${platform}. Include emojis: ${emoji}. Language: ${language}. Make it engaging and professional.`;
            
            const webhookData = {
                sessionId: this.sessionId,
                message: { text: messageText }
            };
            
            // Direct N8N webhook call
            const response = await fetch(this.webhookUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(webhookData),
                signal: AbortSignal.timeout(60000) // 60 second timeout
            });
            
            if (!response.ok) {
                throw new Error(`N8N error: ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            let data;
            if (contentType && contentType.includes('application/json')) {
                data = await response.json().catch(() => response.text());
            } else {
                data = await response.text();
            }
            
            // Process successful N8N response
            this.constructor.hideProcessing();
            
            // Deduct wallet balance via Django API
            await this.constructor.deductBalance(
                this.price, 
                `Social Ads Generator - ${description.substring(0, 50)}...`,
                this.agentSlug
            );
            
            // Display results using the enhanced display function
            this.displayDirectN8NResults(data, platform, language);
            
            this.constructor.showToast('✅ Social ads generated successfully!', 'success');
            
        } catch (error) {
            console.error('Direct N8N error:', error);
            this.constructor.showToast('❌ Direct processing failed, trying Django backend...', 'info');
            
            // Fallback to Django processing
            await this.processViaDjango(form);
        }
    }
    
    /**
     * Django processing fallback
     */
    async processViaDjango(form) {
        const formData = new FormData(form);
        
        const response = await fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        
        const result = await response.json();
        
        if (result.success && result.request_id) {
            // Start polling for results
            this.checkResults(result.request_id);
            if (result.wallet_balance !== undefined) {
                this.constructor.updateWalletBalance(result.wallet_balance);
            }
        } else {
            this.constructor.hideProcessing();
            this.constructor.showToast(`❌ ${result.error || 'Processing failed'}`, 'error');
            this.resetSubmitButton();
        }
    }
    
    /**
     * Display results from direct N8N call
     */
    displayDirectN8NResults(data, platform, language) {
        const resultsContainer = document.getElementById('resultsContainer');
        const resultsContent = document.getElementById('resultsContent');
        
        if (!resultsContainer || !resultsContent) return;
        
        let content = '';
        
        // Handle different N8N response formats
        if (typeof data === 'string') {
            content = data;
        } else if (data && typeof data === 'object') {
            content = data.output || data.text || data.content || data.ad_copy || data.result || data.message || JSON.stringify(data, null, 2);
        } else {
            content = 'Social ads generated successfully!';
        }
        
        // Clear and populate results securely
        resultsContent.textContent = '';
        this.renderSecureContent(resultsContent, content);
        
        // Show results container
        resultsContainer.style.display = 'block';
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        this.resetSubmitButton();
    }
    
    /**
     * Secure content rendering without innerHTML to prevent XSS
     */
    renderSecureContent(container, content) {
        // Sanitize and validate content
        if (!content || typeof content !== 'string') {
            container.textContent = 'No content available';
            return;
        }
        
        // Create wrapper paragraph
        const wrapper = document.createElement('div');
        wrapper.className = 'results-content';
        
        // Split content into lines and process safely
        const lines = content.split('\n');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            if (!line) {
                // Add line break for empty lines
                if (i > 0) wrapper.appendChild(document.createElement('br'));
                continue;
            }
            
            let element;
            
            // Handle headers (but escape content)
            if (line.startsWith('### ')) {
                element = document.createElement('h3');
                element.textContent = line.substring(4);
            } else if (line.startsWith('## ')) {
                element = document.createElement('h2');
                element.textContent = line.substring(3);
            } else if (line.startsWith('# ')) {
                element = document.createElement('h1');
                element.textContent = line.substring(2);
            } else {
                // Handle regular text with basic formatting
                element = document.createElement('span');
                this.formatTextSecurely(element, line);
            }
            
            wrapper.appendChild(element);
            
            // Add line break if not the last line
            if (i < lines.length - 1) {
                wrapper.appendChild(document.createElement('br'));
            }
        }
        
        container.appendChild(wrapper);
    }
    
    /**
     * Format text with basic styling while preventing XSS
     */
    formatTextSecurely(element, text) {
        // Simple approach: handle bold and italic formatting securely
        const parts = [];
        let currentText = text;
        
        // Process **bold** text
        currentText = currentText.replace(/\*\*(.*?)\*\*/g, (match, content) => {
            const placeholder = `__BOLD_${parts.length}__`;
            parts.push({type: 'bold', content: content});
            return placeholder;
        });
        
        // Process *italic* text
        currentText = currentText.replace(/\*(.*?)\*/g, (match, content) => {
            const placeholder = `__ITALIC_${parts.length}__`;
            parts.push({type: 'italic', content: content});
            return placeholder;
        });
        
        // Split by placeholders and create DOM elements
        const segments = currentText.split(/(__(?:BOLD|ITALIC)_\d+__)/);
        
        segments.forEach(segment => {
            if (segment.startsWith('__BOLD_')) {
                const index = parseInt(segment.match(/\d+/)[0]);
                const strong = document.createElement('strong');
                strong.textContent = parts[index].content;
                element.appendChild(strong);
            } else if (segment.startsWith('__ITALIC_')) {
                const index = parseInt(segment.match(/\d+/)[0]);
                const em = document.createElement('em');
                em.textContent = parts[index].content;
                element.appendChild(em);
            } else if (segment) {
                element.appendChild(document.createTextNode(segment));
            }
        });
    }
    
    /**
     * Form validation specific to Social Ads Generator
     */
    initializeFormValidation() {
        const fields = ['description', 'social_platform', 'include_emoji'];
        
        fields.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            if (field) {
                field.addEventListener('blur', () => this.validateField(fieldName));
                field.addEventListener('input', () => this.constructor.clearFieldError(fieldName));
            }
        });
    }
    
    validateField(fieldName) {
        const field = document.getElementById(fieldName);
        const value = field.value.trim();
        
        switch (fieldName) {
            case 'description':
                if (!value) {
                    this.constructor.showFieldError(fieldName, 'Please provide a description of your product or service');
                    return false;
                } else if (value.length < 10) {
                    this.constructor.showFieldError(fieldName, 'Description must be at least 10 characters long');
                    return false;
                }
                break;
            case 'social_platform':
                if (!value) {
                    this.constructor.showFieldError(fieldName, 'Please select a social media platform');
                    return false;
                }
                break;
            case 'include_emoji':
                if (!value) {
                    this.constructor.showFieldError(fieldName, 'Please select whether to include emojis');
                    return false;
                }
                break;
        }
        
        this.constructor.clearFieldError(fieldName);
        return true;
    }
    
    isFormValid() {
        const fields = ['description', 'social_platform', 'include_emoji'];
        let isValid = true;
        
        fields.forEach(fieldName => {
            if (!this.validateField(fieldName)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    /**
     * Check results (polling for Django completion)
     */
    checkResults(requestId) {
        let pollCount = 0;
        const maxPolls = 30; // 5 minutes max
        
        const pollInterval = setInterval(() => {
            pollCount++;
            
            fetch(`/workflows/api/status/${requestId}/`)
                .then(response => response.json())
                .then(result => {
                    if (result.status === 'completed') {
                        clearInterval(pollInterval);
                        this.displayDjangoResults(result);
                    } else if (result.status === 'failed') {
                        clearInterval(pollInterval);
                        this.constructor.hideProcessing();
                        this.constructor.showToast('❌ Social ads generation failed. Please try again.', 'error');
                        this.resetSubmitButton();
                    } else if (pollCount >= maxPolls) {
                        clearInterval(pollInterval);
                        this.constructor.hideProcessing();
                        this.constructor.showToast('⏰ Processing is taking longer than expected. Please check back later.', 'error');
                        this.resetSubmitButton();
                    }
                    // Continue polling if still processing
                })
                .catch(error => {
                    console.error('Status check error:', error);
                    if (pollCount >= maxPolls) {
                        clearInterval(pollInterval);
                        this.constructor.hideProcessing();
                        this.constructor.showToast('❌ Connection error during processing.', 'error');
                        this.resetSubmitButton();
                    }
                });
        }, 10000); // Check every 10 seconds
    }
    
    /**
     * Display results from Django processing
     */
    displayDjangoResults(result) {
        const resultsContainer = document.getElementById('resultsContainer');
        const resultsContent = document.getElementById('resultsContent');
        
        if (result.success || result.output) {
            this.constructor.hideProcessing();
            
            const adContent = result.output || result.ad_copy_content || result.content || 'Social ads generated successfully!';
            if (resultsContent) {
                resultsContent.textContent = '';
                this.renderSecureContent(resultsContent, adContent);
            }
            
            if (resultsContainer) {
                resultsContainer.style.display = 'block';
                resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
            
            this.constructor.showToast('✅ Social ads completed successfully!', 'success');
        } else if (result.error) {
            this.constructor.hideProcessing();
            this.constructor.showToast(`❌ Error: ${result.error}`, 'error');
        } else {
            this.constructor.hideProcessing();
            this.constructor.showToast('❌ Failed to generate social ads. Please try again.', 'error');
        }
        
        this.resetSubmitButton();
    }
    
    /**
     * Reset submit button to original state
     */
    resetSubmitButton() {
        const submitBtn = document.getElementById('generateBtn');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = `📢 Generate Social Ads (${this.price} AED)`;
        }
    }
}

// Result action functions (global for button onclick handlers)
function copyResults() {
    const content = document.getElementById('resultsContent');
    if (content) {
        const text = content.textContent || '';
        WorkflowsCore.copyToClipboard(text, 'Social ads copied to clipboard!');
    }
}

function downloadResults() {
    const content = document.getElementById('resultsContent');
    if (content) {
        const text = content.textContent || '';
        WorkflowsCore.downloadAsFile(text, 'social-ads-results.txt', 'Social ads downloaded!');
    }
}

function resetForm() {
    const form = document.getElementById('agentForm');
    if (form) {
        form.reset();
    }
    
    const resultsContainer = document.getElementById('resultsContainer');
    const processingStatus = document.getElementById('processingStatus');
    
    if (resultsContainer) resultsContainer.style.display = 'none';
    if (processingStatus) processingStatus.style.display = 'none';
    
    // Clear validation errors
    const fields = ['description', 'social_platform', 'include_emoji'];
    fields.forEach(fieldName => WorkflowsCore.clearFieldError(fieldName));
    
    // Scroll back to form
    const formSection = document.getElementById('agentForm');
    if (formSection) {
        formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Initialize Social Ads Processor when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize processor (data attributes set by template)
    window.socialAdsProcessor = new SocialAdsProcessor();
});