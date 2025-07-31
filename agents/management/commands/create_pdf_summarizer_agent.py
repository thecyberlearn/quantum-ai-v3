from django.core.management.base import BaseCommand
from agents.models import AgentCategory, Agent

class Command(BaseCommand):
    help = 'Create PDF summarizer agent'

    def handle(self, *args, **options):
        # Get or create Document Processing category
        doc_category, created = AgentCategory.objects.get_or_create(
            slug='document-processing',
            defaults={
                'name': 'Document Processing',
                'description': 'AI-powered document analysis and processing tools',
                'icon': '📄'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created category: {doc_category.name}'))
        else:
            self.stdout.write(f'Category already exists: {doc_category.name}')
        
        # Create PDF Summarizer agent
        pdf_summarizer_agent, created = Agent.objects.get_or_create(
            slug='pdf-summarizer',
            defaults={
                'name': 'PDF Summarizer',
                'short_description': 'Extract and summarize content from PDF documents with AI analysis',
                'description': 'Upload PDF documents and get comprehensive AI-powered summaries, key insights, and analysis. Perfect for processing reports, research papers, contracts, and other documents. Supports multiple analysis types including summary, key points extraction, and sentiment analysis.',
                'category': doc_category,
                'price': 8.0,
                'form_schema': {
                    'fields': [
                        {
                            'name': 'pdf_file',
                            'type': 'file',
                            'label': 'Upload PDF Document',
                            'required': True,
                            'accept': '.pdf',
                            'max_size': '10MB',
                            'help_text': 'Select a PDF file to analyze (max 10MB)'
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
                                {'value': 'detailed_analysis', 'label': 'Detailed Analysis'},
                                {'value': 'sentiment', 'label': 'Sentiment Analysis'},
                                {'value': 'questions', 'label': 'Generate Questions'},
                                {'value': 'action_items', 'label': 'Extract Action Items'}
                            ],
                            'help_text': 'Choose the type of analysis to perform on the document'
                        },
                        {
                            'name': 'language',
                            'type': 'select',
                            'label': 'Document Language',
                            'required': False,
                            'default': 'auto',
                            'options': [
                                {'value': 'auto', 'label': 'Auto-detect'},
                                {'value': 'English', 'label': 'English'},
                                {'value': 'Arabic', 'label': 'Arabic (العربية)'},
                                {'value': 'Spanish', 'label': 'Spanish (Español)'},
                                {'value': 'French', 'label': 'French (Français)'},
                                {'value': 'German', 'label': 'German (Deutsch)'},
                                {'value': 'Chinese', 'label': 'Chinese (中文)'}
                            ],
                            'help_text': 'Specify document language for better analysis accuracy'
                        },
                        {
                            'name': 'output_length',
                            'type': 'select',
                            'label': 'Summary Length',
                            'required': False,
                            'default': 'medium',
                            'options': [
                                {'value': 'short', 'label': 'Short (1-2 paragraphs)'},
                                {'value': 'medium', 'label': 'Medium (3-5 paragraphs)'},
                                {'value': 'long', 'label': 'Long (detailed summary)'}
                            ],
                            'help_text': 'Choose the desired length of the analysis output'
                        }
                    ]
                },
                'webhook_url': 'http://localhost:5678/webhook/simple-pdf-processor'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created agent: {pdf_summarizer_agent.name}'))
        else:
            self.stdout.write(f'Agent already exists: {pdf_summarizer_agent.name}')
        
        self.stdout.write(self.style.SUCCESS('PDF Summarizer setup completed successfully'))
        self.stdout.write(f'Agent ID: {pdf_summarizer_agent.id}')
        self.stdout.write(f'Agent Slug: {pdf_summarizer_agent.slug}')
        self.stdout.write(f'Price: {pdf_summarizer_agent.price} AED')