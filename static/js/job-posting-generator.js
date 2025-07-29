/**
 * Job Posting Generator - Agent-Specific JavaScript
 * Handles unique functionality for Job Posting Generator agent
 * Uses WorkflowsCore architecture like other agents
 */

class JobPostingGeneratorProcessor extends WorkflowsCore {
    constructor() {
        super();
        this.agentSlug = 'job-posting-generator';
        this.webhookUrl = 'http://localhost:5678/webhook/43f84411-eaaa-488c-9b1f-856e90d0aaf6';
        this.price = 4.0; // Will be overridden by template data
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
        this.constructor.showProcessing('Creating your professional job posting...');
        
        const submitBtn = document.getElementById('generateBtn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = '⏳ Generating...';
        }
        
        try {
            // Direct N8N integration
            await this.processViaDirectN8N(e.target);
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
            const jobTitle = formData.get('job_title').trim();
            const companyName = formData.get('company_name').trim();
            const jobDescription = formData.get('job_description').trim();
            const seniorityLevel = formData.get('seniority_level');
            const contractType = formData.get('contract_type');
            const location = formData.get('location').trim();
            const language = formData.get('language') || 'English';
            
            // Create message for N8N
            const messageText = `Create a professional job posting for: ${jobTitle} at ${companyName}. Description: ${jobDescription}. Seniority: ${seniorityLevel}. Contract: ${contractType}. Location: ${location}. Language: ${language}. Make it comprehensive and attractive to candidates.`;
            
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
                `Job Posting Generator - ${jobTitle} at ${companyName}`,
                this.agentSlug
            );
            
            // Display results using the enhanced display function
            this.displayDirectN8NResults(data, jobTitle, companyName);
            
            this.constructor.showToast('✅ Job posting generated successfully!', 'success');
            
        } catch (error) {
            console.error('N8N processing error:', error);
            this.constructor.hideProcessing();
            this.constructor.showToast('❌ Processing failed. Please try again.', 'error');
            this.resetSubmitButton();
        }
    }
    
    
    /**
     * Form validation specific to Job Posting Generator
     */
    initializeFormValidation() {
        const requiredFields = ['job_title', 'company_name', 'job_description', 'seniority_level', 'contract_type', 'location'];
        
        requiredFields.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            if (field) {
                field.addEventListener('blur', () => this.validateField(fieldName));
                field.addEventListener('input', () => this.validateField(fieldName));
            }
        });
    }
    
    validateField(fieldName) {
        const field = document.getElementById(fieldName);
        if (!field) return true;
        
        const value = field.value.trim();
        
        switch (fieldName) {
            case 'job_title':
                if (!value) {
                    this.constructor.showFieldError(fieldName, 'Job title is required');
                    return false;
                }
                if (value.length < 3) {
                    this.constructor.showFieldError(fieldName, 'Job title should be at least 3 characters');
                    return false;
                }
                break;
                
            case 'company_name':
                if (!value) {
                    this.constructor.showFieldError(fieldName, 'Company name is required');
                    return false;
                }
                if (value.length < 2) {
                    this.constructor.showFieldError(fieldName, 'Company name should be at least 2 characters');
                    return false;
                }
                break;
                
            case 'job_description':
                if (!value) {
                    this.constructor.showFieldError(fieldName, 'Job description is required');
                    return false;
                }
                break;
                
            case 'seniority_level':
            case 'contract_type':
                if (!value) {
                    const fieldLabel = fieldName.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                    this.constructor.showFieldError(fieldName, `${fieldLabel} is required`);
                    return false;
                }
                break;
                
            case 'location':
                if (!value) {
                    this.constructor.showFieldError(fieldName, 'Location is required');
                    return false;
                }
                if (value.length < 3) {
                    this.constructor.showFieldError(fieldName, 'Location should be at least 3 characters');
                    return false;
                }
                break;
        }
        
        this.constructor.clearFieldError(fieldName);
        return true;
    }
    
    isFormValid() {
        const requiredFields = ['job_title', 'company_name', 'job_description', 'seniority_level', 'contract_type', 'location'];
        
        let isValid = true;
        requiredFields.forEach(fieldName => {
            if (!this.validateField(fieldName)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    
    /**
     * Display results from direct N8N call
     */
    displayDirectN8NResults(data, jobTitle, companyName) {
        const resultsContainer = document.getElementById('resultsContainer');
        const resultsContent = document.getElementById('resultsContent');
        
        if (!resultsContainer || !resultsContent) return;
        
        let content = '';
        
        // Handle different N8N response formats
        if (typeof data === 'string') {
            content = data;
        } else if (data && typeof data === 'object') {
            content = data.output || data.text || data.content || data.job_posting || data.result || data.message || JSON.stringify(data, null, 2);
        } else {
            content = 'Job posting generated successfully!';
        }
        
        // Clear and populate results securely
        resultsContent.textContent = '';
        this.renderSecureJobContent(resultsContent, content);
        
        // Show results container
        resultsContainer.style.display = 'block';
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        this.resetSubmitButton();
    }
    
    /**
     * Secure content rendering for job postings without innerHTML to prevent XSS
     */
    renderSecureJobContent(container, content) {
        // Sanitize and validate content
        if (!content || typeof content !== 'string') {
            container.textContent = 'No content available';
            return;
        }
        
        // Create wrapper div
        const wrapper = document.createElement('div');
        wrapper.className = 'job-posting-content';
        
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
                element.className = 'job-section-title';
                element.textContent = line.substring(4);
            } else if (line.startsWith('## ')) {
                element = document.createElement('h2');
                element.className = 'job-section-title';
                element.textContent = line.substring(3);
            } else if (line.startsWith('# ')) {
                element = document.createElement('h1');
                element.className = 'job-section-title';
                element.textContent = line.substring(2);
            } else if (line.startsWith('- ')) {
                // Handle list items
                element = document.createElement('li');
                element.textContent = line.substring(2);
            } else {
                // Handle regular text with basic formatting
                element = document.createElement('p');
                element.className = 'job-paragraph';
                this.formatJobTextSecurely(element, line);
            }
            
            wrapper.appendChild(element);
        }
        
        container.appendChild(wrapper);
    }
    
    /**
     * Format job posting text with basic styling while preventing XSS
     */
    formatJobTextSecurely(element, text) {
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
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Reset submit button to original state
     */
    resetSubmitButton() {
        const submitBtn = document.getElementById('generateBtn');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = `💼 Generate Job Posting (${this.price} AED)`;
        }
    }
}

// Result action functions (global for button onclick handlers)
function copyResults() {
    const content = document.getElementById('resultsContent');
    if (content) {
        const text = content.textContent || '';
        WorkflowsCore.copyToClipboard(text, 'Job posting copied to clipboard!');
    }
}

function downloadResults() {
    const content = document.getElementById('resultsContent');
    if (content) {
        const text = content.textContent || '';
        const jobTitle = document.getElementById('job_title')?.value || 'job-posting';
        const filename = `${jobTitle.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}.txt`;
        WorkflowsCore.downloadAsFile(text, filename, 'Job posting downloaded!');
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
    const fields = ['job_title', 'company_name', 'job_description', 'seniority_level', 'contract_type', 'location'];
    fields.forEach(field => WorkflowsCore.clearFieldError(field));
    
    // Scroll back to form
    const formSection = document.getElementById('agentForm');
    if (formSection) {
        formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Initialize Job Posting Generator Processor when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize processor (data attributes set by template)
    window.jobPostingGeneratorProcessor = new JobPostingGeneratorProcessor();
});