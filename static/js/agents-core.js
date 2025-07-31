/**
 * Agents Core - Dynamic Agent Execution System
 * Handles form submission and N8N integration for any agent
 */

class AgentsCore extends WorkflowsCore {
    constructor() {
        super();
        this.agentId = document.body.getAttribute('data-agent-id');
        this.agentSlug = document.body.getAttribute('data-agent-slug');
        this.webhookUrl = document.body.getAttribute('data-webhook-url');
        this.price = parseFloat(document.body.getAttribute('data-agent-price') || '0');
        this.sessionId = this.constructor.generateSessionId();
        
        // Initialize on page load
        this.initialize();
    }
    
    initialize() {
        // Initialize form submission
        const form = document.getElementById('agentForm');
        if (form) {
            form.addEventListener('submit', this.handleFormSubmission.bind(this));
        }
        
        // Initialize form validation
        this.initializeDynamicFormValidation();
    }
    
    /**
     * Handle form submission with agents API integration
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
        this.constructor.showProcessing('Executing agent...');
        
        const submitBtn = document.getElementById('generateBtn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = '⏳ Processing...';
        }
        
        try {
            // Use agents API for execution
            await this.executeViaAgentsAPI(e.target);
        } catch (error) {
            console.error('Form submission error:', error);
            this.constructor.hideProcessing();
            this.constructor.showToast('❌ Connection error. Please try again.', 'error');
            this.resetSubmitButton();
        }
    }
    
    /**
     * Execute agent via the agents API
     */
    async executeViaAgentsAPI(form) {
        try {
            const formData = new FormData(form);
            
            // Extract all form data dynamically
            const inputData = {};
            for (let [key, value] of formData.entries()) {
                if (key !== 'csrfmiddlewaretoken') {
                    inputData[key] = value;
                }
            }
            
            // Get CSRF token
            const csrfToken = formData.get('csrfmiddlewaretoken');
            
            // Call agents API
            const response = await fetch('/agents/api/execute/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    agent_slug: this.agentSlug,
                    input_data: inputData
                }),
                signal: AbortSignal.timeout(90000) // 90 second timeout
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                throw new Error(errorData.error || `API error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Process successful execution
            this.constructor.hideProcessing();
            
            // Update wallet balance if fee was charged
            if (data.fee_charged) {
                const currentBalance = parseFloat(document.body.getAttribute('data-user-balance') || '0');
                const newBalance = currentBalance - parseFloat(data.fee_charged);
                
                // Update the wallet balance display
                this.constructor.updateWalletBalance(newBalance);
                
                // Update the data attribute for future calculations
                document.body.setAttribute('data-user-balance', newBalance.toString());
            }
            
            // Display results
            this.displayExecutionResults(data);
            
            this.constructor.showToast('✅ Agent executed successfully!', 'success');
            
        } catch (error) {
            console.error('Agent execution error:', error);
            this.constructor.hideProcessing();
            this.constructor.showToast(`❌ ${error.message}`, 'error');
            this.resetSubmitButton();
        }
    }
    
    /**
     * Display results from agent execution
     */
    displayExecutionResults(executionData) {
        const resultsContainer = document.getElementById('resultsContainer');
        const resultsContent = document.getElementById('resultsContent');
        
        if (!resultsContainer || !resultsContent) return;
        
        let content = '';
        
        // Handle different response formats
        if (executionData.output_data && typeof executionData.output_data === 'object') {
            // Handle N8N response formats
            const output = executionData.output_data;
            content = output.output || output.text || output.content || output.result || output.message || JSON.stringify(output, null, 2);
        } else if (executionData.output_data && typeof executionData.output_data === 'string') {
            content = executionData.output_data;
        } else {
            content = `Agent executed successfully!\n\nExecution ID: ${executionData.id}\nStatus: ${executionData.status}\nFee Charged: ${executionData.fee_charged} AED`;
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
        
        // Create wrapper div
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
     * Initialize dynamic form validation based on form schema
     */
    initializeDynamicFormValidation() {
        const fields = document.querySelectorAll('#agentForm [name]');
        
        fields.forEach(field => {
            const fieldName = field.getAttribute('name');
            if (fieldName && fieldName !== 'csrfmiddlewaretoken') {
                field.addEventListener('blur', () => this.validateField(fieldName));
                field.addEventListener('input', () => this.constructor.clearFieldError(fieldName));
            }
        });
    }
    
    validateField(fieldName) {
        const field = document.getElementById(fieldName);
        if (!field) return true;
        
        const value = field.type === 'checkbox' ? field.checked : field.value.trim();
        const required = field.hasAttribute('required');
        
        // Basic required field validation
        if (required && (!value || value === '')) {
            this.constructor.showFieldError(fieldName, `${fieldName.replace('_', ' ')} is required`);
            return false;
        }
        
        // Specific validation based on field type
        if (field.type === 'textarea' && value && value.length < 10) {
            this.constructor.showFieldError(fieldName, 'Please provide more detailed information (at least 10 characters)');
            return false;
        }
        
        if (field.type === 'url' && value && !this.isValidURL(value)) {
            this.constructor.showFieldError(fieldName, 'Please enter a valid URL');
            return false;
        }
        
        this.constructor.clearFieldError(fieldName);
        return true;
    }
    
    isValidURL(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }
    
    isFormValid() {
        const fields = document.querySelectorAll('#agentForm [name]');
        let isValid = true;
        
        fields.forEach(field => {
            const fieldName = field.getAttribute('name');
            if (fieldName && fieldName !== 'csrfmiddlewaretoken') {
                if (!this.validateField(fieldName)) {
                    isValid = false;
                }
            }
        });
        
        return isValid;
    }
    
    /**
     * Reset submit button to original state
     */
    resetSubmitButton() {
        const submitBtn = document.getElementById('generateBtn');
        if (submitBtn) {
            submitBtn.disabled = false;
            const agentSlug = document.body.getAttribute('data-agent-slug') || 'agent';
            const agentName = agentSlug.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
            submitBtn.textContent = `🚀 Execute ${agentName} (${this.price} AED)`;
        }
    }
}

// Result action functions (global for button onclick handlers)
function copyResults() {
    const content = document.getElementById('resultsContent');
    if (content) {
        const text = content.textContent || '';
        WorkflowsCore.copyToClipboard(text, 'Results copied to clipboard!');
    }
}

function downloadResults() {
    const content = document.getElementById('resultsContent');
    if (content) {
        const text = content.textContent || '';
        const agentSlug = document.body.getAttribute('data-agent-slug') || 'agent';
        WorkflowsCore.downloadAsFile(text, `${agentSlug}-results.txt`, 'Results downloaded!');
    }
}

function resetForm() {
    const form = document.getElementById('agentForm');
    if (form) {
        // Reset form but preserve CSRF token
        const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]').value;
        form.reset();
        form.querySelector('[name="csrfmiddlewaretoken"]').value = csrfToken;
    }
    
    const resultsContainer = document.getElementById('resultsContainer');
    const processingStatus = document.getElementById('processingStatus');
    
    if (resultsContainer) resultsContainer.style.display = 'none';
    if (processingStatus) processingStatus.style.display = 'none';
    
    // Clear validation errors
    const fields = document.querySelectorAll('#agentForm [name]');
    fields.forEach(field => {
        const fieldName = field.getAttribute('name');
        if (fieldName && fieldName !== 'csrfmiddlewaretoken') {
            WorkflowsCore.clearFieldError(fieldName);
        }
    });
    
    // Scroll back to form
    const formSection = document.getElementById('agentForm');
    if (formSection) {
        formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Initialize Agents Core when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize processor (data attributes set by template)
    window.agentsCore = new AgentsCore();
});