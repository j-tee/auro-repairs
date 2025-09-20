#!/usr/bin/env python3
"""
Fix Customer-User Database Links
Links existing Customer records to User records by email matching
"""

import os
import sys
import django
from django.conf import settings

sys.path.append('/home/teejay/Documents/Projects/auro-repairs')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from shop.models import Customer
from django.db import transaction

def fix_customer_user_links():
    print("🔧 FIXING CUSTOMER-USER DATABASE LINKS")
    print("=" * 80)
    User = get_user_model()
    customers = Customer.objects.filter(user__isnull=True)
    matches_found = []
    for customer in customers:
        try:
            user = User.objects.get(email=customer.email)
            matches_found.append((customer, user))
            print(f"   ✅ Match found: Customer '{customer.name}' ({customer.email}) -> User ID {user.id}")
        except User.DoesNotExist:
            print(f"   ⚠️  No user found for Customer '{customer.name}' ({customer.email})")
        except User.MultipleObjectsReturned:
            print(f"   ❌ Multiple users found for email {customer.email}")
    if not matches_found:
        print("\n❌ No matching email addresses found!")
        return False
    print(f"\n🔗 LINKING {len(matches_found)} CUSTOMER-USER PAIRS:")
    with transaction.atomic():
        for customer, user in matches_found:
            customer.user = user
            customer.save()
            print(f"   ✅ Linked: Customer {customer.id} ({customer.name}) -> User {user.id} ({user.email})")
    print(f"\n✅ Successfully linked {len(matches_found)} customers to users!")
    # Verify the fix
    print(f"\n🧪 VERIFICATION:")
    try:
        alice_user = User.objects.get(email='alice.cooper@customer.com')
        alice_customer = Customer.objects.get(user=alice_user)
        print(f"   ✅ alice.cooper@customer.com verification:")
        print(f"      User ID: {alice_user.id}")
        print(f"      Customer ID: {alice_customer.id}")
        print(f"      Customer Name: {alice_customer.name}")
    except (User.DoesNotExist, Customer.DoesNotExist) as e:
        print(f"   ⚠️  alice.cooper@customer.com verification failed: {e}")
    linked_customers_after = Customer.objects.filter(user__isnull=False).count()
    unlinked_customers_after = Customer.objects.filter(user__isnull=True).count()
    print(f"\n📈 FINAL STATISTICS:")
    print(f"   ✅ Linked Customers: {linked_customers_after}")
    print(f"   ❌ Unlinked Customers: {unlinked_customers_after}")
    return True

if __name__ == "__main__":
    success = fix_customer_user_links()
    if success:
        print(f"\n🎉 CUSTOMER-USER LINKING COMPLETED SUCCESSFULLY!")
        print("   Frontend can now map authenticated users to customer records")
    else:
        print(f"\n❌ CUSTOMER-USER LINKING FAILED")
        print("   Manual intervention may be required")
    sys.exit(0 if success else 1)
