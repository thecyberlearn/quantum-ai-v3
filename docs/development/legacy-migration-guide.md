# Legacy Agent Migration Guide

## Overview

This guide explains how to properly convert legacy agent templates to the new Template Component Architecture without introducing technical debt or code bloat.

## ⚠️ The Legacy Contamination Problem

When converting legacy agents, the natural instinct is to copy existing working code. However, this leads to:

- **Template Bloat**: 1,000+ line templates instead of 300 lines
- **Duplicate Code**: Custom implementations instead of shared utilities
- **Maintenance Issues**: Multiple copies of the same functionality
- **Architecture Violations**: Inline code instead of component system

## ✅ Correct Migration Process

### Step 1: Analyze Legacy Functionality (Don't Copy Code!)

**DO**: List the functional requirements
```
- File upload for PDF files
- Radio button selection for analysis type
- Display analysis results with formatting
- Copy, download, reset functionality
```

**DON'T**: Copy the implementation code
```
❌ Never copy 500+ lines of inline JavaScript
❌ Never copy 400+ lines of custom CSS
❌ Never copy custom implementations of shared utilities
```

### Step 2: Map to Component Architecture

**Legacy Approach (Wrong)**:
```django
<!-- 100+ lines of custom header HTML -->
<!-- 200+ lines of custom form HTML -->
<!-- 300+ lines of custom JavaScript -->
<!-- 400+ lines of custom CSS -->
```

**Component Approach (Right)**:
```django
{% include "workflows/components/agent_header.html" %}
{% include "workflows/components/quick_agents_panel.html" %}
<!-- 50 lines of agent-specific form -->
{% include "workflows/components/processing_status.html" %}
{% include "workflows/components/results_container.html" %}
```

### Step 3: Use Agent Template Prototype as Reference

**Start with**: `agent_template_prototype.html` (perfect UI patterns)
**Not with**: Existing legacy agent template

The prototype shows exactly how components should work together.

### Step 4: Implement Only Agent-Specific Logic

**Keep from Legacy**:
- ✅ Business logic requirements
- ✅ Form field definitions
- ✅ Validation rules
- ✅ API integration patterns

**Replace with Components**:
- ❌ Header implementation → Use `agent_header.html`
- ❌ Navigation panel → Use `quick_agents_panel.html`
- ❌ Processing display → Use `processing_status.html`
- ❌ Results display → Use `results_container.html`
- ❌ Utility functions → Use `WorkflowsCore`

## 📊 Migration Results Comparison

| Aspect | Legacy Approach | Component Approach | Improvement |
|--------|----------------|-------------------|-------------|
| **Template Size** | 1,031 lines | 285 lines | 72% reduction |
| **CSS Lines** | 480+ lines | 145 lines | 70% reduction |
| **JavaScript** | 500+ inline | 150 external | 70% reduction |
| **Maintenance** | Individual updates | Shared component updates | Automatic |
| **Consistency** | Varies per agent | Identical across agents | Perfect |

## 🎯 Real Example: Data Analyzer Migration

### Before (Legacy Contamination)
```django
<!-- data_analyzer/templates/data_analyzer/detail.html - 928 lines -->
<script>
// 500+ lines of custom JavaScript duplicating WorkflowsCore
function copyResults() {
    // Custom implementation
}
function downloadResults() {
    // Custom implementation  
}
// ... hundreds more lines
</script>

<style>
/* 400+ lines of custom CSS duplicating agent-base.css */
.file-upload-area { /* custom styles */ }
.radio-card { /* custom styles */ }
/* ... hundreds more lines */
</style>
```

### After (Component Architecture)
```django
<!-- workflows/templates/workflows/data-analyzer.html - 285 lines -->
{% include "workflows/components/agent_header.html" %}
{% include "workflows/components/quick_agents_panel.html" %}

<!-- 50 lines of agent-specific form -->
<div class="form-group">
    <label>📁 Upload Data File</label>
    <input type="file" name="file" accept=".pdf">
</div>

{% include "workflows/components/processing_status.html" %}
{% include "workflows/components/results_container.html" %}
```

**Result**: 72% smaller, consistent UI, automatic utility functions.

## 🛡️ Prevention Guidelines

### For Developers
1. **Never start migration by reading legacy template code**
2. **Always start with `agent_template_prototype.html` for UI reference**
3. **Use component includes for all shared functionality**
4. **Write only agent-specific form fields and validation**

### For Code Reviews
1. **Reject any template over 500 lines**
2. **Reject any inline JavaScript over 100 lines**
3. **Reject any custom CSS over 200 lines**
4. **Require component include usage**

### Red Flags in Pull Requests
- ❌ `function copyResults()` - Should use `WorkflowsCore.copyResults()`
- ❌ `function downloadResults()` - Should use `WorkflowsCore.downloadResults()`
- ❌ Custom toast implementations - Should use `WorkflowsCore.showToast()`
- ❌ Custom processing displays - Should use `processing_status.html` component
- ❌ Custom header implementations - Should use `agent_header.html` component

## 📚 Additional Resources

- [Template Component Architecture](../CLAUDE.md#template-component-architecture)
- [Agent Template Prototype](../../agent_template_prototype.html)
- [WorkflowsCore Documentation](../../static/js/workflows-core.js)
- [4-Step Agent Creation Process](../CLAUDE.md#4-step-agent-creation-process)

## 🎯 Key Takeaway

**Legacy functionality should inspire new components, not contaminate them.** 

The goal is to preserve the user experience and business logic while completely replacing the implementation with clean, maintainable component architecture.