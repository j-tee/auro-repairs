from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from shop.models import (
    Shop,
    Employee,
    Customer,
    Vehicle,
    VehicleProblem,
    Service,
    Part,
    Appointment,
    RepairOrder,
    RepairOrderPart,
    RepairOrderService,
)
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Generate seed data for the shop app"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            self.clear_data()

        self.stdout.write("Creating seed data...")

        # Create shops
        shops = self.create_shops()

        # Create services for each shop
        services = self.create_services(shops)

        # Create parts for each shop
        parts = self.create_parts(shops)

        # Create users for employees and customers
        employee_users = self.create_employee_users()
        customer_users = self.create_customer_users()

        # Create employees
        employees = self.create_employees(shops, employee_users)

        # Create customers
        customers = self.create_customers(customer_users)

        # Create vehicles
        vehicles = self.create_vehicles(customers)

        # Create vehicle problems
        problems = self.create_vehicle_problems(vehicles)

        # Create appointments
        appointments = self.create_appointments(vehicles, problems)

        # Create repair orders
        repair_orders = self.create_repair_orders(vehicles, services, parts)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created seed data:\n"
                f"- {len(shops)} shops\n"
                f"- {len(services)} services\n"
                f"- {len(parts)} parts\n"
                f"- {len(employees)} employees\n"
                f"- {len(customers)} customers\n"
                f"- {len(vehicles)} vehicles\n"
                f"- {len(problems)} vehicle problems\n"
                f"- {len(appointments)} appointments\n"
                f"- {len(repair_orders)} repair orders"
            )
        )

    def clear_data(self):
        """Clear existing data"""
        RepairOrderService.objects.all().delete()
        RepairOrderPart.objects.all().delete()
        RepairOrder.objects.all().delete()
        Appointment.objects.all().delete()
        VehicleProblem.objects.all().delete()
        Vehicle.objects.all().delete()
        Customer.objects.all().delete()
        Employee.objects.all().delete()
        Part.objects.all().delete()
        Service.objects.all().delete()
        Shop.objects.all().delete()

        # Clear users that were created for employees/customers
        User.objects.filter(email__contains="@autorepair").delete()
        User.objects.filter(email__contains="@customer").delete()

    def create_shops(self):
        """Create sample shops"""
        shops_data = [
            {
                "name": "Downtown Auto Repair",
                "address": "123 Main St, Downtown, NY 10001",
                "phone": "(555) 123-4567",
                "email": "info@downtownauto.com",
            },
            {
                "name": "Speedy Fix Garage",
                "address": "456 Oak Ave, Midtown, NY 10002",
                "phone": "(555) 234-5678",
                "email": "contact@speedyfix.com",
            },
            {
                "name": "Premium Auto Service",
                "address": "789 Pine Rd, Uptown, NY 10003",
                "phone": "(555) 345-6789",
                "email": "service@premiumauto.com",
            },
        ]

        shops = []
        for shop_data in shops_data:
            shop, created = Shop.objects.get_or_create(
                name=shop_data["name"], defaults=shop_data
            )
            shops.append(shop)
            if created:
                self.stdout.write(f"Created shop: {shop.name}")

        return shops

    def create_services(self, shops):
        """Create sample services"""
        services_data = [
            {
                "name": "Oil Change",
                "description": "Full synthetic oil change with filter",
                "labor_cost": Decimal("45.00"),
                "warranty_months": 3,
            },
            {
                "name": "Brake Inspection",
                "description": "Complete brake system inspection",
                "labor_cost": Decimal("75.00"),
                "warranty_months": 6,
            },
            {
                "name": "Brake Pad Replacement",
                "description": "Replace front or rear brake pads",
                "labor_cost": Decimal("150.00"),
                "warranty_months": 12,
            },
            {
                "name": "Transmission Service",
                "description": "Transmission fluid change and inspection",
                "labor_cost": Decimal("200.00"),
                "warranty_months": 12,
            },
            {
                "name": "Engine Diagnostic",
                "description": "Computer diagnostic scan",
                "labor_cost": Decimal("100.00"),
                "warranty_months": 1,
            },
            {
                "name": "Tire Rotation",
                "description": "Rotate and balance tires",
                "labor_cost": Decimal("50.00"),
                "warranty_months": 6,
            },
            {
                "name": "Battery Test",
                "description": "Battery and charging system test",
                "labor_cost": Decimal("25.00"),
                "warranty_months": 3,
            },
            {
                "name": "Air Filter Replacement",
                "description": "Replace engine air filter",
                "labor_cost": Decimal("30.00"),
                "warranty_months": 12,
            },
        ]

        services = []
        for shop in shops:
            for service_data in services_data:
                service, created = Service.objects.get_or_create(
                    shop=shop, name=service_data["name"], defaults=service_data
                )
                services.append(service)

        return services

    def create_parts(self, shops):
        """Create sample parts"""
        parts_data = [
            {
                "name": "Motor Oil 5W-30",
                "category": "new",
                "part_number": "OIL-5W30-001",
                "manufacturer": "Mobil1",
                "unit_price": Decimal("25.99"),
                "stock_quantity": 50,
            },
            {
                "name": "Oil Filter",
                "category": "new",
                "part_number": "FILTER-001",
                "manufacturer": "Fram",
                "unit_price": Decimal("8.99"),
                "stock_quantity": 30,
            },
            {
                "name": "Brake Pads Front",
                "category": "new",
                "part_number": "BRAKE-F-001",
                "manufacturer": "Wagner",
                "unit_price": Decimal("89.99"),
                "stock_quantity": 20,
            },
            {
                "name": "Brake Pads Rear",
                "category": "new",
                "part_number": "BRAKE-R-001",
                "manufacturer": "Wagner",
                "unit_price": Decimal("79.99"),
                "stock_quantity": 15,
            },
            {
                "name": "Air Filter",
                "category": "new",
                "part_number": "AIR-FILTER-001",
                "manufacturer": "K&N",
                "unit_price": Decimal("24.99"),
                "stock_quantity": 25,
            },
            {
                "name": "Spark Plugs Set",
                "category": "new",
                "part_number": "SPARK-001",
                "manufacturer": "NGK",
                "unit_price": Decimal("45.99"),
                "stock_quantity": 40,
            },
            {
                "name": "Car Battery",
                "category": "new",
                "part_number": "BATTERY-001",
                "manufacturer": "Interstate",
                "unit_price": Decimal("129.99"),
                "stock_quantity": 10,
            },
            {
                "name": "Transmission Fluid",
                "category": "new",
                "part_number": "TRANS-FLUID-001",
                "manufacturer": "Valvoline",
                "unit_price": Decimal("18.99"),
                "stock_quantity": 35,
            },
        ]

        parts = []
        for shop in shops:
            for i, part_data in enumerate(parts_data):
                # Make part numbers unique per shop
                part_data_copy = part_data.copy()
                part_data_copy["part_number"] = f"{part_data['part_number']}-{shop.id}"

                part, created = Part.objects.get_or_create(
                    shop=shop,
                    part_number=part_data_copy["part_number"],
                    defaults=part_data_copy,
                )
                parts.append(part)

        return parts

    def create_employee_users(self):
        """Create user accounts for employees"""
        employees_data = [
            {
                "email": "john.mechanic@autorepair.com",
                "first_name": "John",
                "last_name": "Smith",
                "role": "mechanic",
                "user_role": "employee",
            },
            {
                "email": "sarah.mechanic@autorepair.com",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "role": "mechanic",
                "user_role": "employee",
            },
            {
                "email": "mike.manager@autorepair.com",
                "first_name": "Mike",
                "last_name": "Brown",
                "role": "manager",
                "user_role": "owner",
            },
            {
                "email": "lisa.receptionist@autorepair.com",
                "first_name": "Lisa",
                "last_name": "Davis",
                "role": "receptionist",
                "user_role": "employee",
            },
            {
                "email": "tom.mechanic@autorepair.com",
                "first_name": "Tom",
                "last_name": "Wilson",
                "role": "mechanic",
                "user_role": "employee",
            },
            {
                "email": "anna.receptionist@autorepair.com",
                "first_name": "Anna",
                "last_name": "Taylor",
                "role": "receptionist",
                "user_role": "employee",
            },
        ]

        users = []
        for emp_data in employees_data:
            try:
                user = User.objects.get(email=emp_data["email"])
                # Update role if user exists
                user.role = emp_data["user_role"]
                user.save()
                created = False
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=emp_data["email"],  # Use email as username
                    email=emp_data["email"],
                    password="password123",
                    first_name=emp_data["first_name"],
                    last_name=emp_data["last_name"],
                    role=emp_data["user_role"],
                    is_email_verified=True,
                    is_active=True,
                )
                created = True

            if created:
                self.stdout.write(
                    f'Created employee user: {user.email} ({emp_data["user_role"]})'
                )
            users.append((user, emp_data["role"]))

        return users

    def create_customer_users(self):
        """Create user accounts for customers"""
        customers_data = [
            {
                "email": "alice.cooper@customer.com",
                "first_name": "Alice",
                "last_name": "Cooper",
            },
            {
                "email": "bob.martinez@customer.com",
                "first_name": "Bob",
                "last_name": "Martinez",
            },
            {
                "email": "carol.white@customer.com",
                "first_name": "Carol",
                "last_name": "White",
            },
            {
                "email": "david.lee@customer.com",
                "first_name": "David",
                "last_name": "Lee",
            },
            {
                "email": "emma.garcia@customer.com",
                "first_name": "Emma",
                "last_name": "Garcia",
            },
            {
                "email": "frank.rodriguez@customer.com",
                "first_name": "Frank",
                "last_name": "Rodriguez",
            },
        ]

        users = []
        for cust_data in customers_data:
            try:
                user = User.objects.get(email=cust_data["email"])
                # Update role if user exists
                user.role = "customer"
                user.save()
                created = False
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=cust_data["email"],  # Use email as username
                    email=cust_data["email"],
                    password="password123",
                    first_name=cust_data["first_name"],
                    last_name=cust_data["last_name"],
                    role="customer",
                    is_email_verified=True,
                    is_active=True,
                )
                created = True

            if created:
                self.stdout.write(f"Created customer user: {user.email} (customer)")
            users.append(user)

        return users

    def create_employees(self, shops, employee_users):
        """Create employees"""
        employees = []

        for i, (user, role) in enumerate(employee_users):
            shop = shops[i % len(shops)]  # Distribute employees across shops

            employee, created = Employee.objects.get_or_create(
                name=f"{user.first_name} {user.last_name}",
                shop=shop,
                defaults={
                    "role": role,
                    "phone_number": f"(555) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
                    "email": user.email,
                    # Don't link to user for now due to foreign key constraint issues
                    "user": None,
                },
            )
            employees.append(employee)

        return employees

    def create_customers(self, customer_users):
        """Create customers"""
        addresses = [
            "123 Elm St, Springfield, NY 10001",
            "456 Maple Ave, Springfield, NY 10002",
            "789 Oak Rd, Springfield, NY 10003",
            "321 Pine St, Springfield, NY 10004",
            "654 Cedar Ave, Springfield, NY 10005",
            "987 Birch Rd, Springfield, NY 10006",
        ]

        customers = []
        for i, user in enumerate(customer_users):
            customer, created = Customer.objects.get_or_create(
                name=f"{user.first_name} {user.last_name}",
                defaults={
                    "phone_number": f"(555) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
                    "email": user.email,
                    "address": addresses[i % len(addresses)],
                    # Don't link to user for now due to foreign key constraint issues
                    "user": None,
                },
            )
            customers.append(customer)

        return customers

    def create_vehicles(self, customers):
        """Create vehicles"""
        vehicles_data = [
            {"make": "Toyota", "model": "Camry", "year": 2020, "color": "Silver"},
            {"make": "Honda", "model": "Civic", "year": 2019, "color": "Blue"},
            {"make": "Ford", "model": "F-150", "year": 2021, "color": "Red"},
            {"make": "Chevrolet", "model": "Malibu", "year": 2018, "color": "White"},
            {"make": "Nissan", "model": "Altima", "year": 2020, "color": "Black"},
            {"make": "BMW", "model": "3 Series", "year": 2019, "color": "Gray"},
            {"make": "Audi", "model": "A4", "year": 2021, "color": "Blue"},
            {"make": "Mercedes", "model": "C-Class", "year": 2020, "color": "White"},
        ]

        vehicles = []
        for i, customer in enumerate(customers):
            # Create 1-2 vehicles per customer
            num_vehicles = random.randint(1, 2)
            for j in range(num_vehicles):
                vehicle_data = vehicles_data[(i + j) % len(vehicles_data)]
                vin = f"1HGBH41JXMN{random.randint(100000, 999999)}"
                license_plate = f"{random.choice(['ABC', 'DEF', 'GHI'])}-{random.randint(1000, 9999)}"

                vehicle, created = Vehicle.objects.get_or_create(
                    vin=vin,
                    defaults={
                        "customer": customer,
                        "make": vehicle_data["make"],
                        "model": vehicle_data["model"],
                        "year": vehicle_data["year"],
                        "license_plate": license_plate,
                        "color": vehicle_data["color"],
                    },
                )
                vehicles.append(vehicle)

        return vehicles

    def create_vehicle_problems(self, vehicles):
        """Create vehicle problems"""
        problems_data = [
            "Engine makes strange noise when starting",
            "Brakes feel spongy and require more pressure",
            "Check engine light is on",
            "Air conditioning not cooling properly",
            "Transmission slips when shifting",
            "Battery seems to be dying quickly",
            "Steering wheel vibrates at high speeds",
            "Oil leak under the vehicle",
            "Unusual smell from exhaust",
            "Radio and electrical issues",
        ]

        problems = []
        for vehicle in vehicles:
            # Create 0-2 problems per vehicle
            num_problems = random.randint(0, 2)
            for _ in range(num_problems):
                description = random.choice(problems_data)

                problem = VehicleProblem.objects.create(
                    vehicle=vehicle,
                    description=description,
                    resolved=random.choice([True, False]),
                )
                problems.append(problem)

        return problems

    def create_appointments(self, vehicles, problems):
        """Create appointments"""
        appointments = []

        for i, vehicle in enumerate(
            vehicles[:10]
        ):  # Create appointments for first 10 vehicles
            # Create appointment date within next 30 days
            days_ahead = random.randint(1, 30)
            appointment_date = timezone.now() + timedelta(days=days_ahead)

            # Randomly assign a problem or leave None
            problem = random.choice(problems + [None, None])  # Higher chance of None

            appointment = Appointment.objects.create(
                vehicle=vehicle,
                reported_problem=problem,
                description=f"Scheduled maintenance and inspection for {vehicle.make} {vehicle.model}",
                date=appointment_date,
                status=random.choice(["pending", "in_progress", "completed"]),
            )
            appointments.append(appointment)

        return appointments

    def create_repair_orders(self, vehicles, services, parts):
        """Create repair orders"""
        repair_orders = []

        for i, vehicle in enumerate(
            vehicles[:8]
        ):  # Create repair orders for first 8 vehicles
            repair_order = RepairOrder(
                vehicle=vehicle,
                discount_percent=Decimal(str(random.choice([0, 5, 10]))),
                tax_percent=Decimal("8.25"),  # NY tax rate
                notes=f"Repair work for {vehicle.make} {vehicle.model}",
                total_cost=Decimal("0.00"),  # Set initial total cost
            )
            repair_order.save(
                skip_calculation=True
            )  # Skip calculation during initial creation

            # Add 1-3 services
            vehicle_services = random.sample(services, random.randint(1, 3))
            for service in vehicle_services:
                RepairOrderService.objects.create(
                    repair_order=repair_order, service=service
                )

            # Add 1-4 parts
            vehicle_parts = random.sample(parts, random.randint(1, 4))
            for part in vehicle_parts:
                RepairOrderPart.objects.create(
                    repair_order=repair_order, part=part, quantity=random.randint(1, 3)
                )

            # Now recalculate total cost after adding services and parts
            repair_order.total_cost = repair_order.calculate_total_cost()
            repair_order.save()
            repair_orders.append(repair_order)

        return repair_orders
