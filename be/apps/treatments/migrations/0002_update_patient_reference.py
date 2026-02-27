"""
Migration to update Treatment model to reference new Patient model.
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('treatments', '0001_initial'),
        ('patients', '0004_patient'),  # Must come after Patient model is created
    ]

    operations = [
        # Update the patient ForeignKey to reference Patient model instead of CustomUser
        migrations.AlterField(
            model_name='treatment',
            name='patient',
            field=models.ForeignKey(
                help_text='Patient receiving the treatment',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='treatments',
                to='patients.patient'
            ),
        ),
    ]
