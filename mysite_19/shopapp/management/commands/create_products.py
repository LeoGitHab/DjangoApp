from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    """
    Create products
    """

    def handle(self, *args, **options):
        self.stdout.write('Create products:')
        product_items = [
            ('Laptop', 1999.12, 100),
            ('Smartphone', 2999.22, 1000),
            ('Desktop', 3999.32, 500),
        ]

        for products in product_items:
            product, created = Product.objects.get_or_create(name=products[0], price=products[1], quantity=products[2])
            self.stdout.write(f'Create product {str(product.name)} '
                              f'with price ${product.price} '
                              f'and quantity = {product.quantity}')

        self.stdout.write(self.style.SUCCESS('Products created'))
