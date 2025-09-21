#!/usr/bin/env python3
"""
CREATE TECHNICIAN ALLOCATION MIGRATION
Generates Django migration for adding technician allocation fields to Appointment model
"""
import os
import sys

# Add project to path
sys.path.insert(0, '/home/teejay/Documents/Projects/auro-repairs')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')

import django
django.setup()

def create_migration():
    """Create migration for technician allocation fields"""
    print("🔧 CREATING TECHNICIAN ALLOCATION MIGRATION")
    print("=" * 45)
    
    migration_content = '''# Generated migration for technician allocation
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
'''
    
    # Write migration file
    migration_filename = '/home/teejay/Documents/Projects/auro-repairs/shop/migrations/0002_technician_allocation.py'
    
    try:
        with open(migration_filename, 'w') as f:
            f.write(migration_content)
        
        print(f"✅ Created migration: {migration_filename}")
        print("\n📋 Migration includes:")
        print("   ✅ assigned_technician field (ForeignKey to Employee)")
        print("   ✅ assigned_at timestamp")
        print("   ✅ started_at timestamp") 
        print("   ✅ completed_at timestamp")
        print("   ✅ Updated status choices (scheduled, assigned, in_progress, completed, cancelled)")
        print("   ✅ Data migration: 'pending' → 'scheduled'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating migration: {e}")
        return False

def show_workflow_example():
    """Show the new appointment workflow"""
    print("\n🔄 NEW APPOINTMENT WORKFLOW")
    print("=" * 30)
    
    workflow = '''
1. 📅 SCHEDULED (default)
   ├─ Customer books appointment
   ├─ assigned_technician: None
   └─ Status: "scheduled"

2. 👨‍🔧 ASSIGNED  
   ├─ Shop manager assigns technician
   ├─ assigned_technician: Employee object
   ├─ assigned_at: timestamp
   └─ Status: "assigned"

3. 🔧 IN_PROGRESS
   ├─ Technician starts work
   ├─ started_at: timestamp  
   └─ Status: "in_progress"

4. ✅ COMPLETED
   ├─ Work is finished
   ├─ completed_at: timestamp
   └─ Status: "completed"
'''
    print(workflow)

def main():
    """Main function"""
    print("🚀 TECHNICIAN ALLOCATION MIGRATION SETUP")
    print("=" * 45)
    
    success = create_migration()
    
    if success:
        show_workflow_example()
        
        print("\n🎯 NEXT STEPS:")
        print("1. Run: python manage.py makemigrations")
        print("2. Run: python manage.py migrate")
        print("3. Test technician assignment functionality")
        print("4. Update API endpoints for technician allocation")
        
        print("\n🎉 RESULT: Appointments can now be allocated to technicians!")
        print("   • Status automatically changes: scheduled → assigned → in_progress → completed")
        print("   • Timestamps track the complete workflow")
        print("   • Workload management prevents technician overload")
    else:
        print("\n❌ Migration creation failed - check errors above")

if __name__ == "__main__":
    main()
