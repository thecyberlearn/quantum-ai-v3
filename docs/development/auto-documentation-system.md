# Auto-Documentation System

This system automatically updates README.md, CLAUDE.md, and documentation files whenever significant changes are made to the project.

## Components

### 1. Slash Command (`/update-docs`)
Located: `/home/amit/.claude/slash-commands/update-docs.md`

**Usage in Claude Code:**
```
/update-docs
```

This triggers a comprehensive analysis and update of all documentation files based on recent changes.

### 2. Python Automation Script
Located: `scripts/auto_update_docs.py`

**Manual Usage:**
```bash
python3 scripts/auto_update_docs.py
```

**Features:**
- Analyzes recent git commits (last 5 by default)
- Categorizes changes by type (agents, core, deployment, frontend, backend)
- Updates relevant documentation sections
- Generates update summary
- Only updates when significant changes are detected

### 3. Git Hooks Integration
Setup script: `scripts/setup_git_hooks.sh`

**Install hooks:**
```bash
./scripts/setup_git_hooks.sh
```

**Created hooks:**
- **post-commit**: Auto-updates docs after each commit
- **pre-push**: Checks docs before pushing to remote

### 4. Manual Trigger Script
Located: `scripts/update_docs_manual.sh`

**Usage:**
```bash
./scripts/update_docs_manual.sh
```

## Setup Instructions

### 1. Install Git Hooks (Recommended)
```bash
cd /home/amit/Desktop/quantum_ai
./scripts/setup_git_hooks.sh
```

This enables automatic documentation updates after each commit.

### 2. Test the System
```bash
# Test manual update
./scripts/update_docs_manual.sh

# Check the generated summary
cat docs_update_summary.txt
```

### 3. Configure Slash Command
The slash command is already installed at:
`/home/amit/.claude/slash-commands/update-docs.md`

Use `/update-docs` in Claude Code to trigger comprehensive documentation updates.

## How It Works

### Detection Logic
The system detects when documentation updates are needed by analyzing:

1. **Recent Git Commits**: Looks for keywords like 'add', 'update', 'new', 'feature', 'agent', 'deploy'
2. **Changed Files Categories**:
   - **Agents**: Any agent-related files (triggers agent documentation updates)
   - **Core**: Settings, URLs, views (triggers architecture documentation updates)
   - **Deployment**: Railway, requirements, Docker files (triggers deployment guide updates)
   - **Frontend**: HTML, CSS, JS files (triggers UI documentation updates)

### Update Strategy
- **CLAUDE.md**: Updates project overview, commands, architecture, environment variables
- **README.md**: Updates features, installation, setup instructions
- **docs/ directory**: Updates specific guides based on change categories

### Smart Updates
- Only updates sections actually affected by changes
- Preserves existing documentation structure and style
- Adds timestamps to track last update
- Generates detailed summary of what was changed

## Usage Scenarios

### 1. After Adding New Agent
```bash
# Make your agent changes
git add .
git commit -m "Add new sentiment analysis agent"
# Documentation automatically updates via post-commit hook
```

### 2. Manual Documentation Review
```bash
# Trigger manual update
./scripts/update_docs_manual.sh

# Review changes
git diff

# Commit documentation updates
git add .
git commit -m "📚 Update documentation"
```

### 3. Using Slash Command in Claude Code
```
/update-docs
```
Claude will comprehensively analyze and update all documentation files.

### 4. Before Major Deployment
```bash
# Ensure docs are current before pushing
git push origin main
# pre-push hook automatically checks and updates docs
```

## Configuration

### Customize Update Behavior

Edit `scripts/auto_update_docs.py` to modify:

```python
# Change number of commits to analyze
changes = self.analyze_recent_changes(commit_count=10)

# Modify detection keywords
doc_keywords = ['add', 'update', 'new', 'feature', 'agent', 'deploy', 'fix']

# Customize file categorization
if 'your_pattern' in file:
    categories['your_category'].append(file)
```

### Disable Auto-Updates
```bash
# Remove git hooks
rm .git/hooks/post-commit
rm .git/hooks/pre-push
```

### Auto-Commit Documentation Updates
Uncomment these lines in `.git/hooks/post-commit`:
```bash
# git add *.md docs/ CLAUDE.md README.md docs_update_summary.txt
# git commit -m "📚 Auto-update documentation after recent changes"
```

## Files Updated

The system automatically updates these documentation files:

### Always Checked
- `README.md` (main project readme)
- `CLAUDE.md` (development instructions)
- `docs_update_summary.txt` (generated summary)

### Conditionally Updated
- `docs/development/agent-creation.md` (when agents change)
- `docs/deployment/railway-deployment.md` (when deployment files change)
- `docs/development/setup-guide.md` (when setup requirements change)
- `docs/operations/troubleshooting.md` (when common issues change)

## Troubleshooting

### Script Not Running
```bash
# Check if script is executable
ls -la scripts/auto_update_docs.py
chmod +x scripts/auto_update_docs.py
```

### Git Hooks Not Working
```bash
# Check hook permissions
ls -la .git/hooks/
chmod +x .git/hooks/post-commit
chmod +x .git/hooks/pre-push
```

### No Updates Generated
The system only updates when significant changes are detected. Check:
- Recent commits contain documentation-worthy changes
- Changed files fall into tracked categories
- Git repository is properly initialized

### Slash Command Not Found
Ensure the slash command file exists:
```bash
ls -la /home/amit/.claude/slash-commands/update-docs.md
```

## Best Practices

1. **Review Before Committing**: Always review auto-generated documentation updates
2. **Manual Triggers**: Use manual triggers before major releases
3. **Customize for Your Workflow**: Modify detection logic for your specific needs
4. **Regular Maintenance**: Periodically review and update the automation scripts
5. **Backup Documentation**: Keep backups of important documentation sections

## Summary

This auto-documentation system ensures your project documentation stays current with minimal manual effort. It integrates seamlessly with your git workflow and Claude Code environment, providing comprehensive documentation maintenance automation.

**Key Benefits:**
- ✅ Automatic detection of documentation-worthy changes
- ✅ Smart, targeted updates to relevant sections
- ✅ Integration with git workflow via hooks
- ✅ Claude Code slash command integration
- ✅ Comprehensive change tracking and summaries
- ✅ Minimal manual intervention required