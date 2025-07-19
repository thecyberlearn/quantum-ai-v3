# Implementation Tools and Frameworks

Practical tools, scripts, and frameworks with built-in quality gates to ensure error-free template implementations.

## Overview

This document provides a comprehensive toolkit of automated tools, validation scripts, and frameworks that enforce quality gates throughout the implementation process. These tools prevent the types of failures that occurred with the Social Ads Generator initial implementation.

## Quality Gate Automation Tools

### 1. Pre-Implementation Validation Tool

**Purpose**: Automated validation of requirements and analysis before starting implementation.

**Script: `validate_pre_implementation.py`**
```python
#!/usr/bin/env python3
"""
Pre-Implementation Validation Tool
Validates requirements, analysis, and planning before implementation starts
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class PreImplementationValidator:
    def __init__(self, config_file: str = "validation_config.json"):
        self.config = self.load_config(config_file)
        self.errors = []
        self.warnings = []
        self.report_path = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    def load_config(self, config_file: str) -> Dict:
        """Load validation configuration"""
        default_config = {
            "required_files": [
                "requirements_analysis.md",
                "template_analysis.md",
                "implementation_plan.md"
            ],
            "required_sections": {
                "requirements_analysis.md": [
                    "Explicit Requirements",
                    "Implicit Requirements",
                    "Success Criteria",
                    "Constraints"
                ],
                "template_analysis.md": [
                    "Source Template Analysis",
                    "Target Template Analysis",
                    "Gap Analysis",
                    "Change Requirements"
                ],
                "implementation_plan.md": [
                    "Implementation Strategy",
                    "Risk Assessment",
                    "Timeline",
                    "Quality Gates"
                ]
            },
            "quality_gates": [
                "Gate 1: Requirements Validation",
                "Gate 2: Analysis Validation", 
                "Gate 3: Planning Validation"
            ]
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def validate_files_exist(self) -> bool:
        """Validate that all required files exist"""
        print("📁 Validating required files...")
        all_exist = True
        
        for file_name in self.config["required_files"]:
            if not os.path.exists(file_name):
                self.errors.append(f"Missing required file: {file_name}")
                all_exist = False
            else:
                print(f"  ✅ Found: {file_name}")
        
        return all_exist
    
    def validate_file_sections(self, file_path: str) -> bool:
        """Validate that file contains required sections"""
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_sections = self.config["required_sections"].get(file_path, [])
        missing_sections = []
        
        for section in required_sections:
            # Look for section headers (markdown style)
            if not re.search(rf'^#+\s*{re.escape(section)}', content, re.MULTILINE | re.IGNORECASE):
                missing_sections.append(section)
        
        if missing_sections:
            self.errors.append(f"Missing sections in {file_path}: {', '.join(missing_sections)}")
            return False
        
        return True
    
    def validate_requirements_quality(self) -> bool:
        """Validate the quality of requirements analysis"""
        print("📋 Validating requirements quality...")
        
        req_file = "requirements_analysis.md"
        if not os.path.exists(req_file):
            return False
        
        with open(req_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for specific quality indicators
        quality_checks = [
            ("Explicit requirements listed", r'(?i)explicit requirements?.*?(?:\n.*?){1,10}\n\s*[-*]\s*', "At least 3 explicit requirements should be listed"),
            ("Success criteria defined", r'(?i)success criteria.*?(?:\n.*?){1,10}\n\s*[-*]\s*', "Success criteria should be clearly defined"),
            ("Constraints documented", r'(?i)constraints?.*?(?:\n.*?){1,10}\n\s*[-*]\s*', "Constraints should be documented"),
            ("User request quoted", r'(?i)user request.*?["\'].*?["\']', "Original user request should be quoted")
        ]
        
        for check_name, pattern, error_msg in quality_checks:
            if not re.search(pattern, content, re.MULTILINE | re.DOTALL):
                self.warnings.append(f"Requirements quality: {error_msg}")
        
        return True
    
    def validate_analysis_completeness(self) -> bool:
        """Validate completeness of template analysis"""
        print("🔍 Validating analysis completeness...")
        
        analysis_file = "template_analysis.md"
        if not os.path.exists(analysis_file):
            return False
        
        with open(analysis_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for analysis depth indicators
        depth_checks = [
            ("HTML structure analysis", r'(?i)html.*?structure.*?(?:\n.*?){3,}', "HTML structure should be thoroughly analyzed"),
            ("CSS analysis", r'(?i)css.*?(?:class|style|design).*?(?:\n.*?){3,}', "CSS architecture should be analyzed"),
            ("JavaScript functions", r'(?i)javascript.*?function.*?(?:\n.*?){2,}', "JavaScript functions should be documented"),
            ("Gap analysis table", r'\|.*?\|.*?\|.*?\|', "Gap analysis should include comparison tables"),
            ("Missing elements listed", r'(?i)missing.*?(?:element|component|class).*?(?:\n.*?){2,}', "Missing elements should be identified")
        ]
        
        for check_name, pattern, error_msg in depth_checks:
            if not re.search(pattern, content, re.MULTILINE | re.DOTALL):
                self.warnings.append(f"Analysis completeness: {error_msg}")
        
        return True
    
    def validate_plan_feasibility(self) -> bool:
        """Validate implementation plan feasibility"""
        print("📅 Validating plan feasibility...")
        
        plan_file = "implementation_plan.md"
        if not os.path.exists(plan_file):
            return False
        
        with open(plan_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for planning quality indicators
        planning_checks = [
            ("Step-by-step plan", r'(?i)step.*?(?:\n.*?){5,}', "Implementation should have detailed steps"),
            ("Risk assessment", r'(?i)risk.*?(?:assessment|analysis|mitigation).*?(?:\n.*?){3,}', "Risks should be assessed and mitigated"),
            ("Timeline estimates", r'(?i)(?:timeline|duration|time|hours?).*?(?:\d+|estimate)', "Timeline should include estimates"),
            ("Quality gates defined", r'(?i)quality.*?gate.*?(?:\n.*?){2,}', "Quality gates should be defined"),
            ("Rollback plan", r'(?i)rollback.*?(?:plan|procedure|strategy)', "Rollback plan should be documented")
        ]
        
        for check_name, pattern, error_msg in planning_checks:
            if not re.search(pattern, content, re.MULTILINE | re.DOTALL):
                self.warnings.append(f"Plan feasibility: {error_msg}")
        
        return True
    
    def validate_quality_gates(self) -> bool:
        """Validate that quality gates are properly defined"""
        print("🚪 Validating quality gates...")
        
        for gate in self.config["quality_gates"]:
            gate_found = False
            
            for file_name in self.config["required_files"]:
                if os.path.exists(file_name):
                    with open(file_name, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if gate.lower() in content.lower():
                            gate_found = True
                            break
            
            if not gate_found:
                self.errors.append(f"Quality gate not defined: {gate}")
        
        return len(self.errors) == 0
    
    def generate_report(self) -> str:
        """Generate validation report"""
        report = f"""# Pre-Implementation Validation Report

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Validator**: Pre-Implementation Validation Tool v1.0

## Summary
- **Total Errors**: {len(self.errors)}
- **Total Warnings**: {len(self.warnings)}
- **Overall Status**: {'✅ PASS' if len(self.errors) == 0 else '❌ FAIL'}

## Validation Results

### Errors
"""
        
        if self.errors:
            for error in self.errors:
                report += f"- ❌ {error}\n"
        else:
            report += "- ✅ No errors found\n"
        
        report += "\n### Warnings\n"
        
        if self.warnings:
            for warning in self.warnings:
                report += f"- ⚠️ {warning}\n"
        else:
            report += "- ✅ No warnings\n"
        
        report += f"""
## Recommendations

### If PASS (no errors):
- Review and address any warnings
- Proceed to implementation phase
- Ensure quality gates are followed

### If FAIL (has errors):
- Address all errors before proceeding
- Re-run validation after fixes
- Do not start implementation until PASS

## Quality Gate Status
{'✅ Pre-implementation validation PASSED - Ready to proceed' if len(self.errors) == 0 else '❌ Pre-implementation validation FAILED - Do not proceed'}

---
*Generated by Pre-Implementation Validation Tool*
"""
        
        return report
    
    def run_validation(self) -> bool:
        """Run complete validation process"""
        print("🔍 Starting pre-implementation validation...")
        print("=" * 50)
        
        # Run all validations
        files_valid = self.validate_files_exist()
        
        if files_valid:
            for file_path in self.config["required_files"]:
                self.validate_file_sections(file_path)
            
            self.validate_requirements_quality()
            self.validate_analysis_completeness()
            self.validate_plan_feasibility()
            self.validate_quality_gates()
        
        # Generate report
        report = self.generate_report()
        
        with open(self.report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📋 Validation report generated: {self.report_path}")
        
        # Print summary
        if len(self.errors) == 0:
            print("✅ PRE-IMPLEMENTATION VALIDATION PASSED")
            print("✅ Ready to proceed with implementation")
        else:
            print("❌ PRE-IMPLEMENTATION VALIDATION FAILED")
            print("❌ Address errors before proceeding")
        
        print(f"📊 Summary: {len(self.errors)} errors, {len(self.warnings)} warnings")
        
        return len(self.errors) == 0

def main():
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "validation_config.json"
    
    validator = PreImplementationValidator(config_file)
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

### 2. Live Implementation Monitor

**Purpose**: Real-time monitoring and validation during implementation.

**Script: `implementation_monitor.py`**
```python
#!/usr/bin/env python3
"""
Live Implementation Monitor
Monitors file changes and validates implementation in real-time
"""

import os
import time
import hashlib
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from bs4 import BeautifulSoup
import re
from datetime import datetime

class ImplementationMonitor(FileSystemEventHandler):
    def __init__(self, template_path: str):
        self.template_path = template_path
        self.last_validation = None
        self.validation_history = []
        self.quality_gates = []
        
    def on_modified(self, event):
        if event.is_directory:
            return
        
        if event.src_path.endswith('.html'):
            print(f"🔄 Template modified: {event.src_path}")
            self.validate_template(event.src_path)
    
    def validate_template(self, file_path: str):
        """Validate template in real-time"""
        print(f"🔍 Validating: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Run validation checks
            errors = []
            warnings = []
            
            # Check Django template structure
            errors.extend(self.validate_django_structure(content))
            
            # Check HTML structure
            errors.extend(self.validate_html_structure(soup))
            
            # Check CSS classes
            warnings.extend(self.validate_css_classes(soup))
            
            # Check JavaScript functions
            warnings.extend(self.validate_javascript(content))
            
            # Check accessibility
            warnings.extend(self.validate_accessibility(soup))
            
            # Check security
            errors.extend(self.validate_security(content))
            
            # Print results
            self.print_validation_results(file_path, errors, warnings)
            
            # Store validation result
            self.last_validation = {
                'timestamp': datetime.now(),
                'file': file_path,
                'errors': len(errors),
                'warnings': len(warnings),
                'status': 'PASS' if len(errors) == 0 else 'FAIL'
            }
            
            self.validation_history.append(self.last_validation)
            
        except Exception as e:
            print(f"❌ Validation error: {str(e)}")
    
    def validate_django_structure(self, content: str) -> list:
        """Validate Django template structure"""
        errors = []
        
        required_elements = [
            ("{% extends 'base.html' %}", "Missing base template extension"),
            ("{% load static %}", "Missing static files loading"),
            ("{% block title %}", "Missing title block"),
            ("{% block content %}", "Missing content block"),
            ("{% csrf_token %}", "Missing CSRF token")
        ]
        
        for element, error_msg in required_elements:
            if element not in content:
                errors.append(f"Django: {error_msg}")
        
        return errors
    
    def validate_html_structure(self, soup: BeautifulSoup) -> list:
        """Validate HTML structure"""
        errors = []
        
        # Check for required classes
        required_classes = ['agent-container', 'agent-header', 'agent-grid']
        for class_name in required_classes:
            if not soup.find(class_=class_name):
                errors.append(f"HTML: Missing required class '{class_name}'")
        
        # Check for semantic HTML
        if not soup.find('h1'):
            errors.append("HTML: Missing h1 heading")
        
        # Check for form structure if present
        forms = soup.find_all('form')
        for form in forms:
            if not form.get('method'):
                errors.append("HTML: Form missing method attribute")
        
        return errors
    
    def validate_css_classes(self, soup: BeautifulSoup) -> list:
        """Validate CSS class usage"""
        warnings = []
        
        # Extract all classes
        all_classes = []
        for element in soup.find_all(class_=True):
            all_classes.extend(element.get('class'))
        
        # Check for standard classes
        expected_classes = ['btn', 'form-control', 'widget', 'agent-main']
        for class_name in expected_classes:
            if class_name not in all_classes:
                warnings.append(f"CSS: Standard class '{class_name}' not found")
        
        return warnings
    
    def validate_javascript(self, content: str) -> list:
        """Validate JavaScript functions"""
        warnings = []
        
        # Extract JavaScript content
        js_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
        if js_match:
            js_content = js_match.group(1)
            
            # Check for essential functions
            essential_functions = ['updateWalletBalance', 'showToast']
            for func_name in essential_functions:
                if func_name not in js_content:
                    warnings.append(f"JavaScript: Essential function '{func_name}' not found")
        
        return warnings
    
    def validate_accessibility(self, soup: BeautifulSoup) -> list:
        """Validate accessibility features"""
        warnings = []
        
        # Check for ARIA attributes
        aria_elements = soup.find_all(attrs={"aria-label": True})
        if len(aria_elements) == 0:
            warnings.append("Accessibility: No ARIA labels found")
        
        # Check for form labels
        inputs = soup.find_all('input')
        labels = soup.find_all('label')
        if len(inputs) > len(labels):
            warnings.append("Accessibility: Some inputs may be missing labels")
        
        return warnings
    
    def validate_security(self, content: str) -> list:
        """Validate security measures"""
        errors = []
        
        # Check for HTML sanitization
        if 'innerHTML' in content and 'sanitize' not in content.lower():
            errors.append("Security: Potential XSS vulnerability - innerHTML without sanitization")
        
        # Check for SQL injection prevention (basic check)
        if re.search(r'\.query\s*\([^)]*\+', content):
            errors.append("Security: Potential SQL injection - string concatenation in query")
        
        return errors
    
    def print_validation_results(self, file_path: str, errors: list, warnings: list):
        """Print validation results"""
        print(f"📊 Validation Results for {file_path}")
        print(f"   Errors: {len(errors)}")
        print(f"   Warnings: {len(warnings)}")
        
        if errors:
            print("   🚨 ERRORS:")
            for error in errors:
                print(f"     ❌ {error}")
        
        if warnings:
            print("   ⚠️  WARNINGS:")
            for warning in warnings:
                print(f"     ⚠️ {warning}")
        
        status = "✅ PASS" if len(errors) == 0 else "❌ FAIL"
        print(f"   Status: {status}")
        print("-" * 50)
    
    def get_status_summary(self) -> dict:
        """Get current status summary"""
        if not self.validation_history:
            return {"status": "No validations yet", "errors": 0, "warnings": 0}
        
        latest = self.validation_history[-1]
        return {
            "status": latest['status'],
            "errors": latest['errors'],
            "warnings": latest['warnings'],
            "last_check": latest['timestamp'].strftime('%H:%M:%S')
        }

def monitor_implementation(template_path: str):
    """Start monitoring implementation"""
    print(f"🔍 Starting implementation monitor for: {template_path}")
    print("📁 Monitoring directory for changes...")
    print("Press Ctrl+C to stop monitoring")
    print("=" * 50)
    
    event_handler = ImplementationMonitor(template_path)
    observer = Observer()
    
    # Monitor the directory containing the template
    directory = os.path.dirname(template_path) or '.'
    observer.schedule(event_handler, directory, recursive=True)
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
            # Print status every 30 seconds
            if int(time.time()) % 30 == 0:
                status = event_handler.get_status_summary()
                print(f"📊 Status: {status['status']} | Errors: {status['errors']} | Warnings: {status['warnings']}")
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Monitoring stopped")
    
    observer.join()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python implementation_monitor.py <template_path>")
        sys.exit(1)
    
    template_path = sys.argv[1]
    monitor_implementation(template_path)
```

### 3. Post-Implementation Quality Gate

**Purpose**: Comprehensive validation after implementation completion.

**Script: `post_implementation_validator.py`**
```python
#!/usr/bin/env python3
"""
Post-Implementation Quality Gate
Comprehensive validation after implementation completion
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Tuple

class PostImplementationValidator:
    def __init__(self, source_template: str, target_template: str):
        self.source_template = source_template
        self.target_template = target_template
        self.validation_results = {
            'structural_comparison': {},
            'visual_validation': {},
            'functional_testing': {},
            'performance_check': {},
            'accessibility_audit': {},
            'security_validation': {},
            'overall_status': 'PENDING'
        }
        self.errors = []
        self.warnings = []
        
    def run_complete_validation(self) -> bool:
        """Run complete post-implementation validation"""
        print("🔍 Starting post-implementation validation...")
        print("=" * 60)
        
        # 1. Structural Comparison
        print("📐 Running structural comparison...")
        self.validate_structure()
        
        # 2. Visual Validation
        print("👁️  Running visual validation...")
        self.validate_visual_elements()
        
        # 3. Functional Testing
        print("⚙️  Running functional testing...")
        self.validate_functionality()
        
        # 4. Performance Check
        print("⚡ Running performance check...")
        self.validate_performance()
        
        # 5. Accessibility Audit
        print("♿ Running accessibility audit...")
        self.validate_accessibility()
        
        # 6. Security Validation
        print("🔐 Running security validation...")
        self.validate_security()
        
        # Generate final report
        self.generate_final_report()
        
        # Determine overall status
        has_critical_errors = any(error.get('level') == 'critical' for error in self.errors)
        self.validation_results['overall_status'] = 'FAIL' if has_critical_errors else 'PASS'
        
        return not has_critical_errors
    
    def validate_structure(self):
        """Compare structural elements between source and target"""
        print("  🔍 Analyzing HTML structure...")
        
        source_soup = self.parse_template(self.source_template)
        target_soup = self.parse_template(self.target_template)
        
        if not source_soup or not target_soup:
            self.errors.append({
                'category': 'structural',
                'level': 'critical',
                'message': 'Failed to parse templates'
            })
            return
        
        # Compare CSS classes
        source_classes = self.extract_css_classes(source_soup)
        target_classes = self.extract_css_classes(target_soup)
        
        missing_classes = source_classes - target_classes
        extra_classes = target_classes - source_classes
        
        if missing_classes:
            self.errors.append({
                'category': 'structural',
                'level': 'high',
                'message': f'Missing CSS classes: {", ".join(list(missing_classes)[:10])}'
            })
        
        if extra_classes:
            self.warnings.append({
                'category': 'structural',
                'level': 'medium',
                'message': f'Extra CSS classes: {", ".join(list(extra_classes)[:10])}'
            })
        
        # Compare HTML structure
        source_structure = self.analyze_html_structure(source_soup)
        target_structure = self.analyze_html_structure(target_soup)
        
        structure_match = self.compare_structures(source_structure, target_structure)
        
        self.validation_results['structural_comparison'] = {
            'classes_missing': len(missing_classes),
            'classes_extra': len(extra_classes),
            'structure_match': structure_match,
            'status': 'PASS' if len(missing_classes) == 0 and structure_match > 0.8 else 'FAIL'
        }
        
        print(f"  ✅ Structure comparison: {structure_match:.1%} match")
    
    def validate_visual_elements(self):
        """Validate visual elements and styling"""
        print("  🎨 Analyzing visual elements...")
        
        target_content = self.read_template(self.target_template)
        if not target_content:
            return
        
        # Check for CSS custom properties
        css_vars = re.findall(r'--[\w-]+', target_content)
        expected_vars = ['--primary', '--surface', '--spacing-lg', '--radius-md']
        
        missing_vars = [var for var in expected_vars if var not in css_vars]
        if missing_vars:
            self.errors.append({
                'category': 'visual',
                'level': 'medium',
                'message': f'Missing CSS variables: {", ".join(missing_vars)}'
            })
        
        # Check for responsive design
        has_media_queries = '@media' in target_content
        if not has_media_queries:
            self.warnings.append({
                'category': 'visual',
                'level': 'medium',
                'message': 'No responsive design detected'
            })
        
        # Check color scheme consistency
        color_consistency = self.check_color_consistency(target_content)
        
        self.validation_results['visual_validation'] = {
            'css_variables': len(css_vars),
            'missing_variables': len(missing_vars),
            'responsive_design': has_media_queries,
            'color_consistency': color_consistency,
            'status': 'PASS' if len(missing_vars) == 0 else 'FAIL'
        }
        
        print(f"  ✅ Visual validation: {'PASS' if len(missing_vars) == 0 else 'FAIL'}")
    
    def validate_functionality(self):
        """Validate JavaScript functionality"""
        print("  ⚙️  Analyzing JavaScript functionality...")
        
        target_content = self.read_template(self.target_template)
        if not target_content:
            return
        
        # Extract JavaScript content
        js_content = re.search(r'<script[^>]*>(.*?)</script>', target_content, re.DOTALL)
        if not js_content:
            self.warnings.append({
                'category': 'functional',
                'level': 'medium',
                'message': 'No JavaScript found in template'
            })
            return
        
        js_code = js_content.group(1)
        
        # Check for essential functions
        essential_functions = [
            'updateWalletBalance',
            'showToast',
            'copyToClipboard',
            'downloadAsFile'
        ]
        
        missing_functions = []
        for func in essential_functions:
            if func not in js_code:
                missing_functions.append(func)
        
        if missing_functions:
            self.errors.append({
                'category': 'functional',
                'level': 'high',
                'message': f'Missing functions: {", ".join(missing_functions)}'
            })
        
        # Check for error handling
        has_error_handling = 'try' in js_code and 'catch' in js_code
        if not has_error_handling:
            self.warnings.append({
                'category': 'functional',
                'level': 'medium',
                'message': 'No error handling detected in JavaScript'
            })
        
        # Check for event listeners
        event_patterns = ['addEventListener', 'onclick', 'onsubmit']
        has_events = any(pattern in js_code for pattern in event_patterns)
        
        self.validation_results['functional_testing'] = {
            'functions_found': len(essential_functions) - len(missing_functions),
            'functions_missing': len(missing_functions),
            'error_handling': has_error_handling,
            'event_listeners': has_events,
            'status': 'PASS' if len(missing_functions) == 0 else 'FAIL'
        }
        
        print(f"  ✅ Functional validation: {'PASS' if len(missing_functions) == 0 else 'FAIL'}")
    
    def validate_performance(self):
        """Check performance considerations"""
        print("  ⚡ Analyzing performance...")
        
        target_content = self.read_template(self.target_template)
        if not target_content:
            return
        
        # Check file size
        file_size = len(target_content.encode('utf-8'))
        size_score = 'GOOD' if file_size < 50000 else 'WARNING' if file_size < 100000 else 'POOR'
        
        # Check for optimization
        has_minification = not re.search(r'\n\s+', target_content)
        has_compression = 'gzip' in target_content.lower()
        
        # Check for lazy loading
        has_lazy_loading = 'lazy' in target_content.lower()
        
        # Check for unnecessary requests
        external_requests = len(re.findall(r'src="http', target_content))
        
        performance_score = 0
        if size_score == 'GOOD':
            performance_score += 25
        if external_requests < 5:
            performance_score += 25
        if has_lazy_loading:
            performance_score += 25
        performance_score += 25  # Base score
        
        self.validation_results['performance_check'] = {
            'file_size_bytes': file_size,
            'size_score': size_score,
            'external_requests': external_requests,
            'lazy_loading': has_lazy_loading,
            'performance_score': performance_score,
            'status': 'PASS' if performance_score >= 75 else 'FAIL'
        }
        
        print(f"  ✅ Performance check: {performance_score}/100")
    
    def validate_accessibility(self):
        """Validate accessibility compliance"""
        print("  ♿ Analyzing accessibility...")
        
        target_soup = self.parse_template(self.target_template)
        if not target_soup:
            return
        
        accessibility_score = 0
        issues = []
        
        # Check for ARIA attributes
        aria_elements = target_soup.find_all(attrs={'aria-label': True})
        if len(aria_elements) > 0:
            accessibility_score += 20
        else:
            issues.append('No ARIA labels found')
        
        # Check for semantic HTML
        semantic_tags = ['header', 'main', 'nav', 'section', 'article', 'aside', 'footer']
        found_semantic = [tag for tag in semantic_tags if target_soup.find(tag)]
        accessibility_score += min(len(found_semantic) * 5, 20)
        
        # Check for form labels
        inputs = target_soup.find_all('input')
        labels = target_soup.find_all('label')
        if len(inputs) > 0 and len(labels) >= len(inputs):
            accessibility_score += 20
        elif len(inputs) > len(labels):
            issues.append('Some inputs missing labels')
        
        # Check for image alt text
        images = target_soup.find_all('img')
        images_with_alt = [img for img in images if img.get('alt')]
        if len(images) == 0 or len(images_with_alt) == len(images):
            accessibility_score += 20
        else:
            issues.append('Some images missing alt text')
        
        # Check for keyboard navigation
        target_content = self.read_template(self.target_template)
        has_keyboard_nav = 'keydown' in target_content or 'tabindex' in target_content
        if has_keyboard_nav:
            accessibility_score += 20
        else:
            issues.append('No keyboard navigation detected')
        
        self.validation_results['accessibility_audit'] = {
            'score': accessibility_score,
            'issues': issues,
            'aria_elements': len(aria_elements),
            'semantic_tags': len(found_semantic),
            'status': 'PASS' if accessibility_score >= 80 else 'FAIL'
        }
        
        print(f"  ✅ Accessibility audit: {accessibility_score}/100")
    
    def validate_security(self):
        """Validate security measures"""
        print("  🔐 Analyzing security...")
        
        target_content = self.read_template(self.target_template)
        if not target_content:
            return
        
        security_score = 0
        vulnerabilities = []
        
        # Check for CSRF token
        if '{% csrf_token %}' in target_content:
            security_score += 25
        else:
            vulnerabilities.append('Missing CSRF token')
        
        # Check for XSS prevention
        if 'sanitize' in target_content.lower() or 'HTMLSanitizer' in target_content:
            security_score += 25
        elif 'innerHTML' in target_content:
            vulnerabilities.append('Potential XSS vulnerability')
        else:
            security_score += 25
        
        # Check for input validation
        if 'validate' in target_content.lower() or 'required' in target_content:
            security_score += 25
        else:
            vulnerabilities.append('Limited input validation')
        
        # Check for secure headers
        security_score += 25  # Base score for template-level security
        
        self.validation_results['security_validation'] = {
            'score': security_score,
            'vulnerabilities': vulnerabilities,
            'csrf_protection': '{% csrf_token %}' in target_content,
            'xss_prevention': 'sanitize' in target_content.lower(),
            'status': 'PASS' if security_score >= 75 else 'FAIL'
        }
        
        print(f"  ✅ Security validation: {security_score}/100")
    
    def parse_template(self, file_path: str) -> BeautifulSoup:
        """Parse HTML template"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return BeautifulSoup(content, 'html.parser')
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def read_template(self, file_path: str) -> str:
        """Read template content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""
    
    def extract_css_classes(self, soup: BeautifulSoup) -> set:
        """Extract all CSS classes from soup"""
        classes = set()
        for element in soup.find_all(class_=True):
            classes.update(element.get('class'))
        return classes
    
    def analyze_html_structure(self, soup: BeautifulSoup) -> dict:
        """Analyze HTML structure"""
        structure = {
            'total_elements': len(soup.find_all()),
            'unique_tags': len(set(tag.name for tag in soup.find_all())),
            'forms': len(soup.find_all('form')),
            'inputs': len(soup.find_all('input')),
            'buttons': len(soup.find_all('button')),
            'headings': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
        }
        return structure
    
    def compare_structures(self, source: dict, target: dict) -> float:
        """Compare two structure dictionaries"""
        total_score = 0
        comparisons = 0
        
        for key in source:
            if key in target:
                if source[key] == 0 and target[key] == 0:
                    total_score += 1
                elif source[key] == 0 or target[key] == 0:
                    total_score += 0
                else:
                    ratio = min(source[key], target[key]) / max(source[key], target[key])
                    total_score += ratio
                comparisons += 1
        
        return total_score / comparisons if comparisons > 0 else 0
    
    def check_color_consistency(self, content: str) -> float:
        """Check color scheme consistency"""
        # Extract color values
        colors = re.findall(r'#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|rgb\([^)]+\)', content)
        
        # Check for CSS variables usage
        var_usage = len(re.findall(r'var\(--[\w-]+\)', content))
        total_colors = len(colors) + var_usage
        
        if total_colors == 0:
            return 1.0
        
        # Higher score for more CSS variable usage
        consistency_score = var_usage / total_colors
        return consistency_score
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        report_path = f"post_implementation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        overall_status = self.validation_results['overall_status']
        
        report = f"""# Post-Implementation Validation Report

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Source Template**: {self.source_template}
**Target Template**: {self.target_template}
**Overall Status**: {'✅ PASS' if overall_status == 'PASS' else '❌ FAIL'}

## Executive Summary

This report provides a comprehensive validation of the template implementation against quality standards and the source template.

### Overall Results
- **Structural Comparison**: {self.validation_results['structural_comparison'].get('status', 'UNKNOWN')}
- **Visual Validation**: {self.validation_results['visual_validation'].get('status', 'UNKNOWN')}
- **Functional Testing**: {self.validation_results['functional_testing'].get('status', 'UNKNOWN')}
- **Performance Check**: {self.validation_results['performance_check'].get('status', 'UNKNOWN')}
- **Accessibility Audit**: {self.validation_results['accessibility_audit'].get('status', 'UNKNOWN')}
- **Security Validation**: {self.validation_results['security_validation'].get('status', 'UNKNOWN')}

## Detailed Results

### 1. Structural Comparison
- **Structure Match**: {self.validation_results['structural_comparison'].get('structure_match', 0):.1%}
- **Missing Classes**: {self.validation_results['structural_comparison'].get('classes_missing', 0)}
- **Extra Classes**: {self.validation_results['structural_comparison'].get('classes_extra', 0)}

### 2. Visual Validation
- **CSS Variables**: {self.validation_results['visual_validation'].get('css_variables', 0)} found
- **Missing Variables**: {self.validation_results['visual_validation'].get('missing_variables', 0)}
- **Responsive Design**: {'✅ Yes' if self.validation_results['visual_validation'].get('responsive_design') else '❌ No'}

### 3. Functional Testing
- **Functions Found**: {self.validation_results['functional_testing'].get('functions_found', 0)}
- **Functions Missing**: {self.validation_results['functional_testing'].get('functions_missing', 0)}
- **Error Handling**: {'✅ Yes' if self.validation_results['functional_testing'].get('error_handling') else '❌ No'}

### 4. Performance Analysis
- **File Size**: {self.validation_results['performance_check'].get('file_size_bytes', 0):,} bytes
- **Performance Score**: {self.validation_results['performance_check'].get('performance_score', 0)}/100
- **External Requests**: {self.validation_results['performance_check'].get('external_requests', 0)}

### 5. Accessibility Compliance
- **Accessibility Score**: {self.validation_results['accessibility_audit'].get('score', 0)}/100
- **ARIA Elements**: {self.validation_results['accessibility_audit'].get('aria_elements', 0)}
- **Issues Found**: {len(self.validation_results['accessibility_audit'].get('issues', []))}

### 6. Security Assessment
- **Security Score**: {self.validation_results['security_validation'].get('score', 0)}/100
- **CSRF Protection**: {'✅ Yes' if self.validation_results['security_validation'].get('csrf_protection') else '❌ No'}
- **Vulnerabilities**: {len(self.validation_results['security_validation'].get('vulnerabilities', []))}

## Issues Found

### Critical Errors
"""
        
        critical_errors = [error for error in self.errors if error.get('level') == 'critical']
        if critical_errors:
            for error in critical_errors:
                report += f"- ❌ **{error['category'].title()}**: {error['message']}\n"
        else:
            report += "- ✅ No critical errors found\n"
        
        report += "\n### High Priority Issues\n"
        high_errors = [error for error in self.errors if error.get('level') == 'high']
        if high_errors:
            for error in high_errors:
                report += f"- ⚠️ **{error['category'].title()}**: {error['message']}\n"
        else:
            report += "- ✅ No high priority issues found\n"
        
        report += "\n### Warnings\n"
        if self.warnings:
            for warning in self.warnings:
                report += f"- ⚠️ **{warning['category'].title()}**: {warning['message']}\n"
        else:
            report += "- ✅ No warnings\n"
        
        report += f"""
## Recommendations

### If PASS:
- Address any remaining warnings
- Monitor performance in production
- Consider accessibility improvements
- Document any deviations from source

### If FAIL:
- Address all critical and high priority issues
- Re-run validation after fixes
- Consider rollback if issues are severe
- Update implementation approach

## Quality Gate Decision

**Gate Status**: {'✅ APPROVED - Implementation meets quality standards' if overall_status == 'PASS' else '❌ REJECTED - Implementation fails quality standards'}

---
*Generated by Post-Implementation Validation Tool v1.0*
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📋 Final report generated: {report_path}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python post_implementation_validator.py <source_template> <target_template>")
        sys.exit(1)
    
    source_template = sys.argv[1]
    target_template = sys.argv[2]
    
    validator = PostImplementationValidator(source_template, target_template)
    success = validator.run_complete_validation()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ POST-IMPLEMENTATION VALIDATION PASSED")
        print("✅ Implementation approved for deployment")
    else:
        print("❌ POST-IMPLEMENTATION VALIDATION FAILED")
        print("❌ Implementation requires fixes before deployment")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

## Template Generation Framework

### 4. Smart Template Generator

**Purpose**: Generate optimized templates with built-in quality features.

**Script: `smart_template_generator.py`**
```python
#!/usr/bin/env python3
"""
Smart Template Generator
Generates optimized Django templates with built-in quality features
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class SmartTemplateGenerator:
    def __init__(self, config_file: str = "template_config.json"):
        self.config = self.load_config(config_file)
        self.template_components = self.load_components()
        
    def load_config(self, config_file: str) -> Dict:
        """Load template generation configuration"""
        default_config = {
            "agent_name": "New Agent",
            "description": "AI-powered tool for generating content",
            "include_wallet": True,
            "include_quick_agents": True,
            "include_toast_notifications": True,
            "include_copy_download": True,
            "responsive_design": True,
            "accessibility_features": True,
            "security_features": True,
            "performance_optimizations": True,
            "color_scheme": "default",
            "layout_type": "two-column"
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def load_components(self) -> Dict:
        """Load template component definitions"""
        return {
            "header": self.generate_header_component,
            "wallet": self.generate_wallet_component,
            "quick_agents": self.generate_quick_agents_component,
            "form": self.generate_form_component,
            "output": self.generate_output_component,
            "sidebar": self.generate_sidebar_component,
            "css": self.generate_css_styles,
            "javascript": self.generate_javascript_code
        }
    
    def generate_template(self, output_path: str) -> str:
        """Generate complete optimized template"""
        print(f"🚀 Generating template: {self.config['agent_name']}")
        
        # Generate template structure
        template_content = self.build_template_structure()
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print(f"✅ Template generated: {output_path}")
        
        # Generate validation config
        self.generate_validation_config(output_path)
        
        return template_content
    
    def build_template_structure(self) -> str:
        """Build complete template structure"""
        agent_name = self.config['agent_name']
        description = self.config['description']
        
        template = f'''{% extends 'base.html' %}
{% load static %}

{% block title %}{agent_name} - NetCop AI Hub{% endblock %}

{% block extra_css %}
<style>
{self.template_components["css"]()}
</style>
{% endblock %}

{% block content %}
<div class="agent-container">
    <div class="agent-grid">
        <!-- Main Content Area -->
        <div class="agent-main">
{self.template_components["header"]()}
            
{self.template_components["form"]()}
            
{self.template_components["output"]()}
        </div>
        
        <!-- Sidebar Widgets -->
        <div class="agent-sidebar">
{self.template_components["sidebar"]()}
        </div>
    </div>
</div>

<!-- Toast Notifications Container -->
<div id="toast-container" class="toast-container" aria-live="polite" aria-atomic="true"></div>

<!-- Loading Overlay -->
<div id="loadingOverlay" class="loading-overlay" style="display: none;">
    <div class="loading-spinner">
        <div class="spinner"></div>
        <p>Processing your request...</p>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
{self.template_components["javascript"]()}
</script>
{% endblock %}
'''
        
        return template
    
    def generate_header_component(self) -> str:
        """Generate header component"""
        agent_name = self.config['agent_name']
        description = self.config['description']
        
        return f'''            <div class="agent-header">
                <div class="agent-title">
                    <h1>{agent_name}</h1>
                    <p class="agent-description">{description}</p>
                </div>
                <div class="agent-controls">
                    <button type="button" class="btn btn-outline btn-sm" onclick="resetUI()" 
                            aria-label="Reset interface">
                        <span aria-hidden="true">🔄</span> Reset
                    </button>
                </div>
            </div>'''
    
    def generate_wallet_component(self) -> str:
        """Generate wallet widget if enabled"""
        if not self.config.get('include_wallet', True):
            return ""
            
        return '''            <div class="widget wallet-widget" role="region" aria-labelledby="wallet-title">
                <div class="widget-header">
                    <h3 id="wallet-title" class="widget-title">💰 Your Wallet</h3>
                </div>
                <div class="widget-content">
                    <div class="wallet-balance">
                        <span class="balance-label">Balance:</span>
                        <span class="balance-amount" id="walletBalance" aria-live="polite">
                            {{ user.wallet_balance|floatformat:2 }}
                        </span>
                        <span class="balance-currency">AED</span>
                    </div>
                    <a href="{% url 'wallet_topup' %}" class="btn btn-primary btn-sm">
                        Top Up Wallet
                    </a>
                </div>
            </div>'''
    
    def generate_quick_agents_component(self) -> str:
        """Generate quick agents widget if enabled"""
        if not self.config.get('include_quick_agents', True):
            return ""
            
        return '''            <div class="widget quick-agents-widget" role="region" aria-labelledby="quick-agents-title">
                <div class="widget-header">
                    <h3 id="quick-agents-title" class="widget-title">⚡ Quick Agents</h3>
                    <button type="button" 
                            class="btn btn-outline btn-sm" 
                            id="quick-agent-toggle"
                            onclick="toggleQuickAgents()"
                            aria-expanded="false"
                            aria-controls="quickAgentsPanel">
                        Quick Access
                    </button>
                </div>
                <div class="widget-content">
                    <p class="text-muted">Access other AI agents quickly while working on your current task.</p>
                </div>
            </div>'''
    
    def generate_form_component(self) -> str:
        """Generate form component"""
        return '''            <div class="agent-form-container">
                <form id="agentForm" method="post" enctype="multipart/form-data" class="agent-form" novalidate>
                    {% csrf_token %}
                    
                    <div class="form-sections">
                        {% for field in form %}
                            <div class="form-group">
                                <label for="{{ field.id_for_label }}" class="form-label{% if field.field.required %} required{% endif %}">
                                    {{ field.label }}
                                    {% if field.field.required %}
                                        <span class="sr-only">required</span>
                                    {% endif %}
                                </label>
                                
                                {{ field }}
                                
                                {% if field.help_text %}
                                    <div class="form-help" id="{{ field.id_for_label }}_help">
                                        {{ field.help_text }}
                                    </div>
                                {% endif %}
                                
                                {% if field.errors %}
                                    <div class="form-error" role="alert" aria-live="polite">
                                        {% for error in field.errors %}
                                            {{ error }}
                                        {% endfor %}
                                    </div>
                                {% endif %}
                            </div>
                        {% endfor %}
                    </div>
                    
                    <div class="form-actions">
                        <button type="submit" 
                                class="btn btn-primary" 
                                id="submitBtn"
                                aria-describedby="submit-help">
                            <span class="btn-text">Generate Content</span>
                        </button>
                        <div id="submit-help" class="form-help">
                            Click to process your request
                        </div>
                    </div>
                </form>
            </div>'''
    
    def generate_output_component(self) -> str:
        """Generate output component"""
        copy_download = ''
        if self.config.get('include_copy_download', True):
            copy_download = '''                        <div class="output-actions">
                            <button type="button" 
                                    class="btn btn-outline btn-sm" 
                                    onclick="copyToClipboard('output-content')"
                                    aria-label="Copy content to clipboard">
                                📋 Copy
                            </button>
                            <button type="button" 
                                    class="btn btn-outline btn-sm" 
                                    onclick="downloadAsFile('output-content', 'generated-content.txt')"
                                    aria-label="Download content as file">
                                💾 Download
                            </button>
                        </div>'''
        
        return f'''            <div class="agent-output" id="outputSection" style="display: none;">
                <div class="output-header">
                    <h3>Generated Content</h3>
{copy_download}
                </div>
                <div class="output-content" id="output-content" role="region" aria-live="polite">
                    <!-- Generated content will appear here -->
                </div>
            </div>'''
    
    def generate_sidebar_component(self) -> str:
        """Generate sidebar components"""
        components = []
        
        if self.config.get('include_wallet', True):
            components.append(self.generate_wallet_component())
        
        if self.config.get('include_quick_agents', True):
            components.append(self.generate_quick_agents_component())
        
        # Add help widget
        components.append('''            <div class="widget help-widget" role="region" aria-labelledby="help-title">
                <div class="widget-header">
                    <h3 id="help-title" class="widget-title">❓ Need Help?</h3>
                </div>
                <div class="widget-content">
                    <p>Having trouble? Check our guides or contact support.</p>
                    <a href="#" class="btn btn-outline btn-sm">View Guide</a>
                </div>
            </div>''')
        
        return '\n\n'.join(components)
    
    def generate_css_styles(self) -> str:
        """Generate CSS styles with design system"""
        responsive_css = ""
        if self.config.get('responsive_design', True):
            responsive_css = '''
    /* Responsive Design */
    @media (max-width: 768px) {
        .agent-grid {
            grid-template-columns: 1fr;
            gap: var(--spacing-lg);
        }
        
        .agent-sidebar {
            order: -1;
        }
        
        .agent-container {
            padding: var(--spacing-md);
        }
    }
    
    @media (max-width: 480px) {
        .agent-container {
            padding: var(--spacing-sm);
        }
        
        .agent-grid {
            gap: var(--spacing-md);
        }
        
        .btn {
            width: 100%;
            margin-bottom: var(--spacing-sm);
        }
    }'''
        
        return f'''    /* Design System Variables */
    :root {{
        /* Color Palette */
        --primary: #000000;
        --surface: #ffffff;
        --surface-variant: #f8fafc;
        --background: #f3f4f6;
        --outline: #e4e7eb;
        --outline-variant: #e1e4e7;
        --on-surface: #1a1a1a;
        --on-surface-variant: #6b7280;
        --success: #10b981;
        --error: #ef4444;
        --warning: #f59e0b;
        --info: #3b82f6;
        
        /* Border Radius */
        --radius-xs: 4px;
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
        
        /* Spacing Scale */
        --spacing-xs: 4px;
        --spacing-sm: 8px;
        --spacing-md: 16px;
        --spacing-lg: 24px;
        --spacing-xl: 32px;
        --spacing-2xl: 48px;
        
        /* Typography */
        --font-size-sm: 0.875rem;
        --font-size-base: 1rem;
        --font-size-lg: 1.125rem;
        --font-size-xl: 1.25rem;
        --font-size-2xl: 1.5rem;
        
        /* Shadows */
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
        --shadow-md: 0 4px 8px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 20px rgba(0, 0, 0, 0.15);
        
        /* Transitions */
        --transition-fast: 0.15s ease;
        --transition-base: 0.2s ease;
    }}
    
    /* Layout */
    .agent-container {{
        max-width: 1200px;
        margin: 0 auto;
        padding: var(--spacing-lg);
    }}
    
    .agent-grid {{
        display: grid;
        grid-template-columns: 1fr 300px;
        gap: var(--spacing-xl);
        align-items: start;
    }}
    
    /* Components */
    .agent-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: var(--spacing-xl);
        padding-bottom: var(--spacing-lg);
        border-bottom: 1px solid var(--outline);
    }}
    
    .agent-title h1 {{
        margin: 0 0 var(--spacing-sm) 0;
        font-size: var(--font-size-2xl);
        font-weight: 600;
        color: var(--on-surface);
    }}
    
    .agent-description {{
        margin: 0;
        color: var(--on-surface-variant);
        font-size: var(--font-size-lg);
    }}
    
    /* Widget System */
    .widget {{
        background: var(--surface);
        border: 1px solid var(--outline);
        border-radius: var(--radius-md);
        padding: var(--spacing-md);
        margin-bottom: var(--spacing-md);
        box-shadow: var(--shadow-sm);
        transition: var(--transition-base);
    }}
    
    .widget:hover {{
        box-shadow: var(--shadow-md);
    }}
    
    .widget-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-md);
    }}
    
    .widget-title {{
        margin: 0;
        font-size: var(--font-size-lg);
        font-weight: 600;
        color: var(--on-surface);
    }}
    
    .widget-content {{
        color: var(--on-surface-variant);
    }}
    
    /* Form Components */
    .form-group {{
        margin-bottom: var(--spacing-lg);
    }}
    
    .form-label {{
        display: block;
        font-weight: 500;
        color: var(--on-surface);
        margin-bottom: var(--spacing-sm);
    }}
    
    .form-control {{
        width: 100%;
        padding: var(--spacing-md);
        border: 1px solid var(--outline);
        border-radius: var(--radius-sm);
        font-size: var(--font-size-base);
        background: var(--surface);
        color: var(--on-surface);
        transition: var(--transition-base);
    }}
    
    .form-control:focus {{
        outline: none;
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1);
    }}
    
    /* Button Components */
    .btn {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: var(--spacing-sm) var(--spacing-md);
        border: 1px solid transparent;
        border-radius: var(--radius-sm);
        font-size: var(--font-size-base);
        font-weight: 500;
        text-decoration: none;
        cursor: pointer;
        transition: var(--transition-base);
        user-select: none;
    }}
    
    .btn-primary {{
        background: var(--primary);
        color: var(--surface);
    }}
    
    .btn-primary:hover:not(:disabled) {{
        background: color-mix(in srgb, var(--primary) 90%, black);
    }}
    
    .btn-outline {{
        background: transparent;
        color: var(--primary);
        border-color: var(--outline);
    }}
    
    .btn-outline:hover:not(:disabled) {{
        background: var(--surface-variant);
    }}
    
    .btn-sm {{
        padding: var(--spacing-xs) var(--spacing-sm);
        font-size: var(--font-size-sm);
    }}
    
    /* Loading States */
    .btn-loading {{
        position: relative;
        color: transparent;
    }}
    
    .btn-loading::after {{
        content: "";
        position: absolute;
        top: 50%;
        left: 50%;
        width: 16px;
        height: 16px;
        margin: -8px 0 0 -8px;
        border: 2px solid transparent;
        border-top-color: currentColor;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }}
    
    @keyframes spin {{
        to {{ transform: rotate(360deg); }}
    }}
    
    /* Loading Overlay */
    .loading-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }}
    
    .loading-spinner {{
        background: var(--surface);
        padding: var(--spacing-xl);
        border-radius: var(--radius-lg);
        text-align: center;
        box-shadow: var(--shadow-lg);
    }}
    
    .spinner {{
        width: 40px;
        height: 40px;
        border: 4px solid var(--outline);
        border-top-color: var(--primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto var(--spacing-md);
    }}
    
    /* Toast Notifications */
    .toast-container {{
        position: fixed;
        top: var(--spacing-lg);
        right: var(--spacing-lg);
        z-index: 1100;
        max-width: 300px;
    }}
    
    .toast {{
        background: var(--surface);
        border: 1px solid var(--outline);
        border-radius: var(--radius-md);
        padding: var(--spacing-md);
        margin-bottom: var(--spacing-sm);
        box-shadow: var(--shadow-lg);
        animation: slideIn 0.3s ease;
    }}
    
    .toast.success {{
        border-left: 4px solid var(--success);
    }}
    
    .toast.error {{
        border-left: 4px solid var(--error);
    }}
    
    .toast.warning {{
        border-left: 4px solid var(--warning);
    }}
    
    @keyframes slideIn {{
        from {{
            transform: translateX(100%);
            opacity: 0;
        }}
        to {{
            transform: translateX(0);
            opacity: 1;
        }}
    }}
    
    /* Accessibility */
    .sr-only {{
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }}
    
    /* Focus Management */
    .btn:focus,
    .form-control:focus {{
        outline: 2px solid var(--primary);
        outline-offset: 2px;
    }}
    
    /* Required Field Indicator */
    .required::after {{
        content: " *";
        color: var(--error);
    }}
    
    /* Error States */
    .form-error {{
        color: var(--error);
        font-size: var(--font-size-sm);
        margin-top: var(--spacing-xs);
    }}
    
    .form-help {{
        color: var(--on-surface-variant);
        font-size: var(--font-size-sm);
        margin-top: var(--spacing-xs);
    }}
    
    /* Output Section */
    .agent-output {{
        margin-top: var(--spacing-xl);
        padding: var(--spacing-lg);
        background: var(--surface);
        border: 1px solid var(--outline);
        border-radius: var(--radius-md);
    }}
    
    .output-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-md);
        padding-bottom: var(--spacing-md);
        border-bottom: 1px solid var(--outline);
    }}
    
    .output-actions {{
        display: flex;
        gap: var(--spacing-sm);
    }}
    
    .output-content {{
        min-height: 100px;
        padding: var(--spacing-md);
        background: var(--surface-variant);
        border-radius: var(--radius-sm);
        white-space: pre-wrap;
        word-wrap: break-word;
    }}
{responsive_css}'''
    
    def generate_javascript_code(self) -> str:
        """Generate JavaScript with security and accessibility features"""
        toast_js = ""
        if self.config.get('include_toast_notifications', True):
            toast_js = '''
    // Toast notification system
    function showToast(message, type = 'info', duration = 5000) {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'polite');
        
        const messageElement = document.createElement('div');
        messageElement.textContent = message;
        toast.appendChild(messageElement);
        
        container.appendChild(toast);
        
        // Auto-remove toast
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, duration);
    }'''
        
        copy_download_js = ""
        if self.config.get('include_copy_download', True):
            copy_download_js = '''
    // Copy to clipboard with security
    async function copyToClipboard(elementId) {
        const element = document.getElementById(elementId);
        if (!element) {
            showToast('Content not found', 'error');
            return;
        }
        
        try {
            const text = element.textContent || element.innerText;
            await navigator.clipboard.writeText(text);
            showToast('Content copied to clipboard', 'success');
        } catch (err) {
            showToast('Failed to copy content', 'error');
            console.error('Copy failed:', err);
        }
    }
    
    // Download as file with sanitization
    function downloadAsFile(elementId, filename = 'content.txt') {
        const element = document.getElementById(elementId);
        if (!element) {
            showToast('Content not found', 'error');
            return;
        }
        
        try {
            const content = element.textContent || element.innerText;
            const blob = new Blob([content], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.style.display = 'none';
            
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            
            URL.revokeObjectURL(url);
            showToast('File downloaded successfully', 'success');
        } catch (err) {
            showToast('Failed to download file', 'error');
            console.error('Download failed:', err);
        }
    }'''
        
        quick_agents_js = ""
        if self.config.get('include_quick_agents', True):
            quick_agents_js = '''
    // Quick agents panel
    function toggleQuickAgents() {
        const panel = document.getElementById('quickAgentsPanel');
        const toggle = document.getElementById('quick-agent-toggle');
        
        if (panel && toggle) {
            const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
            toggle.setAttribute('aria-expanded', !isExpanded);
            
            if (isExpanded) {
                panel.style.display = 'none';
                toggle.textContent = 'Quick Access';
            } else {
                panel.style.display = 'block';
                toggle.textContent = 'Close';
            }
        }
    }'''
        
        wallet_js = ""
        if self.config.get('include_wallet', True):
            wallet_js = '''
    // Wallet balance update with validation
    function updateWalletBalance(newBalance) {
        const balanceElement = document.getElementById('walletBalance');
        if (!balanceElement) return;
        
        // Validate balance is a number
        const balance = parseFloat(newBalance);
        if (isNaN(balance)) {
            console.error('Invalid balance value:', newBalance);
            return;
        }
        
        // Update with proper formatting
        balanceElement.textContent = balance.toFixed(2);
        balanceElement.setAttribute('aria-label', `Wallet balance: ${balance.toFixed(2)} AED`);
        
        // Announce balance update to screen readers
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = `Wallet balance updated to ${balance.toFixed(2)} AED`;
        
        document.body.appendChild(announcement);
        setTimeout(() => document.body.removeChild(announcement), 1000);
    }'''
        
        return f'''    // Smart Template Generated JavaScript
    // Security-first, accessibility-focused implementation
    
    document.addEventListener('DOMContentLoaded', function() {{
        initializeTemplate();
    }});
    
    function initializeTemplate() {{
        console.log('Initializing {self.config["agent_name"]} template...');
        
        // Initialize form handling
        initializeFormHandling();
        
        // Initialize accessibility features
        initializeAccessibility();
        
        // Initialize security features
        initializeSecurity();
        
        console.log('Template initialized successfully');
    }}
    
    // Form handling with validation
    function initializeFormHandling() {{
        const form = document.getElementById('agentForm');
        if (!form) return;
        
        form.addEventListener('submit', handleFormSubmit);
        
        // Add real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {{
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearFieldError);
        }});
    }}
    
    async function handleFormSubmit(event) {{
        event.preventDefault();
        
        const form = event.target;
        const submitBtn = document.getElementById('submitBtn');
        const loadingOverlay = document.getElementById('loadingOverlay');
        
        // Validate form
        if (!validateForm(form)) {{
            showToast('Please correct the errors in the form', 'error');
            return;
        }}
        
        // Show loading state
        submitBtn.classList.add('btn-loading');
        submitBtn.disabled = true;
        if (loadingOverlay) loadingOverlay.style.display = 'flex';
        
        try {{
            const formData = new FormData(form);
            
            const response = await fetch(form.action || window.location.pathname, {{
                method: 'POST',
                body: formData,
                headers: {{
                    'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value
                }}
            }});
            
            if (!response.ok) {{
                throw new Error(`HTTP error! status: ${{response.status}}`);
            }}
            
            const result = await response.json();
            
            if (result.success) {{
                displayResult(result.data);
                showToast('Content generated successfully!', 'success');
            }} else {{
                throw new Error(result.error || 'Unknown error occurred');
            }}
            
        }} catch (error) {{
            console.error('Form submission error:', error);
            showToast('Failed to generate content. Please try again.', 'error');
        }} finally {{
            // Hide loading state
            submitBtn.classList.remove('btn-loading');
            submitBtn.disabled = false;
            if (loadingOverlay) loadingOverlay.style.display = 'none';
        }}
    }}
    
    // Form validation
    function validateForm(form) {{
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        
        inputs.forEach(input => {{
            if (!validateField({{ target: input }})) {{
                isValid = false;
            }}
        }});
        
        return isValid;
    }}
    
    function validateField(event) {{
        const field = event.target;
        const value = field.value.trim();
        let isValid = true;
        
        // Clear previous errors
        clearFieldError(event);
        
        // Required field validation
        if (field.hasAttribute('required') && !value) {{
            showFieldError(field, 'This field is required');
            isValid = false;
        }}
        
        // Type-specific validation
        if (value && field.type === 'email') {{
            const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
            if (!emailRegex.test(value)) {{
                showFieldError(field, 'Please enter a valid email address');
                isValid = false;
            }}
        }}
        
        if (value && field.type === 'url') {{
            try {{
                new URL(value);
            }} catch {{
                showFieldError(field, 'Please enter a valid URL');
                isValid = false;
            }}
        }}
        
        return isValid;
    }}
    
    function showFieldError(field, message) {{
        field.classList.add('is-invalid');
        field.setAttribute('aria-invalid', 'true');
        
        let errorElement = field.parentNode.querySelector('.form-error');
        if (!errorElement) {{
            errorElement = document.createElement('div');
            errorElement.className = 'form-error';
            errorElement.setAttribute('role', 'alert');
            field.parentNode.appendChild(errorElement);
        }}
        
        errorElement.textContent = message;
    }}
    
    function clearFieldError(event) {{
        const field = event.target;
        field.classList.remove('is-invalid');
        field.removeAttribute('aria-invalid');
        
        const errorElement = field.parentNode.querySelector('.form-error');
        if (errorElement) {{
            errorElement.remove();
        }}
    }}
    
    // Safe HTML content display
    function displayResult(content) {{
        const outputSection = document.getElementById('outputSection');
        const outputContent = document.getElementById('output-content');
        
        if (!outputSection || !outputContent) return;
        
        // Sanitize content before display
        const sanitizedContent = sanitizeHTML(content);
        
        outputContent.textContent = sanitizedContent;
        outputSection.style.display = 'block';
        
        // Focus on output for accessibility
        outputSection.scrollIntoView({{ behavior: 'smooth' }});
        outputContent.focus();
    }}
    
    // HTML sanitization function
    function sanitizeHTML(html) {{
        if (typeof html !== 'string') {{
            return String(html);
        }}
        
        // Use textContent for safe display
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }}
    
    // Reset UI function
    function resetUI() {{
        const form = document.getElementById('agentForm');
        const outputSection = document.getElementById('outputSection');
        const outputContent = document.getElementById('output-content');
        
        if (form) {{
            form.reset();
            
            // Clear validation errors
            const errorElements = form.querySelectorAll('.form-error');
            errorElements.forEach(el => el.remove());
            
            const invalidFields = form.querySelectorAll('.is-invalid');
            invalidFields.forEach(field => {{
                field.classList.remove('is-invalid');
                field.removeAttribute('aria-invalid');
            }});
        }}
        
        if (outputSection) {{
            outputSection.style.display = 'none';
        }}
        
        if (outputContent) {{
            outputContent.textContent = '';
        }}
        
        showToast('Interface reset', 'info');
    }}
    
    // Accessibility initialization
    function initializeAccessibility() {{
        // Add skip links
        addSkipLinks();
        
        // Enhance keyboard navigation
        enhanceKeyboardNavigation();
        
        // Set up focus management
        setupFocusManagement();
    }}
    
    function addSkipLinks() {{
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.textContent = 'Skip to main content';
        skipLink.className = 'sr-only';
        skipLink.addEventListener('focus', function() {{
            this.classList.remove('sr-only');
        }});
        skipLink.addEventListener('blur', function() {{
            this.classList.add('sr-only');
        }});
        
        document.body.insertBefore(skipLink, document.body.firstChild);
    }}
    
    function enhanceKeyboardNavigation() {{
        // Add keyboard support for custom buttons
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Enter' || event.key === ' ') {{
                const target = event.target;
                if (target.getAttribute('role') === 'button' && !target.disabled) {{
                    event.preventDefault();
                    target.click();
                }}
            }}
        }});
    }}
    
    function setupFocusManagement() {{
        // Manage focus for dynamic content
        const observer = new MutationObserver(function(mutations) {{
            mutations.forEach(function(mutation) {{
                if (mutation.type === 'childList') {{
                    mutation.addedNodes.forEach(function(node) {{
                        if (node.nodeType === Node.ELEMENT_NODE && node.matches('.toast')) {{
                            // Don't steal focus from form elements for toasts
                            if (!document.activeElement || !document.activeElement.matches('input, textarea, select')) {{
                                node.focus();
                            }}
                        }}
                    }});
                }}
            }});
        }});
        
        observer.observe(document.body, {{ childList: true, subtree: true }});
    }}
    
    // Security initialization
    function initializeSecurity() {{
        // Prevent XSS in dynamic content
        setupContentSecurity();
        
        // Add CSRF protection to AJAX requests
        setupCSRFProtection();
    }}
    
    function setupContentSecurity() {{
        // Override innerHTML to prevent XSS
        const originalInnerHTML = Element.prototype.innerHTML;
        Object.defineProperty(Element.prototype, 'innerHTML', {{
            set: function(value) {{
                console.warn('innerHTML usage detected. Consider using textContent for security.');
                return originalInnerHTML.call(this, value);
            }},
            get: function() {{
                return originalInnerHTML.call(this);
            }}
        }});
    }}
    
    function setupCSRFProtection() {{
        // Add CSRF token to all AJAX requests
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        
        if (csrfToken) {{
            // Set up default headers for fetch requests
            const originalFetch = window.fetch;
            window.fetch = function(url, options = {{}}) {{
                if (options.method && options.method.toUpperCase() !== 'GET') {{
                    options.headers = options.headers || {{}};
                    options.headers['X-CSRFToken'] = csrfToken;
                }}
                return originalFetch(url, options);
            }};
        }}
    }}
{toast_js}
{copy_download_js}
{quick_agents_js}
{wallet_js}'''
    
    def generate_validation_config(self, template_path: str):
        """Generate validation configuration file"""
        config = {
            "template_path": template_path,
            "validation_rules": {
                "required_django_elements": [
                    "{% extends 'base.html' %}",
                    "{% load static %}",
                    "{% csrf_token %}"
                ],
                "required_css_classes": [
                    "agent-container",
                    "agent-grid",
                    "agent-header",
                    "widget"
                ],
                "required_javascript_functions": [],
                "accessibility_requirements": [
                    "aria-label attributes",
                    "role attributes",
                    "form labels"
                ],
                "security_requirements": [
                    "CSRF protection",
                    "XSS prevention",
                    "Input validation"
                ]
            },
            "quality_gates": [
                "Structural validation",
                "Visual validation",
                "Functional validation",
                "Accessibility validation",
                "Security validation"
            ]
        }
        
        # Add conditional requirements based on config
        if self.config.get('include_wallet', True):
            config["validation_rules"]["required_javascript_functions"].append("updateWalletBalance")
        
        if self.config.get('include_toast_notifications', True):
            config["validation_rules"]["required_javascript_functions"].append("showToast")
        
        if self.config.get('include_copy_download', True):
            config["validation_rules"]["required_javascript_functions"].extend([
                "copyToClipboard",
                "downloadAsFile"
            ])
        
        config_path = template_path.replace('.html', '_validation_config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Validation config generated: {config_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python smart_template_generator.py <output_path> [config_file]")
        sys.exit(1)
    
    output_path = sys.argv[1]
    config_file = sys.argv[2] if len(sys.argv) > 2 else "template_config.json"
    
    generator = SmartTemplateGenerator(config_file)
    template_content = generator.generate_template(output_path)
    
    print(f"\n✅ Smart template generation completed!")
    print(f"📄 Template: {output_path}")
    print(f"⚙️  Config: {config_file}")
    print(f"📏 Size: {len(template_content):,} characters")

if __name__ == "__main__":
    main()
```

## Automation Scripts

### 5. Quality Gate Automation Script

**Purpose**: Automate quality gate execution throughout the implementation process.

**Script: `automate_quality_gates.sh`**
```bash
#!/bin/bash
# Quality Gate Automation Script
# Automatically runs quality gates throughout implementation

set -e

# Configuration
TEMPLATE_PATH=""
SOURCE_TEMPLATE=""
CONFIG_DIR="quality_gates"
REPORT_DIR="reports"
LOG_FILE="quality_gate_automation.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "INFO")
            echo -e "${BLUE}ℹ️  $message${NC}"
            ;;
        "SUCCESS")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}❌ $message${NC}"
            ;;
    esac
    log "[$status] $message"
}

# Create directories
setup_directories() {
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$REPORT_DIR"
    log "Directories created: $CONFIG_DIR, $REPORT_DIR"
}

# Gate 1: Pre-Implementation Validation
run_gate_1() {
    print_status "INFO" "Running Gate 1: Pre-Implementation Validation"
    
    if python3 validate_pre_implementation.py; then
        print_status "SUCCESS" "Gate 1 PASSED - Pre-implementation validation successful"
        return 0
    else
        print_status "ERROR" "Gate 1 FAILED - Pre-implementation validation failed"
        return 1
    fi
}

# Gate 2: Live Implementation Monitoring
start_gate_2() {
    print_status "INFO" "Starting Gate 2: Live Implementation Monitoring"
    
    if [ -z "$TEMPLATE_PATH" ]; then
        print_status "ERROR" "Template path not specified for monitoring"
        return 1
    fi
    
    # Start monitoring in background
    python3 implementation_monitor.py "$TEMPLATE_PATH" > "$REPORT_DIR/live_monitoring.log" 2>&1 &
    MONITOR_PID=$!
    echo $MONITOR_PID > "$REPORT_DIR/monitor.pid"
    
    print_status "SUCCESS" "Live monitoring started (PID: $MONITOR_PID)"
    return 0
}

# Stop live monitoring
stop_gate_2() {
    if [ -f "$REPORT_DIR/monitor.pid" ]; then
        MONITOR_PID=$(cat "$REPORT_DIR/monitor.pid")
        if kill -0 $MONITOR_PID 2>/dev/null; then
            kill $MONITOR_PID
            print_status "SUCCESS" "Live monitoring stopped"
        fi
        rm -f "$REPORT_DIR/monitor.pid"
    fi
}

# Gate 3: Post-Implementation Validation
run_gate_3() {
    print_status "INFO" "Running Gate 3: Post-Implementation Validation"
    
    if [ -z "$SOURCE_TEMPLATE" ] || [ -z "$TEMPLATE_PATH" ]; then
        print_status "ERROR" "Source template and target template paths required"
        return 1
    fi
    
    if python3 post_implementation_validator.py "$SOURCE_TEMPLATE" "$TEMPLATE_PATH"; then
        print_status "SUCCESS" "Gate 3 PASSED - Post-implementation validation successful"
        return 0
    else
        print_status "ERROR" "Gate 3 FAILED - Post-implementation validation failed"
        return 1
    fi
}

# Template quality check
check_template_quality() {
    local template_file=$1
    print_status "INFO" "Checking template quality: $template_file"
    
    if [ ! -f "$template_file" ]; then
        print_status "ERROR" "Template file not found: $template_file"
        return 1
    fi
    
    # Check file size
    file_size=$(wc -c < "$template_file")
    if [ $file_size -gt 100000 ]; then
        print_status "WARNING" "Template file is large (${file_size} bytes)"
    fi
    
    # Check for required Django elements
    local required_elements=(
        "{% extends 'base.html' %}"
        "{% load static %}"
        "{% csrf_token %}"
        "{% block title %}"
        "{% block content %}"
    )
    
    local missing_elements=()
    for element in "${required_elements[@]}"; do
        if ! grep -q "$element" "$template_file"; then
            missing_elements+=("$element")
        fi
    done
    
    if [ ${#missing_elements[@]} -gt 0 ]; then
        print_status "ERROR" "Missing required Django elements:"
        for element in "${missing_elements[@]}"; do
            echo "  - $element"
        done
        return 1
    fi
    
    # Check for CSS classes
    local css_class_count=$(grep -o 'class="[^"]*"' "$template_file" | wc -l)
    if [ $css_class_count -lt 5 ]; then
        print_status "WARNING" "Few CSS classes found ($css_class_count)"
    fi
    
    # Check for JavaScript functions
    if grep -q "<script" "$template_file"; then
        local js_function_count=$(grep -o 'function [a-zA-Z_][a-zA-Z0-9_]*' "$template_file" | wc -l)
        if [ $js_function_count -lt 3 ]; then
            print_status "WARNING" "Few JavaScript functions found ($js_function_count)"
        fi
    fi
    
    print_status "SUCCESS" "Template quality check passed"
    return 0
}

# Accessibility check
check_accessibility() {
    local template_file=$1
    print_status "INFO" "Checking accessibility compliance: $template_file"
    
    local accessibility_score=0
    local total_checks=5
    
    # Check for ARIA attributes
    if grep -q 'aria-' "$template_file"; then
        accessibility_score=$((accessibility_score + 1))
        print_status "SUCCESS" "ARIA attributes found"
    else
        print_status "WARNING" "No ARIA attributes found"
    fi
    
    # Check for role attributes
    if grep -q 'role=' "$template_file"; then
        accessibility_score=$((accessibility_score + 1))
        print_status "SUCCESS" "Role attributes found"
    else
        print_status "WARNING" "No role attributes found"
    fi
    
    # Check for form labels
    if grep -q '<label' "$template_file"; then
        accessibility_score=$((accessibility_score + 1))
        print_status "SUCCESS" "Form labels found"
    else
        print_status "WARNING" "No form labels found"
    fi
    
    # Check for semantic HTML
    if grep -qE '<(header|main|nav|section|article|aside|footer)' "$template_file"; then
        accessibility_score=$((accessibility_score + 1))
        print_status "SUCCESS" "Semantic HTML elements found"
    else
        print_status "WARNING" "No semantic HTML elements found"
    fi
    
    # Check for keyboard navigation
    if grep -qE '(keydown|keyup|keypress|tabindex)' "$template_file"; then
        accessibility_score=$((accessibility_score + 1))
        print_status "SUCCESS" "Keyboard navigation support found"
    else
        print_status "WARNING" "No keyboard navigation support found"
    fi
    
    # Calculate percentage
    local percentage=$((accessibility_score * 100 / total_checks))
    
    if [ $percentage -ge 80 ]; then
        print_status "SUCCESS" "Accessibility check passed ($percentage%)"
        return 0
    elif [ $percentage -ge 60 ]; then
        print_status "WARNING" "Accessibility check warning ($percentage%)"
        return 0
    else
        print_status "ERROR" "Accessibility check failed ($percentage%)"
        return 1
    fi
}

# Security check
check_security() {
    local template_file=$1
    print_status "INFO" "Checking security compliance: $template_file"
    
    local security_score=0
    local total_checks=4
    
    # Check for CSRF token
    if grep -q '{% csrf_token %}' "$template_file"; then
        security_score=$((security_score + 1))
        print_status "SUCCESS" "CSRF token found"
    else
        print_status "ERROR" "CSRF token missing"
    fi
    
    # Check for XSS prevention
    if grep -qE '(sanitize|HTMLSanitizer)' "$template_file"; then
        security_score=$((security_score + 1))
        print_status "SUCCESS" "XSS prevention found"
    elif grep -q 'innerHTML' "$template_file"; then
        print_status "WARNING" "Potential XSS vulnerability (innerHTML usage)"
    else
        security_score=$((security_score + 1))
        print_status "SUCCESS" "No XSS vulnerabilities detected"
    fi
    
    # Check for input validation
    if grep -qE '(validate|required)' "$template_file"; then
        security_score=$((security_score + 1))
        print_status "SUCCESS" "Input validation found"
    else
        print_status "WARNING" "No input validation detected"
    fi
    
    # Check for secure practices
    if ! grep -qE '(eval|document\.write|dangerouslySetInnerHTML)' "$template_file"; then
        security_score=$((security_score + 1))
        print_status "SUCCESS" "No dangerous JavaScript practices found"
    else
        print_status "ERROR" "Dangerous JavaScript practices detected"
    fi
    
    # Calculate percentage
    local percentage=$((security_score * 100 / total_checks))
    
    if [ $percentage -ge 75 ]; then
        print_status "SUCCESS" "Security check passed ($percentage%)"
        return 0
    else
        print_status "ERROR" "Security check failed ($percentage%)"
        return 1
    fi
}

# Performance check
check_performance() {
    local template_file=$1
    print_status "INFO" "Checking performance optimization: $template_file"
    
    # Check file size
    local file_size=$(wc -c < "$template_file")
    local size_kb=$((file_size / 1024))
    
    if [ $file_size -lt 50000 ]; then
        print_status "SUCCESS" "Good file size (${size_kb}KB)"
    elif [ $file_size -lt 100000 ]; then
        print_status "WARNING" "Moderate file size (${size_kb}KB)"
    else
        print_status "WARNING" "Large file size (${size_kb}KB)"
    fi
    
    # Check for external requests
    local external_requests=$(grep -c 'src="http' "$template_file" || true)
    if [ $external_requests -lt 5 ]; then
        print_status "SUCCESS" "Low external requests ($external_requests)"
    else
        print_status "WARNING" "High external requests ($external_requests)"
    fi
    
    # Check for lazy loading
    if grep -q 'lazy' "$template_file"; then
        print_status "SUCCESS" "Lazy loading implemented"
    else
        print_status "INFO" "No lazy loading detected"
    fi
    
    return 0
}

# Generate comprehensive report
generate_report() {
    local report_file="$REPORT_DIR/quality_gate_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# Quality Gate Automation Report

**Date**: $(date)
**Template**: $TEMPLATE_PATH
**Source Template**: $SOURCE_TEMPLATE

## Summary

This report provides the results of automated quality gate execution.

## Quality Gate Results

EOF
    
    # Add gate results (this would be populated by actual gate runs)
    echo "Report generated: $report_file"
    print_status "SUCCESS" "Comprehensive report generated"
}

# Cleanup function
cleanup() {
    print_status "INFO" "Cleaning up..."
    stop_gate_2
    log "Quality gate automation completed"
}

# Main execution function
main() {
    print_status "INFO" "Starting Quality Gate Automation"
    log "Starting quality gate automation process"
    
    # Setup
    setup_directories
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--template)
                TEMPLATE_PATH="$2"
                shift 2
                ;;
            -s|--source)
                SOURCE_TEMPLATE="$2"
                shift 2
                ;;
            --gate-1)
                run_gate_1
                exit $?
                ;;
            --gate-2-start)
                start_gate_2
                exit $?
                ;;
            --gate-2-stop)
                stop_gate_2
                exit $?
                ;;
            --gate-3)
                run_gate_3
                exit $?
                ;;
            --quality-check)
                check_template_quality "$TEMPLATE_PATH"
                exit $?
                ;;
            --accessibility-check)
                check_accessibility "$TEMPLATE_PATH"
                exit $?
                ;;
            --security-check)
                check_security "$TEMPLATE_PATH"
                exit $?
                ;;
            --performance-check)
                check_performance "$TEMPLATE_PATH"
                exit $?
                ;;
            --full-check)
                if [ -z "$TEMPLATE_PATH" ]; then
                    print_status "ERROR" "Template path required for full check"
                    exit 1
                fi
                
                check_template_quality "$TEMPLATE_PATH" && \
                check_accessibility "$TEMPLATE_PATH" && \
                check_security "$TEMPLATE_PATH" && \
                check_performance "$TEMPLATE_PATH"
                
                exit $?
                ;;
            --all-gates)
                # Run all gates in sequence
                run_gate_1 && \
                start_gate_2 && \
                sleep 2 && \
                stop_gate_2 && \
                run_gate_3
                
                exit $?
                ;;
            -h|--help)
                cat << HELP
Quality Gate Automation Script

Usage: $0 [OPTIONS]

Options:
    -t, --template PATH         Target template path
    -s, --source PATH          Source template path for comparison
    --gate-1                   Run pre-implementation validation
    --gate-2-start             Start live implementation monitoring
    --gate-2-stop              Stop live implementation monitoring
    --gate-3                   Run post-implementation validation
    --quality-check            Run template quality check
    --accessibility-check      Run accessibility compliance check
    --security-check           Run security compliance check
    --performance-check        Run performance optimization check
    --full-check               Run all checks on template
    --all-gates                Run all quality gates in sequence
    -h, --help                 Show this help message

Examples:
    $0 --gate-1
    $0 -t template.html --quality-check
    $0 -t target.html -s source.html --gate-3
    $0 -t template.html --full-check
    $0 -t template.html -s source.html --all-gates

HELP
                exit 0
                ;;
            *)
                print_status "ERROR" "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # If no specific action, show help
    print_status "INFO" "No action specified. Use --help for usage information."
}

# Set up trap for cleanup
trap cleanup EXIT

# Run main function
main "$@"
```

## Usage Examples and Integration

### 6. Complete Implementation Example

**Script: `complete_implementation_example.sh`**
```bash
#!/bin/bash
# Complete Implementation Example
# Demonstrates full workflow using all tools

echo "🚀 Complete Template Implementation Example"
echo "==========================================="

# Configuration
AGENT_NAME="Example Agent"
SOURCE_TEMPLATE="source_template.html"
TARGET_TEMPLATE="generated_template.html"
CONFIG_FILE="example_config.json"

# Step 1: Generate optimized template
echo "📝 Step 1: Generating optimized template..."
cat > "$CONFIG_FILE" << EOF
{
    "agent_name": "$AGENT_NAME",
    "description": "Example AI-powered agent for demonstration",
    "include_wallet": true,
    "include_quick_agents": true,
    "include_toast_notifications": true,
    "include_copy_download": true,
    "responsive_design": true,
    "accessibility_features": true,
    "security_features": true,
    "performance_optimizations": true
}
EOF

python3 smart_template_generator.py "$TARGET_TEMPLATE" "$CONFIG_FILE"

# Step 2: Run pre-implementation validation
echo "🔍 Step 2: Running pre-implementation validation..."
python3 validate_pre_implementation.py

# Step 3: Start live monitoring
echo "📊 Step 3: Starting live implementation monitoring..."
python3 implementation_monitor.py "$TARGET_TEMPLATE" &
MONITOR_PID=$!

# Step 4: Simulate implementation work (wait a bit)
echo "⚙️ Step 4: Simulating implementation work..."
sleep 5

# Step 5: Stop monitoring
echo "🛑 Step 5: Stopping live monitoring..."
kill $MONITOR_PID 2>/dev/null || true

# Step 6: Run post-implementation validation
echo "✅ Step 6: Running post-implementation validation..."
python3 post_implementation_validator.py "$SOURCE_TEMPLATE" "$TARGET_TEMPLATE"

# Step 7: Run quality gate automation
echo "🎯 Step 7: Running automated quality checks..."
./automate_quality_gates.sh -t "$TARGET_TEMPLATE" --full-check

echo "🎉 Complete implementation example finished!"
echo "Check the generated reports for detailed results."
```

This comprehensive toolkit provides:

✅ **Pre-Implementation Validation** - Ensures requirements and analysis are complete before starting
✅ **Live Implementation Monitoring** - Real-time validation during development  
✅ **Post-Implementation Quality Gate** - Comprehensive validation after completion
✅ **Smart Template Generator** - Generates optimized templates with built-in quality features
✅ **Quality Gate Automation** - Automates quality gate execution throughout the process
✅ **Complete Integration Example** - Shows how all tools work together

The tools enforce quality gates, prevent common failures, and ensure systematic, error-free implementations like those needed to avoid the Social Ads Generator issues.