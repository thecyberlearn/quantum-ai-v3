/**
 * NetCop AI Agents - Shared Utilities
 * Contains common functions used across all agent templates
 */

window.AgentUtils = {
    /**
     * Simple Text Formatter
     * Cleans AI-generated text and converts to readable HTML
     */
    parseMarkdown(text) {
        if (!text) return '';
        
        return text
            .replace(/\*\*/g, '') // Remove markdown bold syntax
            .replace(/\#{1,3}\s/g, '') // Remove header syntax
            .replace(/\n{3,}/g, '\n\n') // Reduce excessive line breaks
            .replace(/\n/g, '<br>') // Convert line breaks to HTML
            .trim();
    },

    /**
     * Update wallet balance display across all agents
     */
    updateWalletBalance(newBalance) {
        const balanceElement = document.querySelector('[data-wallet-balance]') || 
                              document.getElementById('walletBalance');
        if (balanceElement) {
            balanceElement.textContent = `${newBalance.toFixed(2)} AED`;
        }
        window.currentWalletBalance = newBalance;
    },

    /**
     * Reset UI to initial state
     */
    resetUI(config) {
        const elements = {
            processingStatus: document.getElementById(config.processingStatusId || 'processingStatus'),
            processButton: document.getElementById(config.processButtonId || 'processButton'),
            results: document.getElementById(config.resultsId)
        };

        if (elements.processingStatus) {
            elements.processingStatus.style.display = 'none';
        }
        
        if (elements.processButton) {
            elements.processButton.disabled = false;
            elements.processButton.innerHTML = config.buttonText || 'Process';
            elements.processButton.classList.remove('loading');
        }

        if (elements.results) {
            elements.results.style.display = 'none';
        }
    },

    /**
     * Show processing status
     */
    showProcessing(config) {
        const elements = {
            processingStatus: document.getElementById(config.processingStatusId || 'processingStatus'),
            processButton: document.getElementById(config.processButtonId || 'processButton'),
            results: document.getElementById(config.resultsId)
        };

        if (elements.processingStatus) {
            elements.processingStatus.style.display = 'block';
        }
        
        if (elements.processButton) {
            elements.processButton.disabled = true;
            elements.processButton.classList.add('loading');
            elements.processButton.innerHTML = config.processingText || '⏳ Processing...';
        }

        if (elements.results) {
            elements.results.style.display = 'none';
        }
    },

    /**
     * Show toast notification with duplicate prevention
     */
    showToast(message, type = 'info') {
        // Prevent duplicate toasts
        const existingToast = document.querySelector('.agent-toast');
        if (existingToast) {
            existingToast.remove();
        }

        const toast = document.createElement('div');
        toast.className = 'agent-toast';
        toast.style.cssText = `
            position: fixed;
            top: 16px;
            right: 16px;
            padding: 8px 12px;
            border-radius: 4px;
            color: white;
            font-size: 13px;
            z-index: 1000;
            max-width: 300px;
            font-weight: 500;
            ${type === 'success' ? 'background: #10b981;' : 'background: #ef4444;'}
        `;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 2000);
    },

    /**
     * Display results with markdown parsing
     * Standardized across all agents
     */
    displayResults(config) {
        const resultsContainer = document.getElementById(config.resultsId);
        const contentContainer = document.getElementById(config.contentId);
        
        if (config.result.success && config.result.status === 'completed') {
            // Get content from various possible fields
            const content = config.result.content || 
                           config.result.job_posting_content || 
                           config.result.ad_copy_content ||
                           config.result.analysis_results ||
                           config.result.insights_summary ||
                           config.result.report_text ||
                           config.result.weather_data ||
                           config.result.formatted_report ||
                           config.result.output_text || 
                           config.defaultMessage || 
                           'Content generated successfully!';
            
            // Parse markdown and display as HTML
            const formattedContent = this.parseMarkdown(content);
            contentContainer.innerHTML = formattedContent;
            
            resultsContainer.style.display = 'block';
            
            // Update wallet balance if provided
            if (config.result.wallet_balance !== undefined) {
                this.updateWalletBalance(config.result.wallet_balance);
            }
            
            this.showToast(config.successMessage || '✅ Content generated and payment processed!', 'success');
        } else {
            this.showToast(config.errorMessage || '❌ Failed to generate content - no charge applied', 'error');
        }
    },

    /**
     * Generate text for copy/download functionality
     */
    generateTextForExport(contentElementId) {
        const content = document.getElementById(contentElementId);
        if (content) {
            return content.innerText || content.textContent || '';
        }
        return 'No content available';
    },

    /**
     * Copy content to clipboard
     */
    copyToClipboard(text, successMessage = 'Content copied to clipboard!') {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast(`📋 ${successMessage}`, 'success');
        }).catch(() => {
            this.showToast('Failed to copy content', 'error');
        });
    },

    /**
     * Download content as text file
     */
    downloadAsFile(text, filename, successMessage = 'File downloaded!') {
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename || `content-${Date.now()}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        this.showToast(`💾 ${successMessage}`, 'success');
    }
};

/**
 * Progressive status steps for better UX
 */
window.StatusStepper = class {
    constructor(steps, statusTextElementId, interval = 800) {
        this.steps = steps;
        this.statusTextElement = document.getElementById(statusTextElementId);
        this.interval = interval;
        this.currentStep = 0;
        this.stepInterval = null;
    }

    start() {
        this.currentStep = 0;
        this.stepInterval = setInterval(() => {
            if (this.currentStep < this.steps.length && this.statusTextElement) {
                this.statusTextElement.textContent = this.steps[this.currentStep];
                this.currentStep++;
            } else {
                this.stop();
            }
        }, this.interval);
    }

    stop() {
        if (this.stepInterval) {
            clearInterval(this.stepInterval);
            this.stepInterval = null;
        }
    }
};