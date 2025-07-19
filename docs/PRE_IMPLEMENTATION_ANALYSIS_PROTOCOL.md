# Pre-Implementation Analysis Protocol

A comprehensive 3-phase approach to ensure thorough analysis before making any template changes.

## Overview

This protocol prevents the failures that occurred with the Social Ads Generator by ensuring complete understanding of requirements and existing implementations before any code changes are made.

## Phase 1: Complete Requirements Analysis

### 1.1 User Requirements Deep Dive

**Requirements Extraction Process:**
1. **Read the entire user request** multiple times
2. **Identify explicit requirements** (what they directly stated)
3. **Identify implicit requirements** (what they likely mean)
4. **Ask clarifying questions** if anything is unclear
5. **Document all requirements** in a structured format

**Requirements Documentation Template:**
```markdown
# Requirements Analysis: [Task Name]

## Explicit Requirements
- [ ] Requirement 1: [Description]
- [ ] Requirement 2: [Description]
- [ ] Requirement 3: [Description]

## Implicit Requirements
- [ ] Implied Requirement 1: [Description and reasoning]
- [ ] Implied Requirement 2: [Description and reasoning]

## Success Criteria
- [ ] Visual: [What should it look like?]
- [ ] Functional: [How should it behave?]
- [ ] Technical: [What technical standards must be met?]

## Constraints
- [ ] Technical constraints: [List]
- [ ] Design constraints: [List]
- [ ] Performance constraints: [List]

## Questions for Clarification
- [ ] Question 1: [What needs clarification?]
- [ ] Question 2: [What assumptions need verification?]
```

### 1.2 Context Understanding

**Environmental Analysis:**
- [ ] What is the current state of the target system?
- [ ] What other templates exist that might be relevant?
- [ ] What is the overall design system and architecture?
- [ ] What are the user's expectations based on past interactions?
- [ ] What are the business requirements and constraints?

**Stakeholder Analysis:**
- [ ] Who is the primary user?
- [ ] What is their technical expertise level?
- [ ] What are their preferences and priorities?
- [ ] What is their tolerance for iterative changes?
- [ ] What is their timeline and urgency level?

### 1.3 Scope Definition

**Scope Boundary Documentation:**
```markdown
# Scope Definition: [Task Name]

## In Scope
- [ ] Specific changes to be made
- [ ] Components to be modified
- [ ] Features to be implemented
- [ ] Standards to be followed

## Out of Scope
- [ ] Changes not requested
- [ ] Components not to be modified
- [ ] Features not to be implemented
- [ ] Standards not applicable

## Assumptions
- [ ] Assumption 1: [Description]
- [ ] Assumption 2: [Description]
- [ ] Assumption 3: [Description]

## Dependencies
- [ ] External dependencies
- [ ] Internal dependencies
- [ ] Technical dependencies
- [ ] Resource dependencies
```

## Phase 2: Complete Reference Analysis

### 2.1 Source Template Deep Analysis

**Comprehensive Template Reading Protocol:**
1. **Read the entire template** from start to finish
2. **Create a mental model** of the overall structure
3. **Re-read focusing on specific sections** (HTML, CSS, JS)
4. **Document every component** and its purpose
5. **Map relationships** between components
6. **Identify patterns** and conventions used

**Template Analysis Worksheet:**
```markdown
# Template Analysis: [Template Name]

## Overall Structure
- **Template extends**: [Base template]
- **Block structure**: [List of Django blocks]
- **Main sections**: [List of major sections]
- **Total lines**: [Count]
- **Complexity level**: [Low/Medium/High]

## HTML Structure Analysis
### Header Section
- **Elements**: [List all elements]
- **Classes**: [List all CSS classes]
- **IDs**: [List all HTML IDs]
- **ARIA attributes**: [List accessibility attributes]
- **Structure pattern**: [Describe the layout pattern]

### Main Content Section
- **Elements**: [List all elements]
- **Classes**: [List all CSS classes]
- **IDs**: [List all HTML IDs]
- **Form elements**: [List all form elements]
- **Structure pattern**: [Describe the layout pattern]

### Sidebar Section
- **Elements**: [List all elements]
- **Classes**: [List all CSS classes]
- **IDs**: [List all HTML IDs]
- **Widget structure**: [Describe widget organization]
- **Structure pattern**: [Describe the layout pattern]

### Footer/Additional Sections
- **Elements**: [List all elements]
- **Classes**: [List all CSS classes]
- **IDs**: [List all HTML IDs]
- **Purpose**: [Describe purpose of each section]

## CSS Architecture Analysis
### Design Tokens
- **Color variables**: [List all color variables]
- **Spacing variables**: [List all spacing variables]
- **Typography variables**: [List all typography variables]
- **Border radius variables**: [List all radius variables]
- **Shadow variables**: [List all shadow variables]

### Component Classes
- **Layout classes**: [List classes for layout]
- **Component classes**: [List classes for components]
- **State classes**: [List classes for states]
- **Utility classes**: [List utility classes]

### Responsive Design
- **Breakpoints**: [List all media queries]
- **Mobile changes**: [List mobile-specific changes]
- **Tablet changes**: [List tablet-specific changes]
- **Desktop changes**: [List desktop-specific changes]

## JavaScript Analysis
### Functions
- **Function 1**: [Name, purpose, parameters, return value]
- **Function 2**: [Name, purpose, parameters, return value]
- **Function 3**: [Name, purpose, parameters, return value]

### Event Listeners
- **Event 1**: [Element, event type, handler function]
- **Event 2**: [Element, event type, handler function]
- **Event 3**: [Element, event type, handler function]

### DOM Manipulation
- **Elements modified**: [List elements that are modified]
- **Classes added/removed**: [List dynamic class changes]
- **Content updates**: [List content that gets updated]

### State Management
- **Global variables**: [List global variables]
- **State tracking**: [List state variables]
- **Data flow**: [Describe how data flows]

## Interaction Patterns
### User Interactions
- **Click interactions**: [List all clickable elements]
- **Form interactions**: [List all form interactions]
- **Hover effects**: [List all hover effects]
- **Focus management**: [List focus management]

### System Interactions
- **API calls**: [List all API interactions]
- **Data persistence**: [List data storage/retrieval]
- **External integrations**: [List external integrations]

## Performance Considerations
- **Loading performance**: [Notes on loading speed]
- **Runtime performance**: [Notes on runtime efficiency]
- **Memory usage**: [Notes on memory consumption]
- **Network requests**: [List all network requests]

## Security Considerations
- **Input validation**: [List input validation measures]
- **Output sanitization**: [List output sanitization measures]
- **XSS prevention**: [List XSS prevention measures]
- **CSRF protection**: [List CSRF protection measures]

## Accessibility Features
- **ARIA attributes**: [List all ARIA attributes]
- **Keyboard navigation**: [List keyboard navigation support]
- **Screen reader support**: [List screen reader features]
- **Color contrast**: [Notes on color contrast]

## Browser Compatibility
- **Supported browsers**: [List supported browsers]
- **Fallbacks**: [List fallback implementations]
- **Polyfills**: [List polyfills used]
- **Progressive enhancement**: [List progressive enhancement features]
```

### 2.2 Target Template Current State Analysis

**Current State Documentation:**
```markdown
# Current State Analysis: [Target Template]

## Existing Implementation
- **Current approach**: [Describe current implementation]
- **Strengths**: [List what works well]
- **Weaknesses**: [List what doesn't work well]
- **Technical debt**: [List technical debt items]

## Component Inventory
- **Existing components**: [List all current components]
- **Reusable components**: [List components that can be reused]
- **Components to replace**: [List components that need replacement]
- **Components to remove**: [List components that should be removed]

## Code Quality Assessment
- **Code organization**: [Assessment of code structure]
- **Naming conventions**: [Assessment of naming patterns]
- **Documentation**: [Assessment of code documentation]
- **Maintainability**: [Assessment of maintainability]

## Performance Analysis
- **Current performance**: [Metrics and observations]
- **Bottlenecks**: [Performance bottlenecks identified]
- **Optimization opportunities**: [List optimization opportunities]
- **Resource usage**: [Current resource usage]
```

### 2.3 Gap Analysis and Mapping

**Detailed Gap Analysis:**
```markdown
# Gap Analysis: [Source] → [Target]

## Structural Differences
| Component | Source | Target | Gap | Priority |
|-----------|---------|---------|-----|----------|
| Header | [Source structure] | [Target structure] | [Gap description] | [High/Medium/Low] |
| Main Content | [Source structure] | [Target structure] | [Gap description] | [High/Medium/Low] |
| Sidebar | [Source structure] | [Target structure] | [Gap description] | [High/Medium/Low] |
| Footer | [Source structure] | [Target structure] | [Gap description] | [High/Medium/Low] |

## Styling Differences
| Style Category | Source | Target | Gap | Priority |
|----------------|---------|---------|-----|----------|
| Color Scheme | [Source colors] | [Target colors] | [Gap description] | [High/Medium/Low] |
| Typography | [Source typography] | [Target typography] | [Gap description] | [High/Medium/Low] |
| Spacing | [Source spacing] | [Target spacing] | [Gap description] | [High/Medium/Low] |
| Layout | [Source layout] | [Target layout] | [Gap description] | [High/Medium/Low] |

## Functional Differences
| Functionality | Source | Target | Gap | Priority |
|---------------|---------|---------|-----|----------|
| User Interactions | [Source interactions] | [Target interactions] | [Gap description] | [High/Medium/Low] |
| Data Handling | [Source data handling] | [Target data handling] | [Gap description] | [High/Medium/Low] |
| State Management | [Source state] | [Target state] | [Gap description] | [High/Medium/Low] |
| Error Handling | [Source errors] | [Target errors] | [Gap description] | [High/Medium/Low] |

## Missing Elements
- [ ] **Missing HTML elements**: [List]
- [ ] **Missing CSS classes**: [List]
- [ ] **Missing JavaScript functions**: [List]
- [ ] **Missing interactions**: [List]
- [ ] **Missing accessibility features**: [List]

## Excessive Elements
- [ ] **Unnecessary HTML elements**: [List]
- [ ] **Unused CSS classes**: [List]
- [ ] **Redundant JavaScript functions**: [List]
- [ ] **Unwanted interactions**: [List]
- [ ] **Obsolete features**: [List]
```

## Phase 3: Implementation Planning

### 3.1 Change Strategy Definition

**Change Strategy Matrix:**
```markdown
# Change Strategy: [Task Name]

## Strategic Approach
- **Overall strategy**: [Comprehensive rewrite / Incremental updates / Hybrid approach]
- **Risk tolerance**: [Low / Medium / High]
- **Timeline**: [Immediate / Short-term / Long-term]
- **Quality vs. Speed**: [Quality first / Balanced / Speed first]

## Implementation Approach
- **Method**: [Single comprehensive update / Staged implementation / Iterative development]
- **Backup strategy**: [Full backup / Incremental backup / Version control]
- **Testing approach**: [Comprehensive testing / Targeted testing / Minimal testing]
- **Rollback plan**: [Immediate rollback / Staged rollback / No rollback]

## Resource Requirements
- **Time estimate**: [Hours/days required]
- **Complexity level**: [Low / Medium / High]
- **Risk level**: [Low / Medium / High]
- **Dependencies**: [List external dependencies]
```

### 3.2 Detailed Implementation Plan

**Step-by-Step Implementation Plan:**
```markdown
# Implementation Plan: [Task Name]

## Phase 1: Foundation
### Step 1.1: Environment Setup
- [ ] Create backup of current implementation
- [ ] Set up development environment
- [ ] Prepare testing environment
- [ ] Document current state

### Step 1.2: Structure Preparation
- [ ] Analyze HTML structure requirements
- [ ] Plan CSS architecture changes
- [ ] Design JavaScript function updates
- [ ] Prepare component templates

## Phase 2: Core Implementation
### Step 2.1: HTML Structure Updates
- [ ] Update header structure
- [ ] Modify main content layout
- [ ] Adjust sidebar components
- [ ] Update footer elements

### Step 2.2: CSS Architecture Implementation
- [ ] Implement design token system
- [ ] Update component classes
- [ ] Add responsive design rules
- [ ] Implement interaction styles

### Step 2.3: JavaScript Functionality
- [ ] Update existing functions
- [ ] Add new functions
- [ ] Implement event listeners
- [ ] Add state management

## Phase 3: Integration and Testing
### Step 3.1: Component Integration
- [ ] Test individual components
- [ ] Test component interactions
- [ ] Verify responsive design
- [ ] Check accessibility compliance

### Step 3.2: System Integration
- [ ] Test full system functionality
- [ ] Verify performance requirements
- [ ] Test cross-browser compatibility
- [ ] Validate security measures

## Phase 4: Validation and Deployment
### Step 4.1: Final Validation
- [ ] Compare with source template
- [ ] Verify all requirements met
- [ ] Test user experience
- [ ] Document changes made

### Step 4.2: Deployment
- [ ] Deploy to production
- [ ] Monitor for issues
- [ ] Gather user feedback
- [ ] Document lessons learned
```

### 3.3 Risk Assessment and Mitigation

**Risk Analysis:**
```markdown
# Risk Assessment: [Task Name]

## High Risk Items
### Risk 1: [Risk Description]
- **Probability**: [High / Medium / Low]
- **Impact**: [High / Medium / Low]
- **Mitigation**: [Mitigation strategy]
- **Contingency**: [Contingency plan]

### Risk 2: [Risk Description]
- **Probability**: [High / Medium / Low]
- **Impact**: [High / Medium / Low]
- **Mitigation**: [Mitigation strategy]
- **Contingency**: [Contingency plan]

## Medium Risk Items
### Risk 3: [Risk Description]
- **Probability**: [High / Medium / Low]
- **Impact**: [High / Medium / Low]
- **Mitigation**: [Mitigation strategy]
- **Contingency**: [Contingency plan]

## Low Risk Items
### Risk 4: [Risk Description]
- **Probability**: [High / Medium / Low]
- **Impact**: [High / Medium / Low]
- **Mitigation**: [Mitigation strategy]
- **Contingency**: [Contingency plan]

## Risk Mitigation Strategies
- [ ] **Backup and Recovery**: [Strategy]
- [ ] **Incremental Testing**: [Strategy]
- [ ] **Rollback Plan**: [Strategy]
- [ ] **Monitoring**: [Strategy]
- [ ] **Communication**: [Strategy]
```

## Protocol Implementation Checklist

### Pre-Analysis Phase
- [ ] User requirements fully understood
- [ ] Context and environment analyzed
- [ ] Scope clearly defined
- [ ] Stakeholder expectations set

### Analysis Phase
- [ ] Source template completely analyzed
- [ ] Target template current state documented
- [ ] Gap analysis completed
- [ ] Change requirements identified

### Planning Phase
- [ ] Change strategy defined
- [ ] Implementation plan created
- [ ] Risk assessment completed
- [ ] Resource requirements identified

### Validation Phase
- [ ] Analysis validated with stakeholders
- [ ] Plan reviewed and approved
- [ ] Risks acknowledged and accepted
- [ ] Implementation authorized

## Templates and Tools

### Requirements Analysis Template
```markdown
# Requirements Analysis: [Date] - [Task Name]

## User Request
**Original Request**: [Exact quote from user]
**Clarifications**: [Any clarifications received]

## Explicit Requirements
1. [Requirement 1]
2. [Requirement 2]
3. [Requirement 3]

## Implicit Requirements
1. [Implied requirement 1] - [Reasoning]
2. [Implied requirement 2] - [Reasoning]

## Success Criteria
- **Visual**: [What should it look like?]
- **Functional**: [How should it behave?]
- **Technical**: [What technical standards?]

## Assumptions
1. [Assumption 1]
2. [Assumption 2]

## Questions for User
1. [Question 1]
2. [Question 2]
```

### Analysis Validation Checklist
```markdown
# Analysis Validation: [Task Name]

## Completeness Check
- [ ] All requirements identified
- [ ] All components analyzed
- [ ] All gaps identified
- [ ] All risks assessed

## Accuracy Check
- [ ] Requirements correctly understood
- [ ] Analysis is accurate
- [ ] Gaps are real
- [ ] Risks are valid

## Feasibility Check
- [ ] Requirements are achievable
- [ ] Timeline is realistic
- [ ] Resources are available
- [ ] Constraints are manageable

## Stakeholder Check
- [ ] User expectations aligned
- [ ] Business requirements met
- [ ] Technical constraints considered
- [ ] Quality standards maintained
```

This protocol ensures that every implementation starts with a complete understanding of what needs to be done, preventing the issues that occurred with the Social Ads Generator initial implementation.