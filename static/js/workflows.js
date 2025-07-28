/**
 * Universal Workflows JavaScript Framework
 * Handles all agent interactions with direct N8N integration
 */

class WorkflowProcessor {
    constructor(agentSlug, webhookUrl, price) {
        this.agentSlug = agentSlug;
        this.webhookUrl = webhookUrl;
        this.price = price;
        this.sessionId = this.generateSessionId();
        this.processing = false;
    }
    
    /**
     * Handle form submission - main entry point
     */
    async handleFormSubmission(event) {
        event.preventDefault();
        
        if (this.processing) {
            this.showToast('Please wait, processing your previous request...', 'warning');
            return;
        }
        
        const form = event.target;
        const formData = new FormData(form);
        
        // Convert FormData to object
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        await this.processWorkflow(data, formData);
    }
    
    /**
     * Main workflow processing function
     */
    async processWorkflow(data, formData = null) {
        try {
            this.processing = true;
            
            // 1. Validate form
            if (!this.validateForm(data)) {
                this.processing = false;
                return;
            }
            
            // 2. Check authentication and balance
            if (!await this.checkBalance()) {
                this.processing = false;
                return;
            }
            
            // 3. Show processing status
            this.showProcessing();
            
            // 4. Call N8N directly
            const result = await this.callN8N(data, formData);
            
            if (result && result.output) {
                // 5. Deduct balance via Django API
                await this.deductBalance();
                
                // 6. Display results
                this.displayResults(result);
                this.showToast('Processing completed successfully!', 'success');
            } else {
                throw new Error('No output received from N8N');
            }
            
        } catch (error) {
            console.error('Workflow processing error:', error);
            this.showError(`Processing failed: ${error.message}`);
            this.showToast('Processing failed. Please try again.', 'error');
        } finally {
            this.processing = false;
            this.hideProcessing();
        }
    }
    
    /**
     * Call N8N webhook directly
     */
    async callN8N(data, formData = null) {
        const messageText = this.formatMessage(data);
        
        const payload = {
            sessionId: this.sessionId,
            message: { text: messageText },
            agentSlug: this.agentSlug,
            timestamp: new Date().toISOString()
        };
        
        // Handle file uploads if present
        if (formData && this.hasFileUploads(data)) {
            // For file uploads, we need to handle differently
            return await this.callN8NWithFiles(messageText, formData);
        }
        
        const response = await fetch(this.webhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`N8N webhook failed: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    /**
     * Handle N8N calls with file uploads
     */
    async callN8NWithFiles(messageText, formData) {
        // Create multipart form data for file uploads
        const uploadData = new FormData();
        uploadData.append('sessionId', this.sessionId);
        uploadData.append('message', JSON.stringify({ text: messageText }));
        uploadData.append('agentSlug', this.agentSlug);
        
        // Add files
        for (let [key, value] of formData.entries()) {
            if (value instanceof File) {
                uploadData.append(key, value);
            }
        }
        
        const response = await fetch(this.webhookUrl, {
            method: 'POST',
            body: uploadData
        });
        
        if (!response.ok) {
            throw new Error(`N8N webhook with files failed: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    /**
     * Deduct wallet balance via Django API
     */
    async deductBalance() {
        const response = await fetch('/wallet/api/deduct/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({
                amount: this.price,
                description: `${this.agentSlug} processing`,
                agent: this.agentSlug
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Balance deduction failed');
        }
        
        const result = await response.json();
        this.updateWalletBalance(result.new_balance);
        return result;
    }
    
    /**
     * Validate form data
     */
    validateForm(data) {
        const requiredFields = document.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            const value = data[field.name];
            if (!value || (typeof value === 'string' && value.trim() === '')) {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
        });
        
        return isValid;
    }
    
    /**
     * Check user authentication and balance
     */
    async checkBalance() {
        const isAuthenticated = document.body.getAttribute('data-user-authenticated') === 'true';
        
        if (!isAuthenticated) {
            this.showToast('Please log in to use this agent', 'error');
            setTimeout(() => {
                window.location.href = '/auth/login/';
            }, 2000);
            return false;
        }
        
        // Get current balance from wallet card
        const balanceElement = document.querySelector('[data-wallet-balance]');
        if (balanceElement) {
            const currentBalance = parseFloat(balanceElement.textContent.replace(/[^\d.]/g, ''));
            if (currentBalance < this.price) {
                this.showToast(`Insufficient balance. You need ${this.price} AED but have ${currentBalance} AED`, 'error');
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * Format message for N8N based on agent configuration
     */
    formatMessage(data) {
        // Create a descriptive message based on the agent and data
        let message = `Process ${this.agentSlug} request:\n\n`;
        
        for (const [key, value] of Object.entries(data)) {
            if (value && key !== 'csrfmiddlewaretoken') {
                const fieldLabel = this.getFieldLabel(key) || key.replace(/[_-]/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                message += `${fieldLabel}: ${value}\n`;
            }
        }
        
        return message.trim();
    }
    
    /**
     * Get field label from DOM
     */
    getFieldLabel(fieldName) {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            const label = document.querySelector(`label[for="${field.id}"]`);
            if (label) {
                return label.textContent.replace('*', '').trim();
            }
        }
        return null;
    }
    
    /**
     * Check if form has file uploads
     */
    hasFileUploads(data) {
        return Object.values(data).some(value => value instanceof File);
    }
    
    /**
     * Display processing status
     */
    showProcessing() {
        const processingStatus = document.getElementById('processingStatus');
        const resultsContainer = document.getElementById('resultsContainer');
        const submitBtn = document.getElementById('submitBtn');
        
        if (processingStatus) {
            processingStatus.style.display = 'block';
            processingStatus.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
        
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing...';
        }
    }
    
    /**
     * Hide processing status
     */
    hideProcessing() {
        const processingStatus = document.getElementById('processingStatus');
        const submitBtn = document.getElementById('submitBtn');
        
        if (processingStatus) {
            processingStatus.style.display = 'none';
        }
        
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = `🚀 Process with ${this.agentSlug.replace(/-/g, ' ')} (${this.price} AED)`;
        }
    }
    
    /**
     * Display results
     */
    displayResults(result) {
        const resultsContainer = document.getElementById('resultsContainer');
        const resultsContent = document.querySelector('.results-content');
        
        if (!resultsContainer || !resultsContent) return;
        
        // Clear previous results
        resultsContent.innerHTML = '';
        
        // Create result content
        const resultDiv = document.createElement('div');
        resultDiv.className = 'workflow-result';
        
        if (result.output) {
            // Create formatted output
            const outputDiv = document.createElement('div');
            outputDiv.className = 'result-output';
            
            // Handle different output formats
            if (typeof result.output === 'string') {
                outputDiv.innerHTML = this.formatTextOutput(result.output);
            } else if (typeof result.output === 'object') {
                outputDiv.innerHTML = this.formatObjectOutput(result.output);
            } else {
                outputDiv.textContent = String(result.output);
            }
            
            resultDiv.appendChild(outputDiv);
        }
        
        // Add action buttons
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'result-actions';
        actionsDiv.innerHTML = `
            <button class="btn btn-secondary" onclick="workflowProcessor.copyResults()">
                📋 Copy Results
            </button>
            <button class="btn btn-secondary" onclick="workflowProcessor.downloadResults()">
                💾 Download
            </button>
            <button class="btn btn-primary" onclick="workflowProcessor.newRequest()">
                🔄 New Request
            </button>
        `;
        
        resultDiv.appendChild(actionsDiv);
        resultsContent.appendChild(resultDiv);
        
        // Show results container
        resultsContainer.style.display = 'block';
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Store results for actions
        this.lastResult = result;
    }
    
    /**
     * Format text output with proper styling
     */
    formatTextOutput(text) {
        // Convert newlines to HTML breaks and preserve formatting
        return text
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^(.*)/, '<p>$1')
            .replace(/(.*?)$/, '$1</p>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
            .replace(/\*(.*?)\*/g, '<em>$1</em>');  // Italic
    }
    
    /**
     * Format object output as structured data
     */
    formatObjectOutput(obj) {
        if (obj.formatted_content) {
            return this.formatTextOutput(obj.formatted_content);
        }
        
        let html = '<div class="structured-output">';
        for (const [key, value] of Object.entries(obj)) {
            if (value && key !== 'raw_data') {
                const label = key.replace(/[_-]/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                html += `<div class="output-item">`;
                html += `<strong>${label}:</strong> `;
                if (typeof value === 'string') {
                    html += this.formatTextOutput(value);
                } else {
                    html += String(value);
                }
                html += `</div>`;
            }
        }
        html += '</div>';
        return html;
    }
    
    /**
     * Copy results to clipboard
     */
    async copyResults() {
        if (!this.lastResult) return;
        
        let textToCopy = '';
        if (typeof this.lastResult.output === 'string') {
            textToCopy = this.lastResult.output;
        } else if (typeof this.lastResult.output === 'object') {
            textToCopy = JSON.stringify(this.lastResult.output, null, 2);
        }
        
        try {
            await navigator.clipboard.writeText(textToCopy);
            this.showToast('Results copied to clipboard!', 'success');
        } catch (err) {
            this.showToast('Failed to copy to clipboard', 'error');
        }
    }
    
    /**
     * Download results as text file
     */
    downloadResults() {
        if (!this.lastResult) return;
        
        let content = '';
        if (typeof this.lastResult.output === 'string') {
            content = this.lastResult.output;
        } else {
            content = JSON.stringify(this.lastResult.output, null, 2);
        }
        
        const blob = new Blob([content], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.agentSlug}-result-${new Date().toISOString().slice(0, 10)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        this.showToast('Results downloaded!', 'success');
    }
    
    /**
     * Reset form for new request
     */
    newRequest() {
        const form = document.getElementById('workflowForm');
        if (form) {
            form.reset();
            
            // Clear file uploads
            document.querySelectorAll('.file-info').forEach(info => {
                info.style.display = 'none';
            });
            
            // Reset radio cards
            document.querySelectorAll('.radio-card').forEach(card => {
                card.classList.remove('selected');
            });
        }
        
        // Hide results
        const resultsContainer = document.getElementById('resultsContainer');
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
        
        // Scroll to form
        form.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        this.showToast('Ready for new request', 'info');
    }
    
    /**
     * Show error message
     */
    showError(message) {
        const resultsContainer = document.getElementById('resultsContainer');
        const resultsContent = document.querySelector('.results-content');
        
        if (resultsContainer && resultsContent) {
            resultsContent.innerHTML = `
                <div class="error-message">
                    <div class="error-icon">⚠️</div>
                    <div class="error-text">${message}</div>
                    <button class="btn btn-primary" onclick="workflowProcessor.newRequest()">
                        🔄 Try Again
                    </button>
                </div>
            `;
            resultsContainer.style.display = 'block';
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
    
    /**
     * Show field error
     */
    showFieldError(field, message) {
        this.clearFieldError(field);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        errorDiv.id = `${field.name}_error`;
        
        field.parentNode.appendChild(errorDiv);
        field.classList.add('error');
    }
    
    /**
     * Clear field error
     */
    clearFieldError(field) {
        const existingError = document.getElementById(`${field.name}_error`);
        if (existingError) {
            existingError.remove();
        }
        field.classList.remove('error');
    }
    
    /**
     * Update wallet balance display
     */
    updateWalletBalance(newBalance) {
        if (newBalance !== undefined) {
            // Update all balance displays
            document.querySelectorAll('[data-wallet-balance]').forEach(element => {
                element.textContent = `${newBalance.toFixed(2)} AED`;
            });
            
            // Update balance in navigation
            const headerBalance = document.querySelector('a[href="/wallet/"]');
            if (headerBalance) {
                headerBalance.textContent = `💰 ${newBalance.toFixed(2)} AED`;
            }
            
            // Store current balance globally
            window.currentWalletBalance = newBalance;
        }
    }
    
    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        // Remove existing toasts
        document.querySelectorAll('.toast').forEach(toast => toast.remove());
        
        // Create new toast
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        // Add to page
        document.body.appendChild(toast);
        
        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    /**
     * Handle file input changes
     */
    handleFileChange(event) {
        const input = event.target;
        const file = input.files[0];
        const container = input.closest('.file-upload-container');
        
        if (!container) return;
        
        const fileInfo = container.querySelector('.file-info');
        const uploadArea = container.querySelector('.file-upload-area');
        
        if (file && fileInfo) {
            // Show file info
            const fileName = fileInfo.querySelector('.file-name');
            const fileSize = fileInfo.querySelector('.file-size');
            
            if (fileName) fileName.textContent = file.name;
            if (fileSize) fileSize.textContent = this.formatFileSize(file.size);
            
            fileInfo.style.display = 'block';
            uploadArea.classList.add('has-file');
        }
    }
    
    /**
     * Setup drag and drop for file uploads
     */
    setupDragAndDrop(container, input) {
        const uploadArea = container.querySelector('.file-upload-area');
        if (!uploadArea) return;
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                this.handleFileChange({ target: input });
            }
        });
        
        uploadArea.addEventListener('click', () => {
            input.click();
        });
    }
    
    /**
     * Format file size for display
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    /**
     * Generate unique session ID
     */
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    /**
     * Get CSRF token from page
     */
    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

// Global utility functions
function removeFile(fieldName) {
    const input = document.getElementById(fieldName);
    const container = input.closest('.file-upload-container');
    
    if (input) input.value = '';
    
    if (container) {
        const fileInfo = container.querySelector('.file-info');
        const uploadArea = container.querySelector('.file-upload-area');
        
        if (fileInfo) fileInfo.style.display = 'none';
        if (uploadArea) uploadArea.classList.remove('has-file');
    }
}

function selectRadio(name, value) {
    // Remove selection from all radio cards with this name
    document.querySelectorAll(`input[name="${name}"]`).forEach(radio => {
        radio.closest('.radio-card').classList.remove('selected');
        radio.checked = false;
    });
    
    // Select the clicked radio
    const radio = document.querySelector(`input[name="${name}"][value="${value}"]`);
    if (radio) {
        radio.checked = true;
        radio.closest('.radio-card').classList.add('selected');
    }
}