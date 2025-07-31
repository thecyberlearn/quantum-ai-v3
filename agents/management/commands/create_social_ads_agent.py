from django.core.management.base import BaseCommand
from agents.models import AgentCategory, Agent

class Command(BaseCommand):
    help = 'Create social ads agent for testing'

    def handle(self, *args, **options):
        # Create Marketing category
        marketing_category, created = AgentCategory.objects.get_or_create(
            slug='marketing',
            defaults={
                'name': 'Marketing & Advertising',
                'description': 'AI-powered marketing and advertising tools',
                'icon': '📢'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created category: {marketing_category.name}'))
        else:
            self.stdout.write(f'Category already exists: {marketing_category.name}')
        
        # Create Social Ads Generator agent
        social_ads_agent, created = Agent.objects.get_or_create(
            slug='social-ads-generator',
            defaults={
                'name': 'Social Ads Generator',
                'short_description': 'Create compelling social media advertisements optimized for different platforms',
                'description': 'Generate engaging social media advertisements with AI-powered content generation. Optimized for Facebook, Instagram, LinkedIn, Twitter, TikTok, and YouTube. Includes platform-specific formatting, emoji support, and multi-language capabilities.',
                'category': marketing_category,
                'price': 6.0,
                'form_schema': {
                    'fields': [
                        {
                            'name': 'description',
                            'type': 'textarea',
                            'label': 'Describe what you\'d like to generate',
                            'placeholder': 'Describe the product, service, or campaign you want to create an ad for. Include key features, target audience, and any specific messaging you want to emphasize.',
                            'required': True,
                            'rows': 4,
                            'help_text': 'Provide clear, specific information about your product or service for better ad copy'
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
                                {'value': 'twitter', 'label': 'X (Twitter)'},
                                {'value': 'tiktok', 'label': 'TikTok'},
                                {'value': 'youtube', 'label': 'YouTube'}
                            ],
                            'help_text': 'Choose the social media platform for optimization'
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
                            ],
                            'help_text': 'Whether to include emojis in the ad copy'
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
                            'help_text': 'Select the primary language for the ad copy'
                        }
                    ]
                },
                'webhook_url': 'http://localhost:5678/webhook/2dc234d8-7217-454a-83e9-81afe5b4fe2d'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created agent: {social_ads_agent.name}'))
        else:
            self.stdout.write(f'Agent already exists: {social_ads_agent.name}')
        
        self.stdout.write(self.style.SUCCESS('Social Ads Agent setup completed successfully'))
        self.stdout.write(f'Agent ID: {social_ads_agent.id}')
        self.stdout.write(f'Agent Slug: {social_ads_agent.slug}')
        self.stdout.write(f'Price: {social_ads_agent.price} AED')