/**
 * Workflows Core - Shared utilities for all agents
 * Contains only truly universal functions that ALL agents use identically
 */

class WorkflowsCore {
    /**
     * Update wallet balance display across the page
     */
    static updateWalletBalance(newBalance) {
        if (newBalance !== undefined) {
            // Update header balance
            const headerBalance = document.querySelector('a[data-wallet-balance]');
            if (headerBalance) {
                headerBalance.textContent = `💰 ${newBalance.toFixed(2)} AED`;
            }
            
            // Update page balance
            const pageBalance = document.getElementById('walletBalance');
            if (pageBalance) {
                pageBalance.textContent = newBalance.toFixed(2);
            }
            
            // Update all data attributes
            document.querySelectorAll('[data-wallet-balance]').forEach(element => {
                element.textContent = `${newBalance.toFixed(2)} AED`;
            });
            
            // Update balance in navigation
            const headerBalanceNav = document.querySelector('a[href="/wallet/"]');
            if (headerBalanceNav) {
                headerBalanceNav.textContent = `💰 ${newBalance.toFixed(2)} AED`;
            }
            
            // Store current balance globally
            window.currentWalletBalance = newBalance;
        }
    }
    
    /**
     * Show toast notification with consistent styling
     */
    static showToast(message, type = 'info') {
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
     * Get CSRF token from page
     */
    static getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
    
    /**
     * Generate unique session ID for N8N calls
     */
    static generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    /**
     * Check user authentication
     */
    static checkAuthentication() {
        const isAuthenticated = document.body.getAttribute('data-user-authenticated') === 'true';
        
        if (!isAuthenticated) {
            this.showToast('Please log in to use this agent', 'error');
            setTimeout(() => {
                window.location.href = '/auth/login/';
            }, 2000);
            return false;
        }
        
        return true;
    }
    
    /**
     * Check wallet balance against required amount
     */
    static checkBalance(requiredAmount) {
        // Get current balance from wallet card
        const balanceElement = document.querySelector('[data-wallet-balance]');
        if (balanceElement) {
            const currentBalance = parseFloat(balanceElement.textContent.replace(/[^\d.]/g, ''));
            if (currentBalance < requiredAmount) {
                this.showToast(`Insufficient balance. You need ${requiredAmount} AED but have ${currentBalance.toFixed(2)} AED`, 'error');
                setTimeout(() => {
                    window.location.href = '/wallet/';
                }, 2000);
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * Deduct wallet balance via Django API
     */
    static async deductBalance(amount, description, agentSlug) {
        try {
            const response = await fetch('/wallet/api/deduct/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    amount: amount,
                    description: description,
                    agent: agentSlug
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Balance deduction failed');
            }
            
            const result = await response.json();
            this.updateWalletBalance(result.new_balance);
            return result;
            
        } catch (error) {
            console.error('Wallet deduction error:', error);
            this.showToast(`Payment error: ${error.message}`, 'error');
            throw error;
        }
    }
    
    /**
     * Show processing status (common pattern)
     */
    static showProcessing(customTitle = 'Processing your request...') {
        const processingStatus = document.getElementById('processingStatus');
        const resultsContainer = document.getElementById('resultsContainer');
        
        if (processingStatus) {
            processingStatus.style.display = 'block';
            processingStatus.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
        
        // Show processing toast
        this.showToast('🔄 ' + customTitle, 'info');
    }
    
    /**
     * Hide processing status (common pattern)
     */
    static hideProcessing() {
        const processingStatus = document.getElementById('processingStatus');
        if (processingStatus) {
            processingStatus.style.display = 'none';
        }
    }
    
    /**
     * Copy text to clipboard with feedback
     */
    static async copyToClipboard(text, successMessage = 'Copied to clipboard!') {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('📋 ' + successMessage, 'success');
        } catch (err) {
            console.error('Failed to copy:', err);
            this.showToast('❌ Failed to copy to clipboard', 'error');
        }
    }
    
    /**
     * Download text as file with feedback
     */
    static downloadAsFile(content, filename, successMessage = 'File downloaded!') {
        try {
            const blob = new Blob([content], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            // Show success message (file download is good feedback but toast confirms)
            this.showToast('💾 ' + successMessage, 'success');
        } catch (error) {
            console.error('Download error:', error);
            this.showToast('❌ Failed to download file', 'error');
        }
    }
    
    /**
     * Format file size for display
     */
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    /**
     * Show field validation error
     */
    static showFieldError(fieldName, message) {
        const field = document.getElementById(fieldName);
        const errorElement = document.getElementById(`${fieldName}-error`);
        
        if (field) {
            field.classList.add('error');
        }
        
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    }
    
    /**
     * Clear field validation error
     */
    static clearFieldError(fieldName) {
        const field = document.getElementById(fieldName);
        const errorElement = document.getElementById(`${fieldName}-error`);
        
        if (field) {
            field.classList.remove('error');
        }
        
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.style.display = 'none';
        }
    }
    
    /**
     * Quick Agent Panel Management (common across all agents)
     */
    static toggleQuickAgents() {
        const panel = document.getElementById('quickAgentsPanel');
        const overlay = document.getElementById('quickAgentsOverlay');
        const toggle = document.querySelector('.quick-agent-toggle');
        
        if (!panel || !overlay) return;
        
        const isActive = panel.classList.contains('active');
        
        if (isActive) {
            // Close panel
            panel.classList.remove('active');
            overlay.classList.remove('active');
            if (toggle) toggle.classList.remove('active');
            // Update ARIA attributes
            if (toggle) toggle.setAttribute('aria-expanded', 'false');
            panel.setAttribute('aria-hidden', 'true');
            overlay.setAttribute('aria-hidden', 'true');
        } else {
            // Open panel
            panel.classList.add('active');
            overlay.classList.add('active');
            if (toggle) toggle.classList.add('active');
            // Update ARIA attributes
            if (toggle) toggle.setAttribute('aria-expanded', 'true');
            panel.setAttribute('aria-hidden', 'false');
            overlay.setAttribute('aria-hidden', 'false');
        }
    }
    
    static closeQuickAgents() {
        const panel = document.getElementById('quickAgentsPanel');
        const overlay = document.getElementById('quickAgentsOverlay');
        const toggle = document.querySelector('.quick-agent-toggle');
        
        if (panel) panel.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
        if (toggle) toggle.classList.remove('active');
        
        // Update ARIA attributes
        if (toggle) toggle.setAttribute('aria-expanded', 'false');
        if (panel) panel.setAttribute('aria-hidden', 'true');
        if (overlay) overlay.setAttribute('aria-hidden', 'true');
    }
    
    /**
     * Initialize form validation on all forms (common pattern)
     */
    static initializeFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('input', () => {
                    if (input.value.trim()) {
                        this.clearFieldError(input.name);
                    }
                });
            });
        });
    }
    
    /**
     * Show/hide results container (common pattern)
     */
    static showResults(content, title = 'Results') {
        const resultsContainer = document.getElementById('resultsContainer');
        const resultsTitle = document.querySelector('#resultsContainer .widget-title');
        const resultsContent = document.querySelector('#resultsContainer .results-content');
        
        if (resultsContainer) {
            resultsContainer.style.display = 'block';
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        
        if (resultsTitle) {
            resultsTitle.textContent = title;
        }
        
        if (resultsContent) {
            resultsContent.innerHTML = content;
        }
        
        // Hide processing
        this.hideProcessing();
    }
    
    /**
     * Copy agent results to clipboard (common agent function)
     */
    static copyResults() {
        const content = document.getElementById('resultsContent') || document.querySelector('.results-content');
        if (content) {
            const text = content.textContent || content.innerText || '';
            this.copyToClipboard(text, 'Results copied to clipboard!');
        } else {
            this.showToast('❌ No results to copy', 'error');
        }
    }
    
    /**
     * Download agent results as file (common agent function)
     */
    static downloadResults(filename = 'analysis-results.txt') {
        const content = document.getElementById('resultsContent') || document.querySelector('.results-content');
        if (content) {
            const text = content.textContent || content.innerText || '';
            this.downloadAsFile(text, filename, 'Results downloaded!');
        } else {
            this.showToast('❌ No results to download', 'error');
        }
    }
    
    /**
     * Reset agent form and hide results (common agent function)
     */
    static resetForm() {
        const form = document.getElementById('agentForm');
        if (form) {
            form.reset();
        }
        
        const resultsContainer = document.getElementById('resultsContainer');
        const processingStatus = document.getElementById('processingStatus');
        
        if (resultsContainer) resultsContainer.style.display = 'none';
        if (processingStatus) processingStatus.style.display = 'none';
        
        // Reset file upload areas
        const uploadAreas = document.querySelectorAll('.file-upload-area');
        uploadAreas.forEach(area => {
            area.classList.remove('file-selected');
            const uploadText = area.querySelector('.upload-text');
            if (uploadText) {
                uploadText.innerHTML = `
                    <div class="upload-icon">📁</div>
                    <div><strong>Click to upload</strong> or drag and drop</div>
                    <div>PDF files only</div>
                `;
            }
        });
        
        // Reset radio selections to first option
        const radioCards = document.querySelectorAll('.radio-card');
        radioCards.forEach(card => card.classList.remove('selected'));
        const firstCard = document.querySelector('.radio-card');
        if (firstCard) {
            firstCard.classList.add('selected');
            const input = firstCard.querySelector('input[type="radio"]');
            if (input) input.checked = true;
        }
        
        this.showToast('🔄 Form reset', 'info');
    }
    
    /**
     * Setup drag and drop for file inputs (enhanced from prototype)
     */
    static setupDragAndDrop(container, fileInput) {
        if (!container || !fileInput) return;
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            container.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            container.addEventListener(eventName, () => {
                container.classList.add('dragover');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            container.addEventListener(eventName, () => {
                container.classList.remove('dragover');
            }, false);
        });
        
        container.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                fileInput.dispatchEvent(new Event('change'));
            }
        }, false);
    }
    
    /**
     * Handle file input change (common pattern for file uploads)
     */
    static handleFileChange(fileInput) {
        const file = fileInput.files[0];
        const fieldName = fileInput.name;
        const container = fileInput.closest('.file-upload-container');
        
        if (!file || !container) return;
        
        const fileInfo = container.querySelector(`#${fieldName}_file_info`);
        const fileName = fileInfo?.querySelector('.file-name');
        const fileSize = fileInfo?.querySelector('.file-size');
        const uploadArea = container.querySelector(`#${fieldName}_upload_area`);
        
        if (fileName) fileName.textContent = file.name;
        if (fileSize) fileSize.textContent = this.formatFileSize(file.size);
        if (fileInfo) fileInfo.style.display = 'block';
        if (uploadArea) uploadArea.style.display = 'none';
        
        // Clear any previous errors
        this.clearFieldError(fieldName);
        
        // Show success feedback
        this.showToast(`📁 File selected: ${file.name}`, 'success');
    }
    
    /**
     * Remove selected file (common pattern)
     */
    static removeFile(fieldName) {
        const fileInput = document.getElementById(fieldName);
        const container = fileInput?.closest('.file-upload-container');
        
        if (!fileInput || !container) return;
        
        const fileInfo = container.querySelector(`#${fieldName}_file_info`);
        const uploadArea = container.querySelector(`#${fieldName}_upload_area`);
        
        // Clear file input
        fileInput.value = '';
        
        // Hide file info, show upload area
        if (fileInfo) fileInfo.style.display = 'none';
        if (uploadArea) uploadArea.style.display = 'block';
        
        this.showToast('📁 File removed', 'info');
    }
}

// Global utility functions that all agents can use
function toggleQuickAgents() {
    WorkflowsCore.toggleQuickAgents();
}

function closeQuickAgents() {
    WorkflowsCore.closeQuickAgents();
}

// Global convenience functions for common actions
function removeFile(fieldName) {
    WorkflowsCore.removeFile(fieldName);
}

function showToast(message, type = 'info') {
    WorkflowsCore.showToast(message, type);
}

function copyToClipboard(text, successMessage) {
    WorkflowsCore.copyToClipboard(text, successMessage);
}

function downloadAsFile(content, filename, successMessage) {
    WorkflowsCore.downloadAsFile(content, filename, successMessage);
}

// Global convenience functions for common agent actions
function copyResults() {
    WorkflowsCore.copyResults();
}

function downloadResults(filename) {
    WorkflowsCore.downloadResults(filename);
}

function resetForm() {
    WorkflowsCore.resetForm();
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize form validation for all forms
    WorkflowsCore.initializeFormValidation();
    
    // Setup file upload drag and drop for any file inputs
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        const container = input.closest('.file-upload-container');
        if (container) {
            WorkflowsCore.setupDragAndDrop(container, input);
        }
        
        // Setup file change handler
        input.addEventListener('change', () => {
            WorkflowsCore.handleFileChange(input);
        });
    });
    
    // Set initial ARIA states for quick agents panel
    const quickAgentsButton = document.querySelector('.quick-agent-toggle');
    const panel = document.getElementById('quickAgentsPanel');
    const overlay = document.getElementById('quickAgentsOverlay');
    
    if (quickAgentsButton) quickAgentsButton.setAttribute('aria-expanded', 'false');
    if (panel) panel.setAttribute('aria-hidden', 'true');
    if (overlay) overlay.setAttribute('aria-hidden', 'true');
});

// Close panel with Escape key (common functionality)
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        WorkflowsCore.closeQuickAgents();
    }
});

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WorkflowsCore;
}