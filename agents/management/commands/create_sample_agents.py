from django.core.management.base import BaseCommand
from agents.models import AgentCategory, Agent

class Command(BaseCommand):
    help = 'Create sample agents for testing'

    def handle(self, *args, **options):
        # Create categories
        ai_category, _ = AgentCategory.objects.get_or_create(
            slug='ai-tools',
            defaults={
                'name': 'AI Tools',
                'description': 'AI-powered automation tools',
                'icon': '🤖'
            }
        )
        
        data_category, _ = AgentCategory.objects.get_or_create(
            slug='data-analysis',
            defaults={
                'name': 'Data Analysis',
                'description': 'Data processing and analysis tools',
                'icon': '📊'
            }
        )
        
        web_category, _ = AgentCategory.objects.get_or_create(
            slug='web-scraping',
            defaults={
                'name': 'Web Scraping',
                'description': 'Web data extraction tools',
                'icon': '🕷️'
            }
        )
        
        # Create sample agents
        Agent.objects.get_or_create(
            slug='pdf-analyzer',
            defaults={
                'name': 'PDF Content Analyzer',
                'short_description': 'Extract and analyze content from PDF documents',
                'description': 'This agent processes PDF files and extracts meaningful insights including summaries, keywords, and sentiment analysis. Perfect for document processing workflows.',
                'category': ai_category,
                'price': 5.00,
                'form_schema': {
                    'fields': [
                        {
                            'name': 'pdf_url',
                            'type': 'url',
                            'label': 'PDF URL',
                            'placeholder': 'https://example.com/document.pdf',
                            'required': True
                        },
                        {
                            'name': 'analysis_type',
                            'type': 'select',
                            'label': 'Analysis Type',
                            'options': [
                                {'value': 'summary', 'label': 'Summary'},
                                {'value': 'keywords', 'label': 'Keywords'},
                                {'value': 'sentiment', 'label': 'Sentiment Analysis'}
                            ],
                            'required': True
                        }
                    ]
                },
                'webhook_url': 'https://your-n8n-instance.com/webhook/pdf-analyzer'
            }
        )
        
        Agent.objects.get_or_create(
            slug='website-scraper',
            defaults={
                'name': 'Website Data Scraper',
                'short_description': 'Extract structured data from any website',
                'description': 'Advanced web scraping agent that can extract specific data from websites using CSS selectors or XPath. Handles JavaScript-rendered content and returns clean, structured data.',
                'category': web_category,
                'price': 3.00,
                'form_schema': {
                    'fields': [
                        {
                            'name': 'website_url',
                            'type': 'url',
                            'label': 'Website URL',
                            'placeholder': 'https://example.com',
                            'required': True
                        },
                        {
                            'name': 'selectors',
                            'type': 'textarea',
                            'label': 'CSS Selectors (one per line)',
                            'placeholder': 'h1.title\n.price\n.description',
                            'required': True
                        },
                        {
                            'name': 'wait_for_js',
                            'type': 'checkbox',
                            'label': 'Wait for JavaScript to load',
                            'required': False
                        }
                    ]
                },
                'webhook_url': 'https://your-n8n-instance.com/webhook/website-scraper'
            }
        )
        
        Agent.objects.get_or_create(
            slug='data-analyzer',
            defaults={
                'name': 'CSV Data Analyzer',
                'short_description': 'Analyze and visualize CSV data with insights',
                'description': 'Upload CSV files and get comprehensive data analysis including statistics, trends, and visualizations. Perfect for business intelligence and data exploration.',
                'category': data_category,
                'price': 4.50,
                'form_schema': {
                    'fields': [
                        {
                            'name': 'csv_url',
                            'type': 'url',
                            'label': 'CSV File URL',
                            'placeholder': 'https://example.com/data.csv',
                            'required': True
                        },
                        {
                            'name': 'analysis_columns',
                            'type': 'text',
                            'label': 'Columns to Analyze (comma-separated)',
                            'placeholder': 'sales,revenue,date',
                            'required': False
                        },
                        {
                            'name': 'chart_type',
                            'type': 'select',
                            'label': 'Chart Type',
                            'options': [
                                {'value': 'line', 'label': 'Line Chart'},
                                {'value': 'bar', 'label': 'Bar Chart'},
                                {'value': 'pie', 'label': 'Pie Chart'},
                                {'value': 'scatter', 'label': 'Scatter Plot'}
                            ],
                            'required': False
                        }
                    ]
                },
                'webhook_url': 'https://your-n8n-instance.com/webhook/data-analyzer'
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Sample agents created successfully'))
        self.stdout.write(f'Created categories: {AgentCategory.objects.count()}')
        self.stdout.write(f'Created agents: {Agent.objects.count()}')