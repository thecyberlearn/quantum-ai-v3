/**
 * Data Analyzer Agent - Specific JavaScript
 * Uses WorkflowsCore for all shared functionality
 */

// Initialize data analyzer functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Data Analyzer loaded');
    
    // Initialize file upload
    const fileInput = document.getElementById('dataFile');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileChange);
    }
    
    // Initialize drag and drop
    const uploadArea = document.querySelector('.file-upload-area');
    if (uploadArea && fileInput) {
        WorkflowsCore.setupDragAndDrop(uploadArea, fileInput);
    }
    
    // Set initial radio selection
    const firstRadio = document.querySelector('.radio-card');
    if (firstRadio && !document.querySelector('.radio-card.selected')) {
        firstRadio.classList.add('selected');
        const input = firstRadio.querySelector('input[type="radio"]');
        if (input) input.checked = true;
    }
    
    // Handle form submission
    const form = document.getElementById('agentForm');
    if (form) {
        form.addEventListener('submit', handleFormSubmission);
    }
});

// Data Analyzer specific functions
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

function handleFileChange(event) {
    const file = event.target.files[0];
    const uploadArea = document.querySelector('.file-upload-area');
    const uploadText = document.querySelector('.upload-text');
    
    if (file) {
        uploadArea.classList.add('file-selected');
        uploadText.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 24px;">📄</span>
                <div>
                    <div style="font-weight: 500;">${file.name}</div>
                    <div style="font-size: 12px; color: var(--on-surface-variant);">${WorkflowsCore.formatFileSize(file.size)}</div>
                </div>
            </div>
        `;
        WorkflowsCore.showToast(`File selected: ${file.name}`, 'success');
    } else {
        uploadArea.classList.remove('file-selected');
        uploadText.innerHTML = `
            <div class="upload-icon">📁</div>
            <div><strong>Click to upload</strong> or drag and drop</div>
            <div>PDF files only</div>
        `;
    }
}

function handleFormSubmission(e) {
    e.preventDefault();
    
    // Validate form
    if (!isFormValid()) {
        return;
    }
    
    // Check authentication and balance using WorkflowsCore
    if (!WorkflowsCore.checkAuthentication()) {
        return;
    }
    
    const agentPrice = parseFloat(document.body.getAttribute('data-agent-price'));
    if (!WorkflowsCore.checkBalance(agentPrice)) {
        return;
    }
    
    // Show processing status
    WorkflowsCore.showProcessing('Analyzing Your Data...');
    
    // Submit form with AJAX
    const formData = new FormData(e.target);
    
    fetch(window.location.href, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.headers.get('content-type')?.includes('application/json')) {
            return response.json();
        } else {
            return response.text().then(html => {
                console.log('HTML response received');
                return { success: true, processing: true };
            });
        }
    })
    .then(result => {
        if (result.success && result.analysis_results) {
            // Handle JSON response with analysis data
            displayAnalysisResults(result.analysis_results);
            
            // Update wallet balance if provided
            if (result.wallet_balance !== undefined) {
                WorkflowsCore.updateWalletBalance(result.wallet_balance);
            }
            
        } else if (result.success && result.processing) {
            // Show processing message
            WorkflowsCore.showToast('🔄 Processing started successfully!', 'success');
            
            // Show unavailable message after timeout (since N8N integration may not be active)
            setTimeout(() => {
                WorkflowsCore.hideProcessing();
                WorkflowsCore.showToast('⚠️ Analysis service temporarily unavailable. Please try again later.', 'error');
            }, 30000); // 30 second timeout
            
        } else {
            WorkflowsCore.hideProcessing();
            WorkflowsCore.showToast(`❌ ${result.error || 'Processing failed'}`, 'error');
        }
    })
    .catch(error => {
        console.error('Form submission error:', error);
        WorkflowsCore.hideProcessing();
        WorkflowsCore.showToast('❌ Connection error. Please try again.', 'error');
    });
}

function displayAnalysisResults(analysisData) {
    WorkflowsCore.hideProcessing();
    
    let resultsHtml = '<h3>✅ Analysis Complete</h3>';
    
    if (analysisData.sections && analysisData.sections.length > 0) {
        resultsHtml += '<div class="analysis-sections">';
        
        analysisData.sections.forEach(section => {
            if (section.heading && section.content) {
                resultsHtml += `
                    <div style="background: var(--surface-variant); border-radius: var(--radius-md); padding: var(--spacing-lg); margin-bottom: var(--spacing-md); border-left: 4px solid var(--primary);">
                        <h4 style="color: var(--primary); font-weight: 600; margin: 0 0 var(--spacing-md) 0; font-size: 16px;">📋 ${section.heading}</h4>
                        <div style="color: var(--on-surface); line-height: 1.6; font-size: 14px;">${section.content.replace(/\n/g, '<br>')}</div>
                    </div>
                `;
            }
        });
        resultsHtml += '</div>';
    } else {
        resultsHtml += '<p>Analysis completed successfully. Your data has been processed.</p>';
    }
    
    if (analysisData.timestamp) {
        resultsHtml += `<p style="margin-top: var(--spacing-lg); text-align: center; color: var(--on-surface-variant);"><small>Analysis completed: ${new Date(analysisData.timestamp).toLocaleString()}</small></p>`;
    }
    
    WorkflowsCore.showResults(resultsHtml, 'Analysis Results');
    WorkflowsCore.showToast('✅ Data analysis completed successfully!', 'success');
}

function isFormValid() {
    const fileInput = document.getElementById('dataFile');
    const analysisType = document.querySelector('input[name="analysisType"]:checked');
    
    // Clear previous errors
    WorkflowsCore.clearFieldError('dataFile');
    WorkflowsCore.clearFieldError('analysisType');
    
    let isValid = true;
    
    if (!fileInput.files || fileInput.files.length === 0) {
        WorkflowsCore.showFieldError('dataFile', 'Please select a data file');
        WorkflowsCore.showToast('Please select a data file', 'error');
        isValid = false;
    }
    
    if (!analysisType) {
        WorkflowsCore.showFieldError('analysisType', 'Please select an analysis type');
        WorkflowsCore.showToast('Please select an analysis type', 'error');
        isValid = false;
    }
    
    return isValid;
}