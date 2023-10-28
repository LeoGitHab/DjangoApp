from string import ascii_letters
from random import choices

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from .models import Product, Order
from .utils import add_two_numbers


class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEquals(result, 5)


class ProductCreateViewTestCase(TestCase):
    def setUp(self) -> None:
        user = User.objects.create_superuser(username="admin", password="password")
        self.client.force_login(user)

        self.product_name = ''.join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(
            reverse('shopapp:product_create'),
            {
                'name': self.product_name,
                'description': 'Good car!',
                'price': 2000,
                'quantity': 15,
                'has_additional_guarantee': False,
                'archived': False,
                # 'created_by': 'User',
            }
        )

        self.assertRedirects(response, reverse('shopapp:products_list'))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )


class ProductDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        Product.objects.create(name='Best Product')
        cls.product = Product.objects.get(name='Best Product')
        cls.product_id = cls.product.id

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse('shopapp:product_detail', kwargs={'pk': self.product_id})
        )
        self.assertEquals(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse('shopapp:product_detail', kwargs={'pk': self.product_id})
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        'users-fixture.json',
        'products-fixture.json',
    ]

    def setUp(self):
        user = User.objects.create_superuser(username="admin", password="password")
        self.client.force_login(user)

    def test_products(self):
        response = self.client.get(reverse('shopapp:products_list'))
        # Проверка контекста т.к. в ProductsListView параметр context_object_name = 'products'
        self.assertQuerySetEqual(
            qs=Product.objects.filter(archived=False).all(),  # Данные, которые мы желаем получить
            values=[p.pk for p in response.context['products']],  # Данные, которые мы получили
            transform=lambda p: p.pk,  # Как нужно преобразовать данные из 'queryset' (qs), чтобы сравнить с 'values'
        )
        self.assertTemplateUsed(response, 'shopapp/articles_list.html')


class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_superuser(username="admin", password="password")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse('shopapp:order_list'))
        self.assertContains(response, 'Orders:')

    def test_orders_view_not_autentincated(self):
        self.client.logout()
        response = self.client.get(reverse('shopapp:order_list'))
        self.assertEquals(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create(username="admin", password="password")
        permission_order = Permission.objects.get(codename='view_order')
        cls.user.user_permissions.add(permission_order)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.order = Order.objects.create(
            delivery_address='Some street, some flat',
            promocode='ABC123!',
            user=self.user,
        )

    def tearDown(self) -> None:
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(reverse(
            'shopapp:order_detail',
            kwargs={'pk': self.order.pk})
        )

        received_data = response.context["orders"].pk
        expected_data = self.order.pk

        self.assertEqual(received_data, expected_data)
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        'users-fixture.json',
        'products-fixture.json',
    ]

    def test_get_products_view(self):
        response = self.client.get(
            reverse('shopapp:products-export'),
        )
        self.assertEquals(response.status_code, 200)
        products = Product.objects.order_by('pk').all()
        expected_data = [
            {
                'pk': product.pk,
                'name': product.name,
                'description': product.description,
                'price': str(product.price),
                'quantity': product.quantity,

            }
            for product in products
        ]
        products_data = response.json()
        self.assertEquals(
            products_data['products'],
            expected_data
        )
