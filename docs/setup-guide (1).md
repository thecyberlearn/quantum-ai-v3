# 📘 setup-guide.md — NetCop AI Hub Agent Frontend Refactor

This guide will help you modularize your AI agent pages using the **Data Analyzer layout as the base template** and build a reusable, theme-driven UI system.

---

## ✅ 1. Define Folder Structure

Create the following Django template structure:

```
templates/
├── base_agent.html
├── agents/
│   ├── data_analyzer.html
│   └── weather_reporter.html
├── components/
│   ├── agent_header.html
│   ├── wallet_card.html
│   ├── how_it_works_widget.html
│   ├── quick_agents_panel.html
│   ├── results_block.html
│   ├── processing_status.html
│   └── ... (other shared components)
static/
└── css/
    └── theme.css
```

---

## 🎨 2. Create `theme.css`

Save this as `static/css/theme.css` and link it in `base_agent.html`.

> This file includes unified tokens: spacing, colors, radius, shadows, typography, responsive styles.

(Refer to the generated `theme.css` in the conversation.)

---

## 📐 3. Create `base_agent.html`

```django
{% extends "base.html" %}
{% load static %}

{% block title %}{{ agent_title }} - NetCop AI Hub{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/theme.css' %}">
{% endblock %}

{% block content %}
<div class="agent-page">
  <div class="agent-container">
    {% include "components/agent_header.html" %}
    {% block agent_main %}{% endblock %}
    {% include "components/processing_status.html" %}
    {% include "components/results_block.html" %}
    {% include "components/quick_agents_panel.html" %}
  </div>
</div>
{% endblock %}
```

---

## 🧩 4. Extract Components

### `agent_header.html`

```django
<div class="agent-header">
  <div>
    <h1 class="agent-title">{{ agent_title }}</h1>
    <p class="agent-subtitle">{{ agent_subtitle }}</p>
  </div>
  <div class="header-controls">
    {% include "components/wallet_card.html" %}
  </div>
</div>
```

### `wallet_card.html`

```django
<div class="wallet-card widget-small" style="margin-bottom: 0;">
  <div class="wallet-header">
    <h3 class="wallet-title">Your Wallet</h3>
    <div class="wallet-icon">💳</div>
  </div>
  <div class="balance-display">
    <div class="balance-amount">
      <span id="walletBalance">{{ user.wallet_balance|floatformat:2 }}</span> AED
    </div>
    <div class="balance-label">Available Balance</div>
  </div>
</div>
```

### `how_it_works_widget.html`

```django
<div class="agent-widget widget-small" style="min-width: min(280px, 100%); max-width: min(280px, 100%); margin-left: auto;">
  <div class="widget-header">
    <h3 class="widget-title">
      <span class="widget-icon">ℹ️</span>
      How It Works
    </h3>
  </div>
  <div class="widget-content">
    {% if steps == "data" %}
      <ol class="info-list">
        <li>Upload your data file</li>
        <li>Choose analysis type</li>
        <li>Get AI-powered insights</li>
        <li>Copy or download results</li>
      </ol>
    {% elif steps == "weather" %}
      <ol class="info-list">
        <li>Enter any city name worldwide</li>
        <li>Choose your preferred report type</li>
        <li>Get real-time weather data</li>
        <li>Copy or download detailed reports</li>
      </ol>
    {% endif %}

    <button class="quick-agent-toggle btn btn-secondary btn-full" onclick="toggleQuickAgents()">
      <span class="toggle-icon">🚀</span>
      <span class="toggle-text">Explore Other Agents</span>
    </button>
  </div>
</div>
```

### `quick_agents_panel.html`

```django
<div class="quick-agents-overlay" id="quickAgentsOverlay" onclick="closeQuickAgents()" aria-hidden="true"></div>
<div class="quick-agents-panel" id="quickAgentsPanel" role="dialog" aria-labelledby="quickAgentsTitle" aria-hidden="true">
  <div class="quick-agents-header">
    <h3 id="quickAgentsTitle">Quick Access to Other Agents</h3>
    <button class="close-panel" onclick="toggleQuickAgents()" aria-label="Close quick agents panel">×</button>
  </div>

  <div class="quick-agents-grid">
    <a href="/agents/data-analyzer/" class="quick-agent-card">
      <div class="agent-icon">📊</div>
      <div class="agent-info">
        <h4>Data Analyzer</h4>
        <p>AI-powered data analysis</p>
        <span class="agent-price">5.0 AED</span>
      </div>
    </a>
    <!-- Add more agents here -->
  </div>

  <div class="quick-agents-footer">
    <a href="{% url 'core:marketplace' %}" class="view-all-agents">View All Agents →</a>
  </div>
</div>
```

### `results_block.html`

```django
<div class="agent-widget widget-wide results-container" id="resultsContainer" style="display: none;">
  <div class="widget-header">
    <h3 class="widget-title">
      <span class="widget-icon">📊</span>
      Analysis Results
    </h3>
    <span class="status-badge">Success</span>
  </div>

  <div class="widget-content">
    <div class="results-content" id="resultsContent"></div>
    <div class="results-actions">
      <button onclick="copyResults()" class="btn btn-primary">📋 Copy</button>
      <button onclick="downloadResults()" class="btn btn-secondary">💾 Download</button>
    </div>
  </div>
</div>
```

### `processing_status.html`

```django
<div id="processingStatus" class="agent-widget widget-wide processing-status">
  <div class="widget-header">
    <h3 class="widget-title">
      <span class="widget-icon">⏳</span>
      Processing Status
    </h3>
  </div>
  <div class="widget-content" style="text-align: center;">
    <div class="status-icon">⏳</div>
    <div class="status-title">Analyzing your data...</div>
    <div class="status-subtitle" id="statusText">Processing file...</div>
  </div>
</div>
```

---

## 🔁 5. Convert `data_analyzer.html` to Use Base Template

```django
{% extends "base_agent.html" %}
{% block agent_main %}
<div class="agent-grid">
  <div class="agent-widget widget-large">
    <!-- Include Data Analyzer form here -->
    <form>...</form>
  </div>
  {% include "components/how_it_works_widget.html" with steps="data" %}
</div>
{% endblock %}
```

---

## 🧠 6. All Other Agents Will:

- Extend `base_agent.html`
- Use `{% block agent_main %}` for agent-specific content
- Include `how_it_works_widget.html` and proper context