from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db import models


def product_preview_directory_path(instance: 'Product', filename: str) -> str:
    return 'products/product_{pk}/preview/{filename}'.format(
        pk=instance.pk,
        filename=filename,
    )


class Product(models.Model):
    """
    Модель Product предсьавляет товар,
    который можно подавать в интернет-магазине.

    Заказы тут: :model:`shopapp.Order`
    """
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['name', 'price']

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0, db_index=True)
    quantity = models.PositiveSmallIntegerField(default=0, db_index=True)
    date_received = models.DateTimeField(auto_now_add=True)
    has_additional_guarantee = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)

    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f'Product {self.name} with id={self.id} for ${self.price} --> {self.quantity} items. {self.description}'


def product_images_directory_path(instance: 'ProductImage', filename: str) -> str:
    return 'products/product_{pk}/images/{filename}'.format(
        pk=instance.product.pk,
        filename=filename,
    )


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.CharField(max_length=200, null=False, blank=True)

    order = models.OneToOneField('Order', on_delete=models.CASCADE, null=True)


class Order(models.Model):
    delivery_address = models.TextField(null=False, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    receipt = models.FileField(null=True, upload_to='orders/receipts/')

    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    products = models.ManyToManyField(Product, related_name='orders')

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self):
        return f'{[self.delivery_address, self.promocode, self.user.pk]!r}'
