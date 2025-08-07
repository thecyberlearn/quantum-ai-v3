# Agent Request Template

Use this template when requesting new agents to ensure all necessary information is provided for quick, error-free agent creation.

## How to Use This Template

1. **Copy the template below**
2. **Fill in all required fields**  
3. **Provide to Claude Code** with the request "Create agent using this template"
4. **Claude will handle** JSON config creation, populate_agents execution, and deployment

---

## Agent Request Template

```markdown
## New Agent Request

**Agent Name**: [Enter the display name for the agent]
**Type**: [Webhook OR Direct Access]
**Category**: [Choose from: analysis, career-education, document-processing, human-resources, marketing, consulting]
**Price**: [X.XX AED or 0.0 for FREE]
**Short Description**: [Brief 1-line description for marketplace]
**Full Description**: [Detailed description of what the agent does and its benefits]

### For Webhook Agents Only:
**Form Fields**: 
- Field 1: [name: field_name, type: text/textarea/select/file/url/checkbox, label: "Display Label", required: true/false]
- Field 2: [name: field_name, type: text/textarea/select/file/url/checkbox, label: "Display Label", required: true/false]
- [Add more fields as needed]

**N8N Webhook URL**: [Your N8N webhook endpoint URL]

### For Direct Access Agents Only:
**External Form URL**: [JotForm, Google Forms, or other external form URL]
**Custom Template Needed**: [Yes/No - specify if you need custom styling/layout]
**Custom Views Needed**: [Yes/No - specify if you need special marketplace behavior]

### Optional Information:
**Special Requirements**: [Any unique features or customizations needed]
**Integration Notes**: [Any special setup or configuration details]
```

---

## Available Categories

**Choose from these existing categories** (avoid creating new ones):

- 🧠 **`analysis`** - Problem-solving, SWOT analysis, strategic analysis tools
- 🎓 **`career-education`** - Career guidance, educational resources, professional development  
- 📄 **`document-processing`** - PDF analysis, file processing, document tools
- 💼 **`human-resources`** - Job postings, HR automation, talent management
- 📢 **`marketing`** - Social ads, branding, content marketing, advertising
- 💼 **`consulting`** - Business consultation, strategy services, expert advice

---

## Form Field Types (Webhook Agents)

- **`text`** - Single-line text input
- **`textarea`** - Multi-line text input
- **`select`** - Dropdown (requires options array)
- **`file`** - File upload with drag-and-drop
- **`url`** - URL input with validation
- **`checkbox`** - Boolean true/false

---

## Example Requests

### Example 1: Webhook Agent
```markdown
## New Agent Request

**Agent Name**: Email Campaign Optimizer
**Type**: Webhook
**Category**: marketing  
**Price**: 4.0 AED
**Short Description**: AI-powered email campaign optimization and A/B testing
**Full Description**: Optimize your email campaigns with AI analysis of subject lines, content, and send times. Get recommendations for better open rates and conversions.

### Form Fields:
- Field 1: [name: email_subject, type: text, label: "Email Subject Line", required: true]
- Field 2: [name: email_content, type: textarea, label: "Email Content", required: true]
- Field 3: [name: target_audience, type: select, label: "Target Audience", required: true, options: [{"value": "b2b", "label": "Business"}, {"value": "b2c", "label": "Consumer"}]]

**N8N Webhook URL**: http://localhost:5678/webhook/email-optimizer
```

### Example 2: Direct Access Agent
```markdown
## New Agent Request  

**Agent Name**: Financial Planning Consultant
**Type**: Direct Access
**Category**: consulting
**Price**: 0.0 AED
**Short Description**: Professional financial planning and investment consultation
**Full Description**: Get expert financial advice tailored to your goals. Our certified financial planners provide personalized investment strategies and retirement planning.

### For Direct Access Agents:
**External Form URL**: https://agent.jotform.com/financial-planning-form-id
**Custom Template Needed**: No
**Custom Views Needed**: No
```

---

## What Happens Next

After you provide the completed template:

1. ✅ **Claude creates JSON config** in `agents/configs/agents/`
2. ✅ **Runs populate_agents command** to add agent to database  
3. ✅ **Agent appears in marketplace** automatically
4. ✅ **Creates any needed templates/views** (for Direct Access agents)
5. ✅ **Updates marketplace integration** if needed
6. ✅ **Commits changes** and makes them Railway-ready

**No additional work needed on your part!** 🚀

---

## Tips for Better Requests

- ✅ **Use existing categories** - Avoid creating new ones unless absolutely necessary
- ✅ **Be specific** - Clear descriptions help users understand the agent's value
- ✅ **Test external forms** - Ensure JotForm/external URLs are working before requesting
- ✅ **Consider pricing** - Free agents get more usage, paid agents need clear value proposition
- ✅ **Think about fields** - For webhook agents, plan your form fields carefully

---

*For comprehensive agent creation details, see `docs/AGENT_CREATION.md`*