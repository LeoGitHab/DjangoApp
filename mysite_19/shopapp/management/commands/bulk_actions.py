from django.contrib.auth.models import User

from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    """
    Create orders
    """

    def handle(self, *args, **options):
        self.stdout.write('Start deme bulk actions')

        result = Product.objects.filter(
            name__contains='Smartphone',
        ).update(has_additional_guarantee=True)

        print(result)

        # info = [
        #     ('Smartphone 1', 799),
        #     ('Smartphone 2', 899),
        #     ('Smartphone 3', 999),
        # ]
        #
        # products = [
        #     Product(name=name, price=price)
        #     for name, price in info
        # ]
        #
        # result = Product.objects.bulk_create(products)
        # for obj in result:
        #     print(obj)

        self.stdout.write('Done !')
