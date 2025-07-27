# Quantum Tasks AI Subagents Guide

This document describes the specialized AI subagents created for the Quantum Tasks AI platform to improve development speed and code quality.

## Available Subagents

### 1. Django Expert (`django-expert`)
**Specialization**: Django development tasks, models, views, URLs, migrations
**Auto-triggers**: Django model creation, view implementation, URL configuration, migration issues
**Use cases**:
- Creating new Django models with proper relationships
- Implementing views with authentication and permissions
- Setting up URL routing with proper namespacing
- Database operations and migrations
- Django settings configuration

### 2. Agent Architect (`agent-architect`)
**Specialization**: Creating new AI agents for the marketplace
**Auto-triggers**: "Create new agent" requests, agent functionality extension
**Use cases**:
- Planning and implementing new marketplace agents
- Setting up agent processors (webhook/API types)
- Implementing component-based templates
- Marketplace catalog integration
- Agent testing and validation

### 3. Django Debugger (`django-debugger`)
**Specialization**: Debugging Django errors and issues
**Auto-triggers**: Django errors, test failures, migration problems, template issues
**Use cases**:
- Fixing Django runtime errors
- Resolving database and migration issues
- Debugging template rendering problems
- Troubleshooting authentication and permission issues
- Performance issue diagnosis

### 4. Security Auditor (`security-auditor`)
**Specialization**: Security reviews and vulnerability assessment
**Auto-triggers**: Security reviews, pre-deployment checks, payment features
**Use cases**:
- Comprehensive security audits
- Authentication and authorization reviews
- Input validation and XSS prevention
- File upload security assessment
- Payment processing security review
- Configuration security checks

### 5. Template Optimizer (`template-optimizer`)
**Specialization**: Frontend template and UI optimization
**Auto-triggers**: Template rendering issues, responsive design problems, UI improvements
**Use cases**:
- Component-based template optimization
- CSS and JavaScript performance improvements
- Responsive design fixes
- Accessibility enhancements
- Template standardization

## How to Use Subagents

### Automatic Invocation
Subagents are automatically invoked by Claude Code when tasks match their expertise:

```
> I need to create a new sentiment analysis agent
# Automatically invokes agent-architect subagent

> There's a Django migration error
# Automatically invokes django-debugger subagent

> Review this code for security issues
# Automatically invokes security-auditor subagent
```

### Explicit Invocation
You can specifically request a subagent:

```
> Use the django-expert subagent to optimize this view
> Have the template-optimizer subagent improve the mobile layout
> Ask the security-auditor subagent to review authentication
```

### Chaining Subagents
For complex workflows, multiple subagents can work together:

```
> Use agent-architect to create the agent, then django-expert to optimize the database models, then security-auditor to review security
```

## Subagent Capabilities

### Django Expert
- ✅ Django model creation with relationships
- ✅ View implementation with authentication
- ✅ URL routing and namespacing
- ✅ Database migrations and optimization
- ✅ Django settings and configuration
- ✅ Template context and form handling

### Agent Architect
- ✅ Complete agent development workflow
- ✅ BaseAgent and BaseAgentProcessor patterns
- ✅ Webhook (N8N) and API agent types
- ✅ Component-based template implementation
- ✅ Dynamic pricing integration
- ✅ Marketplace catalog integration

### Django Debugger
- ✅ Error diagnosis and root cause analysis
- ✅ Database and migration troubleshooting
- ✅ Template rendering issue resolution
- ✅ Authentication and permission debugging
- ✅ Performance issue identification
- ✅ Production deployment debugging

### Security Auditor
- ✅ Comprehensive security assessments
- ✅ Input validation and XSS prevention
- ✅ Authentication security reviews
- ✅ File upload security checks
- ✅ Payment processing security
- ✅ Configuration security audits

### Template Optimizer
- ✅ Component architecture optimization
- ✅ CSS and JavaScript performance
- ✅ Responsive design improvements
- ✅ Accessibility enhancements
- ✅ Template standardization
- ✅ Cross-browser compatibility

## Best Practices

### When to Use Each Subagent

**Django Expert** - Use for:
- Creating new Django apps or models
- Implementing views and URL patterns
- Database schema changes
- Django configuration issues

**Agent Architect** - Use for:
- Building new marketplace agents
- Extending existing agent functionality
- Template component implementation
- Agent integration and testing

**Django Debugger** - Use for:
- Any Django error or unexpected behavior
- Performance issues
- Test failures
- Production deployment problems

**Security Auditor** - Use for:
- Before production deployments
- After implementing authentication features
- When handling payment processing
- Regular security reviews

**Template Optimizer** - Use for:
- UI/UX improvements
- Mobile responsiveness issues
- Template performance problems
- Accessibility enhancements

### Subagent Coordination

For complex tasks, subagents work together efficiently:

1. **New Agent Development Flow**:
   - `agent-architect` → Plan and create agent structure
   - `django-expert` → Optimize models and views
   - `template-optimizer` → Perfect the UI/UX
   - `security-auditor` → Security review
   - `django-debugger` → Test and fix any issues

2. **Bug Fix Flow**:
   - `django-debugger` → Identify and fix the issue
   - `security-auditor` → Ensure fix doesn't introduce vulnerabilities
   - `template-optimizer` → Optimize any UI changes

3. **Feature Enhancement Flow**:
   - `django-expert` → Backend implementation
   - `template-optimizer` → Frontend improvements
   - `security-auditor` → Security validation

## Benefits of Using Subagents

### Increased Development Speed
- ✅ **Faster Agent Creation**: Complete agent development in minutes vs hours
- ✅ **Rapid Debugging**: Systematic error identification and resolution
- ✅ **Quick Security Reviews**: Automated security best practices
- ✅ **Efficient Template Work**: Component-based optimization

### Improved Code Quality
- ✅ **Django Best Practices**: Following established patterns
- ✅ **Security Standards**: Built-in security considerations
- ✅ **Template Consistency**: Standardized component architecture
- ✅ **Performance Optimization**: Automated performance improvements

### Knowledge Consistency
- ✅ **Project-Specific Expertise**: Deep understanding of your codebase
- ✅ **Pattern Recognition**: Consistent application of established patterns
- ✅ **Quality Assurance**: Automated quality checks and validations

## Configuration

Subagents are stored in `.claude/agents/` and automatically available in this project. Each subagent has:

- **Focused expertise** in specific areas
- **Proactive invocation** based on task recognition  
- **Project-specific knowledge** of your architecture
- **Quality standards** enforcement
- **Security-first** approach

## Getting Started

The subagents are ready to use immediately. Simply describe your task and Claude Code will automatically select and invoke the most appropriate subagent(s) for the job.

Example workflows:
```
> "Create a new document analysis agent"
# → agent-architect will handle the complete agent creation

> "Fix this Django migration error" 
# → django-debugger will diagnose and resolve the issue

> "Make this template mobile-responsive"
# → template-optimizer will improve the responsive design

> "Review this code for security issues"
# → security-auditor will perform a comprehensive security review
```

The subagents work seamlessly together to provide expert-level assistance for any development task in your Quantum Tasks AI marketplace platform.