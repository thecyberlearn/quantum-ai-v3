/**
 * Data Analyzer - Agent-Specific JavaScript
 * Handles unique functionality for Data Analyzer agent
 * Uses WorkflowsCore architecture like other agents
 */

class DataAnalyzerProcessor extends WorkflowsCore {
    constructor() {
        super();
        this.agentSlug = 'data-analyzer';
        this.webhookUrl = 'http://localhost:5678/webhook/simple-pdf-processor';
        this.price = 8.0; // Will be overridden by template data
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
        
        // Initialize file upload functionality
        this.initializeFileUpload();
        
        // Initialize form validation
        this.initializeFormValidation();
        
        // Set initial radio selection
        const firstRadio = document.querySelector('.radio-card');
        if (firstRadio && !document.querySelector('.radio-card.selected')) {
            firstRadio.classList.add('selected');
            const input = firstRadio.querySelector('input[type="radio"]');
            if (input) input.checked = true;
        }
    }
    
    /**
     * Initialize file upload functionality
     */
    initializeFileUpload() {
        const fileInput = document.getElementById('dataFile');
        if (fileInput) {
            fileInput.addEventListener('change', this.handleFileChange.bind(this));
        }
        
        // Initialize drag and drop
        const uploadArea = document.querySelector('.file-upload-area');
        if (uploadArea && fileInput) {
            this.constructor.setupDragAndDrop(uploadArea, fileInput);
        }
    }
    
    /**
     * Handle form submission with hybrid N8N/Django approach
     */
    async handleFormSubmission(e) {
        e.preventDefault();
        
        if (!this.isFormValid()) {
            this.constructor.showToast('Please upload a file and select analysis type', 'error');
            return;
        }
        
        // Check authentication and balance
        if (!this.constructor.checkAuthentication()) return;
        if (!this.constructor.checkBalance(this.price)) return;
        
        // Show processing status and disable submit button
        this.constructor.showProcessing('Analyzing your data file...');
        
        const submitBtn = document.getElementById('generateBtn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = '⏳ Analyzing...';
        }
        
        try {
            // Try direct N8N integration for better performance (with Django fallback)
            const useDirectN8N = false; // Feature flag - disabled for file uploads (complex)
            
            if (useDirectN8N) {
                await this.processViaDirectN8N(e.target);
            } else {
                // For file uploads, use immediate Django processing (N8N direct upload is complex)
                await this.processViaDjangoImmediate(e.target);
            }
        } catch (error) {
            console.error('Form submission error:', error);
            this.constructor.hideProcessing();
            this.constructor.showToast('❌ Connection error. Please try again.', 'error');
            this.resetSubmitButton();
        }
    }
    
    /**
     * Django processing for file uploads (immediate response for data analyzer)
     */
    async processViaDjangoImmediate(form) {
        const formData = new FormData(form);
        
        const response = await fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        
        const result = await response.json();
        
        if (result.success && result.analysis_results) {
            // Data analyzer returns results immediately, no polling needed
            this.constructor.hideProcessing();
            
            if (result.wallet_balance !== undefined) {
                this.constructor.updateWalletBalance(result.wallet_balance);
            }
            
            // Display results immediately
            const analysisData = result.analysis_results;
            const formattedHtml = this.formatAnalysisResults(analysisData);
            WorkflowsCore.showResults(formattedHtml, 'Analysis Results');
            this.constructor.showToast('✅ Data analysis completed successfully!', 'success');
            
            this.resetSubmitButton();
        } else {
            this.constructor.hideProcessing();
            this.constructor.showToast(`❌ ${result.error || 'Processing failed'}`, 'error');
            this.resetSubmitButton();
        }
    }
    
    /**
     * Form validation specific to Data Analyzer
     */
    initializeFormValidation() {
        const fileInput = document.getElementById('dataFile');
        const analysisTypeInputs = document.querySelectorAll('input[name="analysisType"]');
        
        if (fileInput) {
            fileInput.addEventListener('change', () => this.validateField('dataFile'));
        }
        
        analysisTypeInputs.forEach(input => {
            input.addEventListener('change', () => this.validateField('analysisType'));
        });
    }
    
    validateField(fieldName) {
        switch (fieldName) {
            case 'dataFile':
                const fileInput = document.getElementById('dataFile');
                if (!fileInput.files || fileInput.files.length === 0) {
                    this.constructor.showFieldError('dataFile', 'Please select a data file');
                    return false;
                }
                
                const file = fileInput.files[0];
                const maxSize = 10 * 1024 * 1024; // 10MB
                if (file.size > maxSize) {
                    this.constructor.showFieldError('dataFile', 'File too large. Maximum size is 10MB');
                    return false;
                }
                
                const allowedExtensions = ['.pdf'];
                const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
                if (!allowedExtensions.includes(fileExtension)) {
                    this.constructor.showFieldError('dataFile', 'Unsupported file type. Please use PDF files only');
                    return false;
                }
                break;
                
            case 'analysisType':
                const analysisType = document.querySelector('input[name="analysisType"]:checked');
                if (!analysisType) {
                    this.constructor.showFieldError('analysisType', 'Please select an analysis type');
                    return false;
                }
                break;
        }
        
        this.constructor.clearFieldError(fieldName);
        return true;
    }
    
    isFormValid() {
        const fileValid = this.validateField('dataFile');
        const analysisValid = this.validateField('analysisType');
        
        return fileValid && analysisValid;
    }
    
    /**
     * Handle file change events
     */
    handleFileChange(event) {
        const file = event.target.files[0];
        const fileNameDisplay = document.getElementById('fileName');
        const fileSizeDisplay = document.getElementById('fileSize');
        const uploadArea = document.querySelector('.file-upload-area');
        
        if (file) {
            if (fileNameDisplay) {
                fileNameDisplay.textContent = `✅ ${file.name}`;
                fileNameDisplay.style.display = 'block';
            }
            if (fileSizeDisplay) {
                fileSizeDisplay.textContent = this.formatFileSize(file.size);
                fileSizeDisplay.style.display = 'block';
            }
            
            // Add visual feedback
            if (uploadArea) {
                uploadArea.classList.add('file-selected');
            }
            
            // Clear any previous errors
            this.constructor.clearFieldError('dataFile');
            
            // Validate file immediately
            this.validateField('dataFile');
        } else {
            // Reset display if no file
            if (fileNameDisplay) {
                fileNameDisplay.textContent = '';
                fileNameDisplay.style.display = 'none';
            }
            if (fileSizeDisplay) {
                fileSizeDisplay.textContent = '';
                fileSizeDisplay.style.display = 'none';
            }
            if (uploadArea) uploadArea.classList.remove('file-selected');
        }
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
     * Format analysis results for HTML display
     */
    formatAnalysisResults(analysisData) {
        let resultsHtml = '<h3>✅ Analysis Complete</h3>';
        
        // Check if we have structured sections data
        if (analysisData && typeof analysisData === 'object' && analysisData.sections && Array.isArray(analysisData.sections) && analysisData.sections.length > 0) {
            resultsHtml += '<div class="analysis-sections">';
            
            analysisData.sections.forEach(section => {
                if (section.heading && section.content) {
                    resultsHtml += `
                        <div style="background: var(--surface-variant); border-radius: var(--radius-md); padding: var(--spacing-lg); margin-bottom: var(--spacing-md); border-left: 4px solid var(--primary);">
                            <h4 style="color: var(--primary); font-weight: 600; margin: 0 0 var(--spacing-md) 0; font-size: 16px;">📋 ${this.escapeHtml(section.heading)}</h4>
                            <div style="color: var(--on-surface); line-height: 1.6; font-size: 14px;">${this.escapeHtml(section.content).replace(/\n/g, '<br>')}</div>
                        </div>
                    `;
                }
            });
            
            resultsHtml += '</div>';
        } else {
            // Handle simple text response or fallback
            const content = typeof analysisData === 'string' ? analysisData : JSON.stringify(analysisData, null, 2);
            resultsHtml += `
                <div style="background: var(--surface-variant); border-radius: var(--radius-md); padding: var(--spacing-lg); margin-bottom: var(--spacing-md); border-left: 4px solid var(--primary);">
                    <h4 style="color: var(--primary); font-weight: 600; margin: 0 0 var(--spacing-md) 0; font-size: 16px;">📊 Analysis Results</h4>
                    <div style="color: var(--on-surface); line-height: 1.6; font-size: 14px; white-space: pre-wrap;">${this.escapeHtml(content)}</div>
                </div>
            `;
        }
        
        // Add timestamp
        if (analysisData && analysisData.timestamp) {
            resultsHtml += `<p style="margin-top: var(--spacing-lg); text-align: center; color: var(--on-surface-variant);"><small>Analysis completed: ${new Date(analysisData.timestamp).toLocaleString()}</small></p>`;
        } else {
            resultsHtml += `<p style="margin-top: var(--spacing-lg); text-align: center; color: var(--on-surface-variant);"><small>Analysis completed: ${new Date().toLocaleString()}</small></p>`;
        }
        
        return resultsHtml;
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
            submitBtn.textContent = `🚀 Analyze Data (${this.price} AED)`;
        }
    }
}

// Data Analyzer specific functions (global for template onclick handlers)
function selectRadio(value) {
    // Remove selected class from all cards
    document.querySelectorAll('.radio-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Add selected class to clicked card
    const selectedCard = document.querySelector(`input[value="${value}"]`).closest('.radio-card');
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }
    
    // Select the radio button
    const radioInput = document.getElementById(value);
    if (radioInput) {
        radioInput.checked = true;
    }
}

// Result action functions (global for button onclick handlers)
function copyResults() {
    const content = document.getElementById('resultsContent');
    if (content) {
        const text = content.textContent || '';
        WorkflowsCore.copyToClipboard(text, 'Analysis results copied to clipboard!');
    }
}

function downloadResults() {
    const content = document.getElementById('resultsContent');
    if (content) {
        const text = content.textContent || '';
        WorkflowsCore.downloadAsFile(text, 'data-analysis-results.txt', 'Analysis results downloaded!');
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
    
    // Clear file display
    const fileNameDisplay = document.getElementById('fileName');
    const fileSizeDisplay = document.getElementById('fileSize');
    if (fileNameDisplay) {
        fileNameDisplay.textContent = '';
        fileNameDisplay.style.display = 'none';
    }
    if (fileSizeDisplay) {
        fileSizeDisplay.textContent = '';
        fileSizeDisplay.style.display = 'none';
    }
    
    // Clear validation errors
    WorkflowsCore.clearFieldError('dataFile');
    WorkflowsCore.clearFieldError('analysisType');
    
    // Reset radio selection
    const firstRadio = document.querySelector('.radio-card');
    if (firstRadio) {
        document.querySelectorAll('.radio-card').forEach(card => card.classList.remove('selected'));
        firstRadio.classList.add('selected');
        const input = firstRadio.querySelector('input[type="radio"]');
        if (input) input.checked = true;
    }
    
    // Scroll back to form
    const formSection = document.getElementById('agentForm');
    if (formSection) {
        formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Initialize Data Analyzer Processor when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize processor (data attributes set by template)
    window.dataAnalyzerProcessor = new DataAnalyzerProcessor();
});