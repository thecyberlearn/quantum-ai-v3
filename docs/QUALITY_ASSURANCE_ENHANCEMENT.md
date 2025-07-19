# Quality Assurance Enhancement

Comprehensive tools and processes to ensure high-quality template implementations.

## Overview

This document provides automated validation tools, manual review processes, and quality control measures to prevent implementation failures and ensure consistent, high-quality results.

## Automated Validation Tools

### 1. Template Structure Validator

**Purpose**: Automatically validate template structure consistency and completeness.

**Validation Script:**
```bash
#!/bin/bash
# Template Structure Validator
# Usage: ./validate_template.sh <template_file>

TEMPLATE_FILE="$1"
VALIDATION_REPORT="validation_report_$(date +%Y%m%d_%H%M%S).md"

echo "# Template Structure Validation Report" > "$VALIDATION_REPORT"
echo "**Template**: $TEMPLATE_FILE" >> "$VALIDATION_REPORT"
echo "**Date**: $(date)" >> "$VALIDATION_REPORT"
echo "**Validator**: Template Structure Validator v1.0" >> "$VALIDATION_REPORT"
echo "" >> "$VALIDATION_REPORT"

# Check Django template structure
echo "## Django Template Structure" >> "$VALIDATION_REPORT"
echo "### Base Template Extension" >> "$VALIDATION_REPORT"
if grep -q "{% extends 'base.html' %}" "$TEMPLATE_FILE"; then
    echo "✅ Base template extension found" >> "$VALIDATION_REPORT"
else
    echo "❌ Base template extension missing" >> "$VALIDATION_REPORT"
fi

if grep -q "{% load static %}" "$TEMPLATE_FILE"; then
    echo "✅ Static files loading found" >> "$VALIDATION_REPORT"
else
    echo "❌ Static files loading missing" >> "$VALIDATION_REPORT"
fi

# Check required blocks
echo "### Required Blocks" >> "$VALIDATION_REPORT"
required_blocks=("title" "extra_css" "content" "extra_js")
for block in "${required_blocks[@]}"; do
    if grep -q "{% block $block %}" "$TEMPLATE_FILE"; then
        echo "✅ Block '$block' found" >> "$VALIDATION_REPORT"
    else
        echo "❌ Block '$block' missing" >> "$VALIDATION_REPORT"
    fi
done

# Check HTML structure
echo "### HTML Structure" >> "$VALIDATION_REPORT"
required_elements=("agent-container" "agent-header" "agent-grid" "agent-widget")
for element in "${required_elements[@]}"; do
    if grep -q "class=\"[^\"]*$element[^\"]*\"" "$TEMPLATE_FILE"; then
        echo "✅ Element '$element' found" >> "$VALIDATION_REPORT"
    else
        echo "❌ Element '$element' missing" >> "$VALIDATION_REPORT"
    fi
done

# Check CSS custom properties
echo "### CSS Custom Properties" >> "$VALIDATION_REPORT"
css_vars=("--primary" "--surface" "--spacing-lg" "--radius-md" "--shadow-sm")
for var in "${css_vars[@]}"; do
    if grep -q "$var" "$TEMPLATE_FILE"; then
        echo "✅ CSS variable '$var' found" >> "$VALIDATION_REPORT"
    else
        echo "❌ CSS variable '$var' missing" >> "$VALIDATION_REPORT"
    fi
done

# Check JavaScript functions
echo "### JavaScript Functions" >> "$VALIDATION_REPORT"
js_functions=("updateWalletBalance" "showToast" "copyToClipboard" "downloadAsFile")
for func in "${js_functions[@]}"; do
    if grep -q "$func" "$TEMPLATE_FILE"; then
        echo "✅ JavaScript function '$func' found" >> "$VALIDATION_REPORT"
    else
        echo "❌ JavaScript function '$func' missing" >> "$VALIDATION_REPORT"
    fi
done

# Check security measures
echo "### Security Measures" >> "$VALIDATION_REPORT"
if grep -q "{% csrf_token %}" "$TEMPLATE_FILE"; then
    echo "✅ CSRF token found" >> "$VALIDATION_REPORT"
else
    echo "❌ CSRF token missing" >> "$VALIDATION_REPORT"
fi

if grep -q "safeSetHTML\|HTMLSanitizer" "$TEMPLATE_FILE"; then
    echo "✅ HTML sanitization found" >> "$VALIDATION_REPORT"
else
    echo "❌ HTML sanitization missing" >> "$VALIDATION_REPORT"
fi

# Check accessibility
echo "### Accessibility" >> "$VALIDATION_REPORT"
if grep -q "aria-" "$TEMPLATE_FILE"; then
    echo "✅ ARIA attributes found" >> "$VALIDATION_REPORT"
else
    echo "❌ ARIA attributes missing" >> "$VALIDATION_REPORT"
fi

if grep -q "role=" "$TEMPLATE_FILE"; then
    echo "✅ Role attributes found" >> "$VALIDATION_REPORT"
else
    echo "❌ Role attributes missing" >> "$VALIDATION_REPORT"
fi

# Generate summary
echo "## Validation Summary" >> "$VALIDATION_REPORT"
passed=$(grep -c "✅" "$VALIDATION_REPORT")
failed=$(grep -c "❌" "$VALIDATION_REPORT")
total=$((passed + failed))

echo "**Total Checks**: $total" >> "$VALIDATION_REPORT"
echo "**Passed**: $passed" >> "$VALIDATION_REPORT"
echo "**Failed**: $failed" >> "$VALIDATION_REPORT"
echo "**Success Rate**: $(( passed * 100 / total ))%" >> "$VALIDATION_REPORT"

if [ $failed -eq 0 ]; then
    echo "**Overall Status**: ✅ PASS" >> "$VALIDATION_REPORT"
else
    echo "**Overall Status**: ❌ FAIL" >> "$VALIDATION_REPORT"
fi

echo "Validation report generated: $VALIDATION_REPORT"
```

### 2. CSS Class Auditor

**Purpose**: Verify CSS class usage and consistency across templates.

**Auditor Script:**
```bash
#!/bin/bash
# CSS Class Auditor
# Usage: ./audit_css_classes.sh <template_file> <reference_file>

TEMPLATE_FILE="$1"
REFERENCE_FILE="$2"
AUDIT_REPORT="css_audit_$(date +%Y%m%d_%H%M%S).md"

echo "# CSS Class Audit Report" > "$AUDIT_REPORT"
echo "**Template**: $TEMPLATE_FILE" >> "$AUDIT_REPORT"
echo "**Reference**: $REFERENCE_FILE" >> "$AUDIT_REPORT"
echo "**Date**: $(date)" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# Extract CSS classes from both files
echo "## CSS Class Analysis" >> "$AUDIT_REPORT"

# Get classes from template
grep -oE 'class="[^"]*"' "$TEMPLATE_FILE" | sed 's/class="//g' | sed 's/"//g' | tr ' ' '\n' | sort | uniq > template_classes.tmp

# Get classes from reference
grep -oE 'class="[^"]*"' "$REFERENCE_FILE" | sed 's/class="//g' | sed 's/"//g' | tr ' ' '\n' | sort | uniq > reference_classes.tmp

# Compare classes
echo "### Classes in Reference but Missing in Template" >> "$AUDIT_REPORT"
comm -23 reference_classes.tmp template_classes.tmp | while read class; do
    echo "❌ Missing class: \`$class\`" >> "$AUDIT_REPORT"
done

echo "### Classes in Template but Not in Reference" >> "$AUDIT_REPORT"
comm -13 reference_classes.tmp template_classes.tmp | while read class; do
    echo "⚠️  Extra class: \`$class\`" >> "$AUDIT_REPORT"
done

echo "### Common Classes" >> "$AUDIT_REPORT"
comm -12 reference_classes.tmp template_classes.tmp | while read class; do
    echo "✅ Common class: \`$class\`" >> "$AUDIT_REPORT"
done

# Clean up
rm template_classes.tmp reference_classes.tmp

echo "CSS class audit report generated: $AUDIT_REPORT"
```

### 3. JavaScript Function Checker

**Purpose**: Verify JavaScript function equivalence and behavior.

**Checker Script:**
```bash
#!/bin/bash
# JavaScript Function Checker
# Usage: ./check_js_functions.sh <template_file> <reference_file>

TEMPLATE_FILE="$1"
REFERENCE_FILE="$2"
JS_REPORT="js_function_report_$(date +%Y%m%d_%H%M%S).md"

echo "# JavaScript Function Analysis Report" > "$JS_REPORT"
echo "**Template**: $TEMPLATE_FILE" >> "$JS_REPORT"
echo "**Reference**: $REFERENCE_FILE" >> "$JS_REPORT"
echo "**Date**: $(date)" >> "$JS_REPORT"
echo "" >> "$JS_REPORT"

# Extract function names
echo "## Function Analysis" >> "$JS_REPORT"

# Get functions from template
grep -oE 'function [a-zA-Z_][a-zA-Z0-9_]*' "$TEMPLATE_FILE" | sed 's/function //g' | sort | uniq > template_functions.tmp

# Get functions from reference
grep -oE 'function [a-zA-Z_][a-zA-Z0-9_]*' "$REFERENCE_FILE" | sed 's/function //g' | sort | uniq > reference_functions.tmp

# Compare functions
echo "### Functions in Reference but Missing in Template" >> "$JS_REPORT"
comm -23 reference_functions.tmp template_functions.tmp | while read func; do
    echo "❌ Missing function: \`$func\`" >> "$JS_REPORT"
done

echo "### Functions in Template but Not in Reference" >> "$JS_REPORT"
comm -13 reference_functions.tmp template_functions.tmp | while read func; do
    echo "⚠️  Extra function: \`$func\`" >> "$JS_REPORT"
done

echo "### Common Functions" >> "$JS_REPORT"
comm -12 reference_functions.tmp template_functions.tmp | while read func; do
    echo "✅ Common function: \`$func\`" >> "$JS_REPORT"
done

# Check for essential functions
echo "### Essential Function Check" >> "$JS_REPORT"
essential_functions=("updateWalletBalance" "showToast" "copyToClipboard" "downloadAsFile" "resetUI")
for func in "${essential_functions[@]}"; do
    if grep -q "$func" "$TEMPLATE_FILE"; then
        echo "✅ Essential function '$func' found" >> "$JS_REPORT"
    else
        echo "❌ Essential function '$func' missing" >> "$JS_REPORT"
    fi
done

# Clean up
rm template_functions.tmp reference_functions.tmp

echo "JavaScript function analysis report generated: $JS_REPORT"
```

### 4. Accessibility Compliance Checker

**Purpose**: Validate accessibility standards and ARIA attributes.

**Accessibility Checker:**
```bash
#!/bin/bash
# Accessibility Compliance Checker
# Usage: ./check_accessibility.sh <template_file>

TEMPLATE_FILE="$1"
A11Y_REPORT="accessibility_report_$(date +%Y%m%d_%H%M%S).md"

echo "# Accessibility Compliance Report" > "$A11Y_REPORT"
echo "**Template**: $TEMPLATE_FILE" >> "$A11Y_REPORT"
echo "**Date**: $(date)" >> "$A11Y_REPORT"
echo "" >> "$A11Y_REPORT"

# Check ARIA attributes
echo "## ARIA Attributes" >> "$A11Y_REPORT"
aria_attributes=("aria-label" "aria-labelledby" "aria-describedby" "aria-expanded" "aria-hidden" "aria-live" "role")
for attr in "${aria_attributes[@]}"; do
    if grep -q "$attr=" "$TEMPLATE_FILE"; then
        count=$(grep -c "$attr=" "$TEMPLATE_FILE")
        echo "✅ $attr found ($count occurrences)" >> "$A11Y_REPORT"
    else
        echo "❌ $attr missing" >> "$A11Y_REPORT"
    fi
done

# Check form accessibility
echo "## Form Accessibility" >> "$A11Y_REPORT"
if grep -q "<label" "$TEMPLATE_FILE"; then
    echo "✅ Form labels found" >> "$A11Y_REPORT"
else
    echo "❌ Form labels missing" >> "$A11Y_REPORT"
fi

if grep -q "for=" "$TEMPLATE_FILE"; then
    echo "✅ Label associations found" >> "$A11Y_REPORT"
else
    echo "❌ Label associations missing" >> "$A11Y_REPORT"
fi

# Check heading structure
echo "## Heading Structure" >> "$A11Y_REPORT"
for i in {1..6}; do
    if grep -q "<h$i" "$TEMPLATE_FILE"; then
        count=$(grep -c "<h$i" "$TEMPLATE_FILE")
        echo "✅ H$i headings found ($count occurrences)" >> "$A11Y_REPORT"
    else
        echo "ℹ️  H$i headings not found" >> "$A11Y_REPORT"
    fi
done

# Check alt text for images
echo "## Image Accessibility" >> "$A11Y_REPORT"
if grep -q "<img" "$TEMPLATE_FILE"; then
    if grep -q "alt=" "$TEMPLATE_FILE"; then
        echo "✅ Image alt text found" >> "$A11Y_REPORT"
    else
        echo "❌ Image alt text missing" >> "$A11Y_REPORT"
    fi
else
    echo "ℹ️  No images found" >> "$A11Y_REPORT"
fi

# Check focus management
echo "## Focus Management" >> "$A11Y_REPORT"
if grep -q "focus()" "$TEMPLATE_FILE"; then
    echo "✅ Focus management found" >> "$A11Y_REPORT"
else
    echo "❌ Focus management missing" >> "$A11Y_REPORT"
fi

# Check keyboard navigation
echo "## Keyboard Navigation" >> "$A11Y_REPORT"
if grep -q "keydown\|keyup\|keypress" "$TEMPLATE_FILE"; then
    echo "✅ Keyboard event handling found" >> "$A11Y_REPORT"
else
    echo "❌ Keyboard event handling missing" >> "$A11Y_REPORT"
fi

echo "Accessibility compliance report generated: $A11Y_REPORT"
```

## Manual Review Processes

### 1. Pixel-Perfect Visual Comparison

**Visual Comparison Checklist:**
```markdown
# Visual Comparison Checklist

## Layout Structure
- [ ] Header layout matches exactly
- [ ] Main content area positioning correct
- [ ] Sidebar placement accurate
- [ ] Footer alignment proper
- [ ] Overall grid structure identical

## Typography
- [ ] Font families match
- [ ] Font sizes identical
- [ ] Font weights correct
- [ ] Line heights consistent
- [ ] Letter spacing accurate

## Color Scheme
- [ ] Primary colors match
- [ ] Secondary colors accurate
- [ ] Background colors correct
- [ ] Text colors identical
- [ ] Accent colors consistent

## Spacing and Padding
- [ ] Margin values match
- [ ] Padding values identical
- [ ] Gap sizes consistent
- [ ] Border spacing accurate
- [ ] Element spacing proper

## Visual Effects
- [ ] Shadows match exactly
- [ ] Border radius identical
- [ ] Gradients accurate
- [ ] Hover effects consistent
- [ ] Transition timing correct

## Responsive Design
- [ ] Mobile layout matches
- [ ] Tablet layout accurate
- [ ] Desktop layout identical
- [ ] Breakpoint behavior consistent
- [ ] Scaling behavior proper
```

### 2. Interaction Testing Protocol

**Interaction Testing Checklist:**
```markdown
# Interaction Testing Checklist

## Click Interactions
- [ ] All buttons respond to clicks
- [ ] Click areas are appropriate size
- [ ] Click feedback is immediate
- [ ] Double-click prevention works
- [ ] Context menus work correctly

## Form Interactions
- [ ] Input fields accept text
- [ ] Validation works correctly
- [ ] Submit buttons function
- [ ] Reset buttons clear forms
- [ ] Error messages display properly

## Navigation Interactions
- [ ] Menu items work correctly
- [ ] Breadcrumbs function properly
- [ ] Back/forward buttons work
- [ ] Internal links navigate correctly
- [ ] External links open properly

## Keyboard Navigation
- [ ] Tab order is logical
- [ ] Enter key activates buttons
- [ ] Escape key closes modals
- [ ] Arrow keys work for navigation
- [ ] Shortcuts function correctly

## Mouse Interactions
- [ ] Hover effects work
- [ ] Click states are visual
- [ ] Drag and drop functions
- [ ] Scroll behaviors work
- [ ] Context menus appear

## Touch Interactions
- [ ] Tap targets are large enough
- [ ] Swipe gestures work
- [ ] Pinch zoom functions
- [ ] Touch feedback is immediate
- [ ] Touch scrolling is smooth
```

### 3. Performance Validation Process

**Performance Validation Checklist:**
```markdown
# Performance Validation Checklist

## Loading Performance
- [ ] Page load time under 3 seconds
- [ ] First contentful paint under 1.5 seconds
- [ ] Time to interactive under 2.5 seconds
- [ ] Cumulative layout shift under 0.1
- [ ] Resource loading optimized

## Runtime Performance
- [ ] Smooth scrolling (60fps)
- [ ] Animations run smoothly
- [ ] No memory leaks detected
- [ ] CPU usage reasonable
- [ ] Network requests optimized

## Resource Usage
- [ ] Image sizes optimized
- [ ] CSS file size reasonable
- [ ] JavaScript file size optimized
- [ ] Font loading efficient
- [ ] Third-party resources minimal

## Caching Performance
- [ ] Browser caching configured
- [ ] CDN caching working
- [ ] API response caching
- [ ] Static asset caching
- [ ] Database query optimization

## Mobile Performance
- [ ] Mobile load time acceptable
- [ ] Touch response immediate
- [ ] Scroll performance smooth
- [ ] Battery usage reasonable
- [ ] Data usage optimized
```

### 4. Cross-Browser Compatibility Testing

**Browser Compatibility Matrix:**
```markdown
# Browser Compatibility Testing Matrix

## Desktop Browsers
| Feature | Chrome | Firefox | Safari | Edge | Status |
|---------|---------|---------|---------|---------|---------|
| Layout | [ ] | [ ] | [ ] | [ ] | [ ] |
| Styling | [ ] | [ ] | [ ] | [ ] | [ ] |
| JavaScript | [ ] | [ ] | [ ] | [ ] | [ ] |
| Interactions | [ ] | [ ] | [ ] | [ ] | [ ] |
| Performance | [ ] | [ ] | [ ] | [ ] | [ ] |

## Mobile Browsers
| Feature | Chrome Mobile | Safari Mobile | Firefox Mobile | Samsung Browser | Status |
|---------|---------|---------|---------|---------|---------|
| Layout | [ ] | [ ] | [ ] | [ ] | [ ] |
| Styling | [ ] | [ ] | [ ] | [ ] | [ ] |
| JavaScript | [ ] | [ ] | [ ] | [ ] | [ ] |
| Interactions | [ ] | [ ] | [ ] | [ ] | [ ] |
| Performance | [ ] | [ ] | [ ] | [ ] | [ ] |

## Compatibility Issues
- [ ] CSS Grid support verified
- [ ] Flexbox compatibility confirmed
- [ ] ES6 features working
- [ ] CSS Custom Properties supported
- [ ] Modern JavaScript APIs available

## Fallback Mechanisms
- [ ] Graceful degradation implemented
- [ ] Progressive enhancement working
- [ ] Polyfills loaded when needed
- [ ] Fallback styles provided
- [ ] Error handling for unsupported features
```

## Quality Control Measures

### 1. Code Quality Standards

**Code Quality Checklist:**
```markdown
# Code Quality Standards Checklist

## HTML Quality
- [ ] Valid HTML5 markup
- [ ] Semantic HTML elements used
- [ ] Proper nesting structure
- [ ] Accessibility attributes included
- [ ] SEO meta tags present

## CSS Quality
- [ ] Valid CSS3 syntax
- [ ] Consistent naming conventions
- [ ] Modular CSS architecture
- [ ] Responsive design principles
- [ ] Performance optimizations

## JavaScript Quality
- [ ] Valid JavaScript syntax
- [ ] Consistent coding style
- [ ] Proper error handling
- [ ] Memory leak prevention
- [ ] Security best practices

## Django Template Quality
- [ ] Proper template inheritance
- [ ] Correct template tag usage
- [ ] CSRF protection implemented
- [ ] XSS prevention measures
- [ ] Template variable escaping
```

### 2. Security Validation

**Security Validation Checklist:**
```markdown
# Security Validation Checklist

## Input Validation
- [ ] All user inputs validated
- [ ] XSS prevention implemented
- [ ] SQL injection prevention
- [ ] File upload security
- [ ] Input sanitization active

## Output Sanitization
- [ ] HTML output sanitized
- [ ] JavaScript output escaped
- [ ] CSS output cleaned
- [ ] JSON output validated
- [ ] XML output sanitized

## Authentication Security
- [ ] CSRF tokens present
- [ ] Session management secure
- [ ] Password security enforced
- [ ] Access control implemented
- [ ] Rate limiting active

## Data Protection
- [ ] Sensitive data encrypted
- [ ] Secure data transmission
- [ ] Data validation implemented
- [ ] Error message sanitization
- [ ] Logging security measures
```

### 3. Performance Benchmarks

**Performance Benchmark Standards:**
```markdown
# Performance Benchmark Standards

## Loading Performance Targets
- **Page Load Time**: < 3 seconds
- **First Contentful Paint**: < 1.5 seconds
- **Time to Interactive**: < 2.5 seconds
- **Cumulative Layout Shift**: < 0.1
- **First Input Delay**: < 100ms

## Runtime Performance Targets
- **Animation Frame Rate**: 60fps
- **Scroll Performance**: Smooth scrolling
- **Memory Usage**: < 50MB
- **CPU Usage**: < 20%
- **Network Requests**: < 10 initial requests

## Resource Size Targets
- **HTML Size**: < 50KB
- **CSS Size**: < 100KB
- **JavaScript Size**: < 200KB
- **Image Total Size**: < 1MB
- **Total Page Size**: < 2MB

## Mobile Performance Targets
- **Mobile Load Time**: < 4 seconds
- **Touch Response**: < 50ms
- **Battery Usage**: Minimal impact
- **Data Usage**: < 1MB initial load
- **Offline Capability**: Basic functionality
```

## Automated Testing Integration

### 1. Continuous Integration Pipeline

**CI/CD Pipeline Configuration:**
```yaml
# .github/workflows/template-validation.yml
name: Template Validation

on:
  push:
    paths:
      - '*/templates/**/*.html'
  pull_request:
    paths:
      - '*/templates/**/*.html'

jobs:
  validate-templates:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install beautifulsoup4 lxml
          npm install -g html-validate
      
      - name: Validate HTML structure
        run: |
          for file in $(find . -name "*.html" -path "*/templates/*"); do
            echo "Validating $file"
            html-validate "$file"
          done
      
      - name: Check template structure
        run: |
          python scripts/validate_template_structure.py
      
      - name: Run accessibility tests
        run: |
          python scripts/check_accessibility.py
      
      - name: Generate validation report
        run: |
          python scripts/generate_validation_report.py
```

### 2. Automated Testing Scripts

**Template Validation Script:**
```python
#!/usr/bin/env python3
"""
Template Structure Validation Script
Validates Django templates for structural consistency
"""

import os
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

class TemplateValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate_template(self, template_path):
        """Validate a single template file"""
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check Django template structure
        self._check_django_structure(content, template_path)
        
        # Check HTML structure
        self._check_html_structure(content, template_path)
        
        # Check CSS classes
        self._check_css_classes(content, template_path)
        
        # Check JavaScript functions
        self._check_javascript_functions(content, template_path)
        
        # Check accessibility
        self._check_accessibility(content, template_path)
        
        # Check security
        self._check_security(content, template_path)
    
    def _check_django_structure(self, content, template_path):
        """Check Django template structure"""
        if "{% extends 'base.html' %}" not in content:
            self.errors.append(f"{template_path}: Missing base template extension")
        
        if "{% load static %}" not in content:
            self.errors.append(f"{template_path}: Missing static files loading")
        
        required_blocks = ['title', 'extra_css', 'content', 'extra_js']
        for block in required_blocks:
            if f"{{% block {block} %}}" not in content:
                self.errors.append(f"{template_path}: Missing {block} block")
    
    def _check_html_structure(self, content, template_path):
        """Check HTML structure"""
        required_classes = ['agent-container', 'agent-header', 'agent-grid']
        for class_name in required_classes:
            if f'class="{class_name}"' not in content and f'class="[^"]*{class_name}[^"]*"' not in content:
                self.errors.append(f"{template_path}: Missing {class_name} class")
    
    def _check_css_classes(self, content, template_path):
        """Check CSS class usage"""
        # Extract all CSS classes
        css_classes = re.findall(r'class="([^"]*)"', content)
        
        # Check for standard classes
        standard_classes = ['btn', 'form-control', 'agent-widget']
        for class_name in standard_classes:
            if not any(class_name in class_list for class_list in css_classes):
                self.warnings.append(f"{template_path}: Standard class {class_name} not found")
    
    def _check_javascript_functions(self, content, template_path):
        """Check JavaScript functions"""
        required_functions = ['updateWalletBalance', 'showToast']
        for func in required_functions:
            if func not in content:
                self.errors.append(f"{template_path}: Missing {func} function")
    
    def _check_accessibility(self, content, template_path):
        """Check accessibility features"""
        if 'aria-' not in content:
            self.warnings.append(f"{template_path}: No ARIA attributes found")
        
        if 'role=' not in content:
            self.warnings.append(f"{template_path}: No role attributes found")
    
    def _check_security(self, content, template_path):
        """Check security measures"""
        if '{% csrf_token %}' not in content:
            self.errors.append(f"{template_path}: Missing CSRF token")
        
        if 'safeSetHTML' not in content and 'HTMLSanitizer' not in content:
            self.warnings.append(f"{template_path}: No HTML sanitization found")
    
    def generate_report(self):
        """Generate validation report"""
        report = f"""# Template Validation Report

## Summary
- **Total Errors**: {len(self.errors)}
- **Total Warnings**: {len(self.warnings)}

## Errors
"""
        for error in self.errors:
            report += f"- ❌ {error}\n"
        
        report += "\n## Warnings\n"
        for warning in self.warnings:
            report += f"- ⚠️ {warning}\n"
        
        return report

def main():
    validator = TemplateValidator()
    
    # Find all template files
    template_files = []
    for root, dirs, files in os.walk('.'):
        if 'templates' in root:
            for file in files:
                if file.endswith('.html'):
                    template_files.append(os.path.join(root, file))
    
    # Validate each template
    for template_file in template_files:
        validator.validate_template(template_file)
    
    # Generate and save report
    report = validator.generate_report()
    with open('template_validation_report.md', 'w') as f:
        f.write(report)
    
    print(f"Validation complete. Found {len(validator.errors)} errors and {len(validator.warnings)} warnings.")
    
    if validator.errors:
        sys.exit(1)

if __name__ == '__main__':
    main()
```

This comprehensive Quality Assurance Enhancement framework provides automated tools, manual processes, and quality control measures to ensure high-quality template implementations and prevent the issues that occurred with the Social Ads Generator initial implementation.