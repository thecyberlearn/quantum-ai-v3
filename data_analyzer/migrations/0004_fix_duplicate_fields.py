# Generated manually to fix duplicate field migration errors

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_analyzer', '0003_dataanalysisagentrequest_input_text_and_more'),
    ]

    operations = [
        # This migration exists to mark the problematic fields as "already applied"
        # It doesn't actually change anything, just syncs Django's migration state
        # with the actual database schema
        
        # The following fields already exist in the database but Django thinks they need to be added:
        # - data_file (from 0002_auto_20250710_0431)
        # - analysis_type (from 0002_auto_20250710_0431) 
        # - analysis_results (from 0002_auto_20250710_0431)
        # - insights_summary (from 0002_auto_20250710_0431)
        # - report_text (from 0002_auto_20250710_0431)
        
        # This empty migration helps sync the state without actually changing the database
    ]