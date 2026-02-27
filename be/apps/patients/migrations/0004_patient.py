"""
Migration to create standalone Patient model and update Treatment references.
"""

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0003_patientprofile_is_deleted'),  # or the latest migration
        ('clinics', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        # Create new Patient model
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(db_index=True, help_text='Patient first name', max_length=100)),
                ('last_name', models.CharField(db_index=True, help_text='Patient last name', max_length=100)),
                ('email', models.EmailField(help_text='Patient email address', max_length=254, validators=[django.core.validators.EmailValidator()])),
                ('contact_number', models.CharField(blank=True, help_text='Patient phone number', max_length=20, null=True)),
                ('gender', models.CharField(blank=True, choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other'), ('NOT_SPECIFIED', 'Prefer not to specify')], help_text='Patient gender', max_length=20, null=True)),
                ('date_of_birth', models.DateField(blank=True, help_text='Patient date of birth', null=True)),
                ('address', models.TextField(blank=True, help_text='Patient address', null=True)),
                ('medical_history', models.TextField(blank=True, help_text='Detailed medical history and conditions', null=True)),
                ('allergies', models.TextField(blank=True, help_text='Known allergies and sensitivities', null=True)),
                ('is_active', models.BooleanField(db_index=True, default=True, help_text='Whether patient is active')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='Soft delete flag')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_doctor', models.ForeignKey(blank=True, help_text='Doctor assigned to this patient', limit_choices_to={'role': 'DOCTOR'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_patients', to='users.customuser')),
                ('clinic', models.ForeignKey(help_text='Clinic where patient is registered', on_delete=django.db.models.deletion.CASCADE, related_name='patients', to='clinics.clinic')),
                ('created_by', models.ForeignKey(blank=True, help_text='User who created this patient record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='patients_created', to='users.customuser')),
                ('updated_by', models.ForeignKey(blank=True, help_text='User who last updated this patient record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='patients_updated', to='users.customuser')),
            ],
            options={
                'verbose_name': 'Patient',
                'verbose_name_plural': 'Patients',
                'ordering': ['-created_at'],
            },
        ),
        
        # Add indexes to Patient model
        migrations.AddIndex(
            model_name='patient',
            index=models.Index(fields=['clinic', 'is_active'], name='patients_pa_clinic_a3b5e0_idx'),
        ),
        migrations.AddIndex(
            model_name='patient',
            index=models.Index(fields=['clinic', 'assigned_doctor'], name='patients_pa_clinic_d2f4c1_idx'),
        ),
        migrations.AddIndex(
            model_name='patient',
            index=models.Index(fields=['first_name', 'last_name'], name='patients_pa_first_n_e3c6d2_idx'),
        ),
        migrations.AddIndex(
            model_name='patient',
            index=models.Index(fields=['email'], name='patients_pa_email_f7a8e9_idx'),
        ),
    ]
