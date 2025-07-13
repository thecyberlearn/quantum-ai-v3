# Agent Polling System Guide

This document explains how to use the reusable polling system for NetCop AI agents.

## Overview

The agent polling system provides a standardized way to handle asynchronous requests in agent templates, with proper cleanup, error handling, and user feedback.

## Key Features

- **Automatic cleanup**: Prevents memory leaks and duplicate polling
- **Error handling**: Handles network errors and timeouts gracefully
- **Duplicate prevention**: Ensures results are displayed only once
- **Progressive feedback**: Shows status steps for better UX
- **Reusable utilities**: Common functions for wallet updates, toasts, etc.

## Basic Usage

### 1. Include the Script

Add to your agent template's `extra_css` block:

```html
{% block extra_js %}
<script src="{% static 'js/agent-polling.js' %}"></script>
<script>
// Your agent-specific code here
</script>
{% endblock %}
```

### 2. Set Up Polling

```javascript
// For agents that use async polling
function startPolling(requestId) {
    const poller = window.pollingManager.createPoller('myAgent', {
        requestId: requestId,
        statusUrl: `/agents/my-agent/status/${requestId}/`,
        maxPolls: 30,
        pollInterval: 1000,
        onComplete: (result) => {
            AgentUtils.resetUI({
                processingStatusId: 'processingStatus',
                processButtonId: 'processButton',
                resultsId: 'results',
                buttonText: '🔄 Generate Again (5.00 AED)'
            });
            displayResults(result);
        },
        onError: (error) => {
            AgentUtils.resetUI({
                processingStatusId: 'processingStatus',
                processButtonId: 'processButton',
                buttonText: '🔄 Try Again (5.00 AED)'
            });
            AgentUtils.showToast('❌ Network error - please try again', 'error');
        },
        onTimeout: () => {
            AgentUtils.resetUI({
                processingStatusId: 'processingStatus',
                processButtonId: 'processButton',
                buttonText: '🔄 Try Again (5.00 AED)'
            });
            AgentUtils.showToast('❌ Processing timeout - please try again', 'error');
        }
    });
    
    poller.start();
}
```

### 3. Handle Form Submission

```javascript
document.getElementById('myForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Validation
    if (!isFormValid()) {
        AgentUtils.showToast('Please fill in all required fields', 'error');
        return;
    }
    
    // Authentication check
    if (!isAuthenticated) {
        window.location.href = loginUrl;
        return;
    }
    
    // Balance check
    if (userBalance < requiredAmount) {
        AgentUtils.showToast(`Insufficient balance! You need ${requiredAmount} AED.`, 'error');
        setTimeout(() => window.location.href = walletUrl, 2000);
        return;
    }
    
    // Clear any existing polling
    window.pollingManager.stopAll();
    
    // Show processing status
    AgentUtils.showProcessing({
        processingStatusId: 'processingStatus',
        processButtonId: 'processButton',
        resultsId: 'results',
        processingText: '⏳ Processing...'
    });
    
    // Start status steps
    const stepper = new StatusStepper([
        'Analyzing request...',
        'Processing data...',
        'Generating results...',
        'Finalizing output...'
    ], 'statusText');
    stepper.start();
    
    // Submit form
    const formData = new FormData(this);
    
    fetch(submitUrl, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(result => {
        stepper.stop();
        
        if (result.success && result.request_id) {
            // Start polling for async agents
            startPolling(result.request_id);
        } else {
            // Handle immediate response
            AgentUtils.resetUI({
                processingStatusId: 'processingStatus',
                processButtonId: 'processButton',
                buttonText: '🔄 Try Again (5.00 AED)'
            });
            
            if (result.error) {
                AgentUtils.showToast(`❌ ${result.error}`, 'error');
            } else {
                displayResults(result);
            }
        }
    })
    .catch(error => {
        stepper.stop();
        AgentUtils.resetUI({
            processingStatusId: 'processingStatus',
            processButtonId: 'processButton',
            buttonText: '🔄 Try Again (5.00 AED)'
        });
        AgentUtils.showToast('❌ Network error - please try again', 'error');
    });
});
```

### 4. Reset Function

```javascript
function resetForm() {
    // Stop all polling
    window.pollingManager.stopAll();
    
    // Reset form
    document.getElementById('myForm').reset();
    
    // Reset UI
    AgentUtils.resetUI({
        processingStatusId: 'processingStatus',
        processButtonId: 'processButton',
        resultsId: 'results',
        buttonText: '🚀 Generate (5.00 AED)'
    });
    
    AgentUtils.showToast('Form reset! Ready for another request.', 'success');
}
```

## API Reference

### AgentPoller Class

```javascript
const poller = new AgentPoller({
    requestId: 'string',      // Request ID to poll
    statusUrl: 'string',      // Status endpoint URL
    maxPolls: 30,             // Maximum poll attempts
    pollInterval: 1000,       // Poll interval in ms
    onComplete: function(result) {},  // Success callback
    onError: function(error) {},      // Error callback
    onTimeout: function() {}          // Timeout callback
});
```

### PollingManager

```javascript
// Create and start a poller
const poller = window.pollingManager.createPoller('pollerId', config);
poller.start();

// Stop specific poller
window.pollingManager.stopPoller('pollerId');

// Stop all pollers
window.pollingManager.stopAll();
```

### AgentUtils

```javascript
// Update wallet balance
AgentUtils.updateWalletBalance(150.00);

// Reset UI elements
AgentUtils.resetUI({
    processingStatusId: 'processingStatus',
    processButtonId: 'processButton',
    resultsId: 'results',
    buttonText: 'Process Again'
});

// Show processing state
AgentUtils.showProcessing({
    processingStatusId: 'processingStatus',
    processButtonId: 'processButton',
    resultsId: 'results',
    processingText: '⏳ Working...'
});

// Show toast notification
AgentUtils.showToast('Success message', 'success');
AgentUtils.showToast('Error message', 'error');
```

### StatusStepper

```javascript
const stepper = new StatusStepper([
    'Step 1...',
    'Step 2...',
    'Step 3...'
], 'statusTextElementId', 800); // 800ms interval

stepper.start();
stepper.stop();
```

## Migration Guide

### Converting Existing Agents

1. **Include the script** in your template
2. **Replace polling logic** with `AgentPoller`
3. **Use `AgentUtils`** for common operations
4. **Add proper cleanup** in reset functions
5. **Use `StatusStepper`** for better UX

### Before (old way):

```javascript
// Old polling code with potential issues
let pollInterval = setInterval(() => {
    fetch(statusUrl)
        .then(response => response.json())
        .then(result => {
            if (result.status === 'completed') {
                clearInterval(pollInterval);
                displayResults(result);
            }
        });
}, 1000);
```

### After (new way):

```javascript
// New robust polling
const poller = window.pollingManager.createPoller('agent', {
    requestId: requestId,
    statusUrl: statusUrl,
    onComplete: displayResults,
    onError: handleError,
    onTimeout: handleTimeout
});
poller.start();
```

## Best Practices

1. **Always stop existing polling** before starting new requests
2. **Use unique poller IDs** for different agents/features
3. **Provide clear error messages** to users
4. **Set appropriate timeouts** based on expected processing time
5. **Clean up resources** in reset functions
6. **Use progressive status steps** for better UX
7. **Prevent duplicate submissions** with proper state management

## Troubleshooting

### Common Issues

1. **Multiple polling instances**: Use `pollingManager.stopAll()` before starting new requests
2. **Memory leaks**: Always call `stop()` or use the manager's cleanup methods
3. **Duplicate results**: The system prevents this automatically
4. **Network errors**: Handled automatically with proper user feedback

### Debug Mode

Enable debug logging:

```javascript
// In development
window.agentPollingDebug = true;
```

This will log polling activities to the console for debugging.