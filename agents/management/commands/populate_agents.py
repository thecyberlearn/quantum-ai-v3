from django.core.management.base import BaseCommand
from agents.models import AgentCategory, Agent

class Command(BaseCommand):
    help = 'Populate all agents and categories - ensures database consistency between local and production'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Populating all agents and categories...'))
        self.stdout.write('')
        
        # Track creation statistics
        categories_created = 0
        agents_created = 0
        
        # Define all categories
        categories_data = [
            {
                'slug': 'analysis',
                'name': 'Analysis & Problem Solving',
                'description': 'AI-powered analysis tools for problem-solving and decision making',
                'icon': '🧠'
            },
            {
                'slug': 'career-education', 
                'name': 'Career & Education',
                'description': 'Professional career guidance and educational resources',
                'icon': '🎓'
            },
            {
                'slug': 'document-processing',
                'name': 'Document Processing', 
                'description': 'AI-powered document analysis and processing tools',
                'icon': '📄'
            },
            {
                'slug': 'human-resources',
                'name': 'Human Resources',
                'description': 'HR automation and talent management solutions',
                'icon': '💼'
            },
            {
                'slug': 'marketing',
                'name': 'Marketing & Advertising',
                'description': 'AI-powered marketing tools and advertising solutions',
                'icon': '📢'
            }
        ]
        
        # Create categories
        categories = {}
        for category_data in categories_data:
            category, created = AgentCategory.objects.get_or_create(
                slug=category_data['slug'],
                defaults={
                    'name': category_data['name'],
                    'description': category_data['description'],
                    'icon': category_data['icon']
                }
            )
            categories[category_data['slug']] = category
            if created:
                categories_created += 1
                self.stdout.write(f'✅ Created category: {category.name}')
            else:
                self.stdout.write(f'   Category exists: {category.name}')
        
        self.stdout.write('')
        
        # Define all agents
        agents_data = [
            # Webhook Agents
            {
                'slug': 'five-whys-analysis',
                'name': '5 Whys Analysis',
                'short_description': 'Interactive problem-solving using the proven 5 Whys methodology',
                'description': 'Systematically find root causes through guided 5 Whys methodology. Perfect for troubleshooting operational problems, understanding failures, and identifying systemic issues.',
                'category': 'analysis',
                'price': 15.0,
                'agent_type': 'chat',
                'form_schema': None,
                'webhook_url': 'http://localhost:5678/webhook/5-whys-web',
                'access_url_name': '',
                'display_url_name': ''
            },
            {
                'slug': 'social-ads-generator',
                'name': 'Social Ads Generator',
                'short_description': 'Create compelling social media advertisements optimized for different platforms',
                'description': 'Generate engaging social media advertisements with AI-powered content generation. Optimized for Facebook, Instagram, LinkedIn, Twitter, TikTok, and YouTube.',
                'category': 'marketing',
                'price': 6.0,
                'agent_type': 'form',
                'form_schema': {
                    'fields': [
                        {
                            'name': 'description',
                            'type': 'textarea',
                            'label': 'Describe what you\'d like to generate',
                            'placeholder': 'Describe the product, service, or campaign',
                            'required': True,
                            'rows': 4
                        },
                        {
                            'name': 'social_platform',
                            'type': 'select',
                            'label': 'For Social Media Platform',
                            'required': True,
                            'options': [
                                {'value': '', 'label': 'Select a platform...'},
                                {'value': 'facebook', 'label': 'Facebook'},
                                {'value': 'instagram', 'label': 'Instagram'},
                                {'value': 'linkedin', 'label': 'LinkedIn'},
                                {'value': 'twitter', 'label': 'X (Twitter)'}
                            ]
                        },
                        {
                            'name': 'include_emoji',
                            'type': 'select',
                            'label': 'Include Emoji',
                            'required': True,
                            'options': [
                                {'value': '', 'label': 'Select an option...'},
                                {'value': 'yes', 'label': 'Yes'},
                                {'value': 'no', 'label': 'No'}
                            ]
                        }
                    ]
                },
                'webhook_url': 'http://localhost:5678/webhook/2dc234d8-7217-454a-83e9-81afe5b4fe2d',
                'access_url_name': '',
                'display_url_name': ''
            },
            {
                'slug': 'job-posting-generator',
                'name': 'Job Posting Generator',
                'short_description': 'Create professional job postings that attract top talent',
                'description': 'Generate comprehensive and attractive job postings with AI-powered content creation. Perfect for HR teams and recruiters.',
                'category': 'human-resources',
                'price': 10.0,
                'agent_type': 'form',
                'form_schema': {
                    'fields': [
                        {'name': 'job_title', 'type': 'text', 'label': 'Job Title', 'required': True},
                        {'name': 'company_name', 'type': 'text', 'label': 'Company Name', 'required': True},
                        {'name': 'job_description', 'type': 'textarea', 'label': 'Job Description', 'required': True, 'rows': 5},
                        {
                            'name': 'seniority_level',
                            'type': 'select',
                            'label': 'Seniority Level',
                            'required': True,
                            'options': [
                                {'value': '', 'label': 'Select level...'},
                                {'value': 'entry', 'label': 'Entry Level'},
                                {'value': 'junior', 'label': 'Junior'},
                                {'value': 'mid', 'label': 'Mid Level'},
                                {'value': 'senior', 'label': 'Senior'}
                            ]
                        },
                        {'name': 'location', 'type': 'text', 'label': 'Location', 'required': True}
                    ]
                },
                'webhook_url': 'http://localhost:5678/webhook/43f84411-eaaa-488c-9b1f-856e90d0aaf6',
                'access_url_name': '',
                'display_url_name': ''
            },
            {
                'slug': 'pdf-summarizer',
                'name': 'PDF Summarizer',
                'short_description': 'Extract and summarize content from PDF documents with AI analysis',
                'description': 'Upload PDF documents and get comprehensive AI-powered summaries, key insights, and analysis. Perfect for processing reports and research papers.',
                'category': 'document-processing',
                'price': 8.0,
                'agent_type': 'form',
                'form_schema': {
                    'fields': [
                        {
                            'name': 'pdf_file',
                            'type': 'file',
                            'label': 'Upload PDF Document',
                            'required': True,
                            'accept': '.pdf',
                            'max_size': '10MB'
                        },
                        {
                            'name': 'analysis_type',
                            'type': 'select',
                            'label': 'Analysis Type',
                            'required': True,
                            'default': 'summary',
                            'options': [
                                {'value': '', 'label': 'Select analysis type...'},
                                {'value': 'summary', 'label': 'Document Summary'},
                                {'value': 'key_points', 'label': 'Key Points Extraction'},
                                {'value': 'detailed_analysis', 'label': 'Detailed Analysis'}
                            ]
                        }
                    ]
                },
                'webhook_url': 'http://localhost:5678/webhook/simple-pdf-processor',
                'access_url_name': '',
                'display_url_name': ''
            },
            
            # Direct Access Agents
            {
                'slug': 'cybersec-career-navigator',
                'name': 'CyberSec Career Navigator',
                'short_description': 'Get personalized cybersecurity career guidance from AI expert Jessica',
                'description': 'Navigate your cybersecurity career path with expert AI guidance. Get personalized advice on certifications, job roles, skills development, and career progression.',
                'category': 'career-education',
                'price': 0.0,
                'agent_type': 'form',
                'form_schema': {'fields': []},
                'webhook_url': 'https://agent.jotform.com/019865a942ab7fa5b5b743a5fd2abe09e345',
                'access_url_name': 'agents:direct_access_handler',
                'display_url_name': 'agents:direct_access_display'
            },
            {
                'slug': 'ai-brand-strategist',
                'name': 'AI Brand Strategist',
                'short_description': 'Get AI-powered brand strategy insights and recommendations for your business',
                'description': 'Transform your brand with AI-driven strategic insights. Get expert guidance on brand positioning, messaging, visual identity, and competitive differentiation.',
                'category': 'marketing',
                'price': 0.0,
                'agent_type': 'form',
                'form_schema': {'fields': []},
                'webhook_url': 'https://agent.jotform.com/01986502acd276b48e3d5f39337046c8d9b6',
                'access_url_name': 'agents:direct_access_handler',
                'display_url_name': 'agents:direct_access_display'
            }
        ]
        
        # Create agents
        for agent_data in agents_data:
            category = categories[agent_data['category']]
            
            agent, created = Agent.objects.get_or_create(
                slug=agent_data['slug'],
                defaults={
                    'name': agent_data['name'],
                    'short_description': agent_data['short_description'],
                    'description': agent_data['description'],
                    'category': category,
                    'price': agent_data['price'],
                    'agent_type': agent_data['agent_type'],
                    'form_schema': agent_data['form_schema'],
                    'webhook_url': agent_data['webhook_url'],
                    'access_url_name': agent_data['access_url_name'],
                    'display_url_name': agent_data['display_url_name']
                }
            )
            
            if created:
                agents_created += 1
                system_type = 'Direct Access' if agent.access_url_name else 'Webhook'
                self.stdout.write(f'✅ Created agent: {agent.name} ({system_type})')
                self.stdout.write(f'   💰 Price: {agent.price} AED')
            else:
                self.stdout.write(f'   Agent exists: {agent.name}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Population completed successfully!'))
        self.stdout.write('')
        self.stdout.write(f'📊 Summary:')
        self.stdout.write(f'   Categories created: {categories_created}')
        self.stdout.write(f'   Agents created: {agents_created}')
        self.stdout.write('')
        
        # Final verification
        total_categories = AgentCategory.objects.filter(is_active=True).count()
        total_agents = Agent.objects.filter(is_active=True).count()
        webhook_agents = Agent.objects.filter(is_active=True, access_url_name='').count()
        direct_agents = Agent.objects.filter(is_active=True).exclude(access_url_name='').count()
        
        self.stdout.write(f'🔍 Final verification:')
        self.stdout.write(f'   Total categories: {total_categories}')
        self.stdout.write(f'   Total agents: {total_agents}')
        self.stdout.write(f'   Webhook agents: {webhook_agents}')
        self.stdout.write(f'   Direct access agents: {direct_agents}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Database is now consistent and ready!'))