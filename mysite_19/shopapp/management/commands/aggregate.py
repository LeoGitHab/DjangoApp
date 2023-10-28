from django.contrib.auth.models import User

from django.core.management import BaseCommand
from django.db.models import Avg, Max, Min, Count, Sum

from shopapp.models import Product, Order


class Command(BaseCommand):
    """
    Create orders
    """

    def handle(self, *args, **options):
        self.stdout.write('Start deme aggregate')

        orders = Order.objects.annotate(
            total=Sum('products__price', default=0),  # Обращаемся к продуктам, и внутри каждого продукта - к цене
            products_count=Count('products')
        )
        for order in orders:
            print(
                f'Order #{order.id} with {order.products_count} products worth {order.total}.'
            )

        # result = Product.objects.filter(
        #     name__contains='Smartphone'
        # ).aggregate(
        #     average_price=Avg('price'),
        #     max_price=Max('price'),
        #     min_price=Min('price'),
        #     count=Count('id'),
        # )

        # result = Product.objects.aggregate(
        #     Avg('price'),
        #     Max('price'),
        #     Min('price'),
        #     Count('id'),
        # )

        # print(result)

        self.stdout.write('Done !')
