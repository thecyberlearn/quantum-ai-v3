from django.core.management.base import BaseCommand
from agents.models import AgentCategory, Agent

class Command(BaseCommand):
    help = 'Create job posting generator agent'

    def handle(self, *args, **options):
        # Get or use existing HR category
        hr_category, created = AgentCategory.objects.get_or_create(
            slug='human-resources',
            defaults={
                'name': 'Human Resources',
                'description': 'AI-powered HR and recruitment tools',
                'icon': '💼'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created category: {hr_category.name}'))
        else:
            self.stdout.write(f'Category already exists: {hr_category.name}')
        
        # Create Job Posting Generator agent
        job_posting_agent, created = Agent.objects.get_or_create(
            slug='job-posting-generator',
            defaults={
                'name': 'Job Posting Generator',
                'short_description': 'Create professional job postings that attract top talent',
                'description': 'Generate comprehensive and attractive job postings with AI-powered content creation. Perfect for HR teams and recruiters looking to create compelling job descriptions that attract qualified candidates. Supports multiple languages, locations, and contract types.',
                'category': hr_category,
                'price': 10.0,
                'form_schema': {
                    'fields': [
                        {
                            'name': 'job_title',
                            'type': 'text',
                            'label': 'Job Title',
                            'placeholder': 'e.g., Senior Full Stack Developer',
                            'required': True,
                            'help_text': 'The position title for the job posting'
                        },
                        {
                            'name': 'company_name',
                            'type': 'text',
                            'label': 'Company Name',
                            'placeholder': 'e.g., Quantum Technologies Inc.',
                            'required': True,
                            'help_text': 'Name of the hiring company'
                        },
                        {
                            'name': 'job_description',
                            'type': 'textarea',
                            'label': 'Job Description',
                            'placeholder': 'Describe the role, responsibilities, and what makes this opportunity exciting...',
                            'required': True,
                            'rows': 5,
                            'help_text': 'Detailed description of the role, responsibilities, and company culture'
                        },
                        {
                            'name': 'seniority_level',
                            'type': 'select',
                            'label': 'Seniority Level',
                            'required': True,
                            'options': [
                                {'value': '', 'label': 'Select seniority level...'},
                                {'value': 'entry', 'label': 'Entry Level'},
                                {'value': 'junior', 'label': 'Junior'},
                                {'value': 'mid', 'label': 'Mid Level'},
                                {'value': 'senior', 'label': 'Senior'},
                                {'value': 'lead', 'label': 'Lead'},
                                {'value': 'principal', 'label': 'Principal'},
                                {'value': 'executive', 'label': 'Executive'}
                            ],
                            'help_text': 'Experience level required for this position'
                        },
                        {
                            'name': 'contract_type',
                            'type': 'select',
                            'label': 'Contract Type',
                            'required': True,
                            'options': [
                                {'value': '', 'label': 'Select contract type...'},
                                {'value': 'full-time', 'label': 'Full-time'},
                                {'value': 'part-time', 'label': 'Part-time'},
                                {'value': 'contract', 'label': 'Contract'},
                                {'value': 'freelance', 'label': 'Freelance'},
                                {'value': 'internship', 'label': 'Internship'},
                                {'value': 'temporary', 'label': 'Temporary'}
                            ],
                            'help_text': 'Type of employment contract'
                        },
                        {
                            'name': 'location',
                            'type': 'text',
                            'label': 'Location',
                            'placeholder': 'e.g., Dubai, UAE (Remote)',
                            'required': True,
                            'help_text': 'Job location, include if remote work is available'
                        },
                        {
                            'name': 'language',
                            'type': 'select',
                            'label': 'Language',
                            'required': False,
                            'default': 'English',
                            'options': [
                                {'value': 'English', 'label': 'English'},
                                {'value': 'Arabic', 'label': 'Arabic (العربية)'},
                                {'value': 'Spanish', 'label': 'Spanish (Español)'},
                                {'value': 'French', 'label': 'French (Français)'},
                                {'value': 'German', 'label': 'German (Deutsch)'},
                                {'value': 'Chinese', 'label': 'Chinese (中文)'}
                            ],
                            'help_text': 'Primary language for the job posting'
                        }
                    ]
                },
                'webhook_url': 'http://localhost:5678/webhook/43f84411-eaaa-488c-9b1f-856e90d0aaf6',
                'access_url_name': '',
                'display_url_name': ''
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created agent: {job_posting_agent.name}'))
        else:
            self.stdout.write(f'Agent already exists: {job_posting_agent.name}')
        
        self.stdout.write(self.style.SUCCESS('Job Posting Generator setup completed successfully'))
        self.stdout.write(f'Agent ID: {job_posting_agent.id}')
        self.stdout.write(f'Agent Slug: {job_posting_agent.slug}')
        self.stdout.write(f'Price: {job_posting_agent.price} AED')