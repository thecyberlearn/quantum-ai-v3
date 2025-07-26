#!/usr/bin/env python3
"""
N8N Workflow Management Script for Quantum Tasks AI

This script helps manage N8N workflows for webhook-based agents:
- Import workflows to N8N instance
- Export workflows from N8N instance
- Sync workflows between local files and N8N
- Backup and restore workflows

Usage:
    python manage_n8n_workflows.py import [agent_name]
    python manage_n8n_workflows.py export [agent_name]
    python manage_n8n_workflows.py sync
    python manage_n8n_workflows.py backup
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
import argparse

# Configuration
N8N_BASE_URL = os.getenv('N8N_BASE_URL', 'http://localhost:5678')
N8N_API_KEY = os.getenv('N8N_API_KEY', '')

# Webhook-based agents that need N8N workflows
WEBHOOK_AGENTS = [
    'data_analyzer',
    'social_ads_generator', 
    'job_posting_generator',
    'five_whys_analyzer'
]

class N8NWorkflowManager:
    def __init__(self):
        self.base_url = N8N_BASE_URL
        self.api_key = N8N_API_KEY
        self.headers = {
            'Content-Type': 'application/json',
            'X-N8N-API-KEY': self.api_key
        } if self.api_key else {'Content-Type': 'application/json'}
    
    def get_workflow_path(self, agent_name):
        """Get the workflow directory path for an agent"""
        return Path(f"{agent_name}/n8n_workflows")
    
    def load_workflow_json(self, agent_name, filename='workflow.json'):
        """Load workflow JSON from agent directory"""
        workflow_path = self.get_workflow_path(agent_name) / filename
        if not workflow_path.exists():
            print(f"❌ Workflow file not found: {workflow_path}")
            return None
        
        try:
            with open(workflow_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {workflow_path}: {e}")
            return None
    
    def save_workflow_json(self, agent_name, workflow_data, filename='workflow.json'):
        """Save workflow JSON to agent directory"""
        workflow_path = self.get_workflow_path(agent_name)
        workflow_path.mkdir(exist_ok=True)
        
        filepath = workflow_path / filename
        with open(filepath, 'w') as f:
            json.dump(workflow_data, f, indent=2)
        
        print(f"✅ Workflow saved: {filepath}")
    
    def import_workflow_to_n8n(self, agent_name):
        """Import workflow from local file to N8N instance"""
        print(f"📥 Importing workflow for {agent_name}...")
        
        workflow_data = self.load_workflow_json(agent_name)
        if not workflow_data:
            return False
        
        # Create workflow in N8N
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/workflows",
                headers=self.headers,
                json=workflow_data
            )
            
            if response.status_code == 201:
                workflow_id = response.json().get('id')
                print(f"✅ Workflow imported successfully: ID {workflow_id}")
                
                # Activate the workflow
                activate_response = requests.post(
                    f"{self.base_url}/api/v1/workflows/{workflow_id}/activate",
                    headers=self.headers
                )
                
                if activate_response.status_code == 200:
                    print(f"✅ Workflow activated successfully")
                else:
                    print(f"⚠️ Workflow imported but activation failed: {activate_response.text}")
                
                return True
            else:
                print(f"❌ Import failed: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def export_workflow_from_n8n(self, agent_name, workflow_name=None):
        """Export workflow from N8N instance to local file"""
        print(f"📤 Exporting workflow for {agent_name}...")
        
        if not workflow_name:
            workflow_name = f"{agent_name.replace('_', ' ').title()} Agent"
        
        try:
            # Get all workflows
            response = requests.get(
                f"{self.base_url}/api/v1/workflows",
                headers=self.headers
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to fetch workflows: {response.text}")
                return False
            
            workflows = response.json()
            
            # Find workflow by name
            target_workflow = None
            for workflow in workflows:
                if workflow.get('name', '').lower() == workflow_name.lower():
                    target_workflow = workflow
                    break
            
            if not target_workflow:
                print(f"❌ Workflow '{workflow_name}' not found in N8N")
                print("Available workflows:")
                for wf in workflows:
                    print(f"  - {wf.get('name', 'Unnamed')}")
                return False
            
            # Save workflow with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.save_workflow_json(agent_name, target_workflow, f"workflow_exported_{timestamp}.json")
            
            # Also save as main workflow file
            self.save_workflow_json(agent_name, target_workflow, "workflow.json")
            
            return True
            
        except requests.RequestException as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def backup_all_workflows(self):
        """Backup all workflows to timestamped files"""
        print("🔄 Backing up all workflows...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for agent_name in WEBHOOK_AGENTS:
            workflow_path = self.get_workflow_path(agent_name)
            if (workflow_path / "workflow.json").exists():
                workflow_data = self.load_workflow_json(agent_name)
                if workflow_data:
                    self.save_workflow_json(agent_name, workflow_data, f"workflow_backup_{timestamp}.json")
                    print(f"✅ Backed up {agent_name} workflow")
    
    def sync_workflows(self):
        """Sync workflows between local files and N8N instance"""
        print("🔄 Syncing all workflows...")
        
        for agent_name in WEBHOOK_AGENTS:
            print(f"\n--- {agent_name} ---")
            
            # Check if local workflow exists
            if (self.get_workflow_path(agent_name) / "workflow.json").exists():
                print(f"📁 Local workflow found for {agent_name}")
                
                # Try to import to N8N
                success = self.import_workflow_to_n8n(agent_name)
                if not success:
                    print(f"⚠️ Failed to sync {agent_name} to N8N")
            else:
                print(f"❌ No local workflow found for {agent_name}")
                print(f"💡 Place your workflow JSON file at: {self.get_workflow_path(agent_name)}/workflow.json")
    
    def list_workflows(self):
        """List all workflows in N8N and local directories"""
        print("📋 Listing all workflows...\n")
        
        # List N8N workflows
        try:
            response = requests.get(f"{self.base_url}/api/v1/workflows", headers=self.headers)
            if response.status_code == 200:
                workflows = response.json()
                print(f"🌐 N8N Instance ({len(workflows)} workflows):")
                for wf in workflows:
                    status = "🟢 Active" if wf.get('active') else "🔴 Inactive"
                    print(f"  - {wf.get('name', 'Unnamed')} ({status})")
            else:
                print("❌ Could not connect to N8N instance")
        except requests.RequestException:
            print("❌ Could not connect to N8N instance")
        
        print()
        
        # List local workflows
        print("📁 Local Workflows:")
        for agent_name in WEBHOOK_AGENTS:
            workflow_path = self.get_workflow_path(agent_name)
            if workflow_path.exists():
                files = list(workflow_path.glob("*.json"))
                if files:
                    print(f"  {agent_name}: {len(files)} files")
                    for file in files:
                        print(f"    - {file.name}")
                else:
                    print(f"  {agent_name}: No workflow files")
            else:
                print(f"  {agent_name}: Directory not found")

def main():
    parser = argparse.ArgumentParser(description='N8N Workflow Management for Quantum Tasks AI')
    parser.add_argument('action', choices=['import', 'export', 'sync', 'backup', 'list'], 
                        help='Action to perform')
    parser.add_argument('agent', nargs='?', choices=WEBHOOK_AGENTS, 
                        help='Specific agent to operate on (for import/export)')
    parser.add_argument('--workflow-name', help='Workflow name in N8N (for export)')
    
    args = parser.parse_args()
    
    manager = N8NWorkflowManager()
    
    if args.action == 'import':
        if not args.agent:
            print("❌ Please specify an agent name for import")
            print(f"Available agents: {', '.join(WEBHOOK_AGENTS)}")
            sys.exit(1)
        success = manager.import_workflow_to_n8n(args.agent)
        sys.exit(0 if success else 1)
    
    elif args.action == 'export':
        if not args.agent:
            print("❌ Please specify an agent name for export")
            print(f"Available agents: {', '.join(WEBHOOK_AGENTS)}")
            sys.exit(1)
        success = manager.export_workflow_from_n8n(args.agent, args.workflow_name)
        sys.exit(0 if success else 1)
    
    elif args.action == 'sync':
        manager.sync_workflows()
    
    elif args.action == 'backup':
        manager.backup_all_workflows()
    
    elif args.action == 'list':
        manager.list_workflows()

if __name__ == '__main__':
    main()