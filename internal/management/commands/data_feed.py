from internal.models import *
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
import random
from django.utils import timezone
from faker import Faker


fake = Faker()


class Command(BaseCommand):
    help = "Creates dummy data for orders"

    def handle(self, *args, **options):
        try:
            # Create some dummy users if they don't exist
            user, created = User.objects.get_or_create(username="Rahul")

            # Create some dummy orders
            for i in range(1, 11):  # Create 10 dummy orders
                order = Order.objects.create(
                    customer=user,
                    total_price=i * 100.00,
                    order_status="pending",
                    payment_status="paid",
                    pickup_approx_time=timezone.now() + timezone.timedelta(minutes=20),
                    location=fake.address(),
                    created_by=user,
                    modified_by=user,
                )
                # Create some order items for each order
                for recp in Recipe.objects.all():
                    OrderItem.objects.create(
                        order=order,
                        recipe=recp,
                        quantity=random.randint(1, 5),
                        price=recp.price,
                    )

            self.stdout.write(
                self.style.SUCCESS("Successfully created dummy order data")
            )

        except Exception as e:
            raise CommandError(f"Error creating dummy data: {str(e)}")
