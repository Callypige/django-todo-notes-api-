# Generated migration to add status field to Note model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='status',
            field=models.CharField(
                choices=[
                    ('active', 'Active'),
                    ('in_progress', 'In Progress'),
                    ('completed', 'Completed'),
                    ('archived', 'Archived')
                ],
                default='active',
                help_text='Status automatically updated based on associated todos',
                max_length=20
            ),
        ),
    ]
