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
            
            // Check if form contains file uploads
            const hasFiles = Array.from(formData.entries()).some(([key, value]) => 
                value instanceof File && key !== 'csrfmiddlewaretoken'
            );
            
            if (hasFiles) {
                // Handle file upload via multipart form data
                await this.executeWithFileUpload(formData);
            } else {
                // Handle regular form data via JSON API
                await this.executeWithJsonAPI(formData);
            }
        } catch (error) {
            console.error('Agent execution error:', error);
            this.constructor.hideProcessing();
            this.constructor.showToast(`❌ ${error.message}`, 'error');
            this.resetSubmitButton();
        }
    }
    
    /**
     * Execute agent with file upload using multipart form data
     */
    async executeWithFileUpload(formData) {
        // Get CSRF token
        const csrfToken = formData.get('csrfmiddlewaretoken');
        
        // Prepare multipart form data for direct webhook call (similar to workflows)
        const webhookFormData = new FormData();
        
        // Add files and regular form fields
        for (let [key, value] of formData.entries()) {
            if (key !== 'csrfmiddlewaretoken') {
                if (value instanceof File) {
                    webhookFormData.append('file', value);
                } else {
                    // Map form fields to webhook expected format
                    if (key === 'analysis_type') {
                        webhookFormData.append('analysisType', value);
                    } else {
                        webhookFormData.append(key, value);
                    }
                }
            }
        }
        
        // Call webhook directly for file uploads (similar to workflows approach)
        const response = await fetch(this.webhookUrl, {
            method: 'POST',
            body: webhookFormData,
            signal: AbortSignal.timeout(120000) // 2 minute timeout for file processing
        });
        
        if (!response.ok) {
            throw new Error(`File processing failed: ${response.status}`);
        }
        
        // Parse response
        const data = await response.json();
        
        // Deduct wallet balance manually since we bypassed the API
        await this.deductBalanceForFileUpload();
        
        // Process successful execution
        this.constructor.hideProcessing();
        
        // Display results
        this.displayFileProcessingResults(data);
        
        this.constructor.showToast('✅ File processed successfully!', 'success');
    }
    
    /**
     * Execute agent with JSON API (for non-file uploads)
     */
    async executeWithJsonAPI(formData) {
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
        
        // Update wallet balance ONLY after successful AI execution
        if (data.fee_charged) {
            const currentBalance = parseFloat(document.body.getAttribute('data-user-balance') || '0');
            const newBalance = currentBalance - parseFloat(data.fee_charged);
            
            console.log('Charging wallet after successful execution:', {
                currentBalance,
                feeCharged: data.fee_charged,
                newBalance,
                executionStatus: data.status
            });
            
            // Update the wallet balance display
            this.constructor.updateWalletBalance(newBalance);
            
            // Show notification about successful charge
            this.constructor.showToast(`💰 Charged ${data.fee_charged} AED - Service completed!`, 'success');
        }
        
        // Display results
        this.displayExecutionResults(data);
        
        this.constructor.showToast('✅ Agent executed successfully!', 'success');
    }
    
    /**
     * Deduct wallet balance for file upload (manual deduction)
     */
    async deductBalanceForFileUpload() {
        try {
            // Call the wallet deduction API
            const response = await fetch('/wallet/api/deduct/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    amount: this.price,
                    description: `${this.agentSlug.replace('-', ' ')} execution`,
                    agent_slug: this.agentSlug
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.new_balance !== undefined) {
                    // Update wallet balance display
                    this.constructor.updateWalletBalance(data.new_balance);
                }
            }
        } catch (error) {
            console.error('Wallet deduction error:', error);
        }
    }
    
    /**
     * Display execution results
     */
    displayExecutionResults(data) {
        const resultsContainer = document.getElementById('resultsContainer');
        const resultsContent = document.getElementById('resultsContent');
        
        if (!resultsContainer || !resultsContent) {
            console.log('Results containers not found');
            return;
        }
        
        // Clear previous results
        resultsContent.innerHTML = '';
        
        // Extract output content with better format handling and debugging
        let content = '';
        
        // Add debugging to see what we're getting
        console.log('=== DEBUGGING EXECUTION RESULTS ===');
        console.log('Full data object:', data);
        console.log('output_data type:', typeof data.output_data);
        console.log('output_data content:', data.output_data);
        console.log('Agent slug:', this.agentSlug);
        
        // Check for PDF analyzer direct response format FIRST
        if (data.sections && Array.isArray(data.sections)) {
            console.log('Using PDF direct response format');
            content = this.formatPDFAnalysisResults(data.sections);
        }
        // Check for PDF analyzer array response format
        else if (Array.isArray(data) && data[0] && data[0].sections) {
            console.log('Using PDF array response format');
            content = this.formatPDFAnalysisResults(data[0].sections);
        }
        // Then check for standard output_data format
        else if (data.output_data && typeof data.output_data === 'object') {
            // Handle PDF analyzer nested response format
            if (Array.isArray(data.output_data) && data.output_data[0] && data.output_data[0].sections) {
                console.log('Using PDF nested analysis format');
                content = this.formatPDFAnalysisResults(data.output_data[0].sections);
            }
            // Handle standard webhook response format  
            else if (data.output_data.output) {
                console.log('Using standard output format');
                // Check if this is a job posting and format it specially
                if (this.agentSlug === 'job-posting-generator') {
                    content = this.formatJobPostingResults(data.output_data.output);
                } else {
                    content = data.output_data.output;
                }
            }
            // Handle other response formats
            else if (data.output_data.result || data.output_data.content) {
                console.log('Using result/content format');
                content = data.output_data.result || data.output_data.content;
            }
            // Show the actual data structure instead of generic message
            else {
                console.log('Using JSON fallback format');
                content = `<div style="background: #f5f5f5; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap;">${JSON.stringify(data.output_data, null, 2)}</div>`;
            }
        } else if (data.output_data) {
            console.log('Using string format');
            content = data.output_data.toString();
        } else {
            console.log('No output_data found - using fallback');
            // Show the full response to debug what's missing
            content = `<div style="background: #fff3cd; padding: 15px; border: 1px solid #ffeaa7; border-radius: 5px;">
                <h4>Execution Details:</h4>
                <p><strong>Status:</strong> ${data.status || 'unknown'}</p>
                <p><strong>Agent:</strong> ${this.agentSlug}</p>
                <p><strong>Execution ID:</strong> ${data.id || 'unknown'}</p>
                <p><strong>Error:</strong> ${data.error_message || 'No error message'}</p>
                <details>
                    <summary>Full Response Data</summary>
                    <pre style="background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto;">${JSON.stringify(data, null, 2)}</pre>
                </details>
            </div>`;
        }
        console.log('Final content length:', content.length);
        console.log('=====================================');
        
        // Create content element
        const contentDiv = document.createElement('div');
        contentDiv.className = 'results-content';
        
        // Use innerHTML for formatted PDF results, textContent for others
        if (content.includes('<h') || content.includes('<div')) {
            contentDiv.innerHTML = content;
        } else {
            contentDiv.textContent = content;
        }
        
        resultsContent.appendChild(contentDiv);
        
        // Show results container
        resultsContainer.style.display = 'block';
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        this.resetSubmitButton();
    }
    
    /**
     * Format PDF analysis results - simple and clean
     */
    formatPDFAnalysisResults(sections) {
        let html = '<div class="simple-results">';
        
        sections.forEach(section => {
            let content = section.content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            content = content.replace(/\n/g, '<br>');
            
            html += `
                <div class="result-section">
                    <h3>${section.heading}</h3>
                    <div>${content}</div>
                </div>
            `;
        });
        
        html += '</div>';
        
        // Simple, clean styling
        html += `
            <style>
                .simple-results {
                    font-family: system-ui, sans-serif;
                    line-height: 1.5;
                }
                .result-section {
                    margin-bottom: 20px;
                    padding-bottom: 15px;
                    border-bottom: 1px solid #eee;
                }
                .result-section:last-child {
                    border-bottom: none;
                }
                .result-section h3 {
                    color: #333;
                    margin: 0 0 10px 0;
                    font-size: 16px;
                    font-weight: 600;
                }
                .result-section div {
                    color: #555;
                    font-size: 14px;
                }
                .result-section strong {
                    color: #222;
                }
            </style>
        `;
        
        return html;
    }
    
    /**
     * Process markdown-like content and convert to HTML
     */
    processMarkdownContent(content) {
        // Handle numbered lists (1. **Title**: Description)
        content = content.replace(/(\d+)\.\s\*\*(.*?)\*\*:\s*(.*?)(?=\n\d+\.|\n-|$)/g, 
            '<ol><li><strong>$2</strong>: $3</li></ol>');
        
        // Fix multiple consecutive ol tags
        content = content.replace(/<\/ol>\s*<ol>/g, '');
        
        // Handle bullet points (- **Title**: Description)
        content = content.replace(/(?:^|\n)-\s\*\*(.*?)\*\*:\s*(.*?)(?=\n-|$)/g, 
            '<ul><li><strong>$1</strong>: $2</li></ul>');
        
        // Fix multiple consecutive ul tags  
        content = content.replace(/<\/ul>\s*<ul>/g, '');
        
        // Handle standalone numbered items without the list wrapper
        content = content.replace(/(\d+)\.\s\*\*(.*?)\*\*:\s*(.*?)(?=\n|$)/g, 
            '<div class="numbered-item"><strong>$1. $2</strong>: $3</div>');
        
        // Handle standalone bold items
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Handle line breaks
        content = content.replace(/\n/g, '<br>');
        
        // Clean up extra breaks around lists
        content = content.replace(/<br>\s*<(ol|ul|div class="numbered-item")>/g, '<$1>');
        content = content.replace(/<\/(ol|ul)>\s*<br>/g, '</$1>');
        
        return content;
    }
    
    /**
     * Format job posting results - simple and clean
     */
    formatJobPostingResults(jobPostingText) {
        // Just convert markdown bold to HTML and preserve line breaks
        let content = jobPostingText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        content = content.replace(/\n\n/g, '<br><br>');
        content = content.replace(/\n/g, '<br>');
        
        let html = `
            <div class="simple-job-posting">
                ${content}
            </div>
            <style>
                .simple-job-posting {
                    font-family: system-ui, sans-serif;
                    line-height: 1.5;
                    color: #333;
                    font-size: 14px;
                }
                .simple-job-posting strong {
                    color: #222;
                    font-weight: 600;
                }
            </style>
        `;
        
        return html;
    }
    
    /**
     * Display file processing results
     */
    displayFileProcessingResults(data) {
        // Use same method as regular execution results
        this.displayExecutionResults(data);
    }
    
    /**
     * Dynamic form validation based on form schema
     */
    initializeDynamicFormValidation() {
        const formGroups = document.querySelectorAll('.form-group');
        
        formGroups.forEach(group => {
            const field = group.querySelector('input, select, textarea');
            if (field) {
                field.addEventListener('blur', () => this.validateField(field));
                field.addEventListener('input', () => this.constructor.clearFieldError(field.id));
            }
        });
    }
    
    /**
     * Validate individual field
     */
    validateField(field) {
        const value = field.value.trim();
        const isRequired = field.hasAttribute('required');
        
        if (isRequired && !value) {
            this.constructor.showFieldError(field.id, 'This field is required');
            return false;
        }
        
        // Type-specific validation
        if (field.type === 'email' && value && !this.isValidEmail(value)) {
            this.constructor.showFieldError(field.id, 'Please enter a valid email address');
            return false;
        }
        
        if (field.type === 'url' && value && !this.isValidUrl(value)) {
            this.constructor.showFieldError(field.id, 'Please enter a valid URL');
            return false;
        }
        
        this.constructor.clearFieldError(field.id);
        return true;
    }
    
    /**
     * Check if form is valid
     */
    isFormValid() {
        let isValid = true;
        const formGroups = document.querySelectorAll('.form-group');
        
        formGroups.forEach(group => {
            const field = group.querySelector('input, select, textarea');
            if (field && !this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    /**
     * Email validation helper
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    /**
     * URL validation helper
     */
    isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }
    
    /**
     * Reset submit button to original state
     */
    resetSubmitButton() {
        const submitBtn = document.getElementById('generateBtn');
        if (submitBtn) {
            submitBtn.disabled = false;
            const agentIcon = this.getAgentIcon();
            submitBtn.textContent = `${agentIcon} Execute ${this.getAgentName()} (${this.price} AED)`;
        }
    }
    
    /**
     * Get agent icon (fallback to generic icon)
     */
    getAgentIcon() {
        const iconMap = {
            'social-ads-generator': '📢',
            'job-posting-generator': '💼',
            'pdf-summarizer': '📄',
            'five-whys-analyzer': '❓'
        };
        
        return iconMap[this.agentSlug] || '🤖';
    }
    
    /**
     * Get agent display name
     */
    getAgentName() {
        return this.agentSlug.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
}

// Global functions for button onclick handlers
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
        form.reset();
    }
    
    const resultsContainer = document.getElementById('resultsContainer');
    const processingStatus = document.getElementById('processingStatus');
    
    if (resultsContainer) resultsContainer.style.display = 'none';
    if (processingStatus) processingStatus.style.display = 'none';
    
    // Clear validation errors
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach(group => {
        const field = group.querySelector('input, select, textarea');
        if (field) {
            WorkflowsCore.clearFieldError(field.id);
        }
    });
    
    // Scroll back to form
    const formSection = document.getElementById('agentForm');
    if (formSection) {
        formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Quick Agents Panel Functions
function toggleQuickAgents() {
    const panel = document.getElementById('quickAgentsPanel');
    const overlay = document.getElementById('quickAgentsOverlay');
    
    if (panel && overlay) {
        const isOpen = panel.getAttribute('aria-hidden') === 'false';
        
        if (isOpen) {
            // Close panel
            panel.setAttribute('aria-hidden', 'true');
            overlay.setAttribute('aria-hidden', 'true');
            panel.style.transform = 'translateX(100%)';
            overlay.style.opacity = '0';
            overlay.style.visibility = 'hidden';
        } else {
            // Open panel
            panel.setAttribute('aria-hidden', 'false');
            overlay.setAttribute('aria-hidden', 'false');
            panel.style.transform = 'translateX(0)';
            overlay.style.opacity = '1';
            overlay.style.visibility = 'visible';
        }
    }
}

function closeQuickAgents() {
    const panel = document.getElementById('quickAgentsPanel');
    const overlay = document.getElementById('quickAgentsOverlay');
    
    if (panel && overlay) {
        panel.setAttribute('aria-hidden', 'true');
        overlay.setAttribute('aria-hidden', 'true');
        panel.style.transform = 'translateX(100%)';
        overlay.style.opacity = '0';
        overlay.style.visibility = 'hidden';
    }
}

// Close panel with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeQuickAgents();
    }
});

// Initialize AgentsCore when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('agentForm')) {
        window.agentsCore = new AgentsCore();
    }
});