from typing import Sequence

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction

from shopapp.models import Order, Product


class Command(BaseCommand):
    """
    Create orders
    """

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Create order with products')
        user = User.objects.get(username='leodjango')

        # products: Sequence[Product] = Product.objects.defer('quantity', 'date_received').all()
        products: Sequence[Product] = Product.objects.only('id').all()

        order, created = Order.objects.get_or_create(
            delivery_address='Sidorov street, house 777',
            promocode='promo1000',
            user=user,
        )

        for product in products:
            order.products.add(product)

        order.save()

        self.stdout.write(self.style.SUCCESS(f'Created orders {order}'))
