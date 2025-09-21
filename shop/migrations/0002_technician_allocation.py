# Generated migration for technician allocation
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),  # Adjust based on your latest migration
    ]

    operations = [
        # Add technician allocation fields to Appointment model
        migrations.AddField(
            model_name='appointment',
            name='assigned_technician',
            field=models.ForeignKey(
                blank=True,
                help_text='Technician assigned to work on this appointment',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='assigned_appointments',
                to='shop.employee'
            ),
        ),
        migrations.AddField(
            model_name='appointment',
            name='assigned_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the technician was assigned',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='appointment',
            name='started_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When work actually began',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='appointment',
            name='completed_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When work was completed',
                null=True
            ),
        ),
        # Update status choices to include new workflow states
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(
                choices=[
                    ('scheduled', 'Scheduled'),
                    ('assigned', 'Assigned'),
                    ('in_progress', 'In Progress'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled')
                ],
                default='scheduled',
                max_length=20
            ),
        ),
        # Data migration to update existing appointments from 'pending' to 'scheduled'
        migrations.RunSQL(
            "UPDATE shop_appointment SET status = 'scheduled' WHERE status = 'pending';",
            reverse_sql="UPDATE shop_appointment SET status = 'pending' WHERE status = 'scheduled';"
        ),
    ]
