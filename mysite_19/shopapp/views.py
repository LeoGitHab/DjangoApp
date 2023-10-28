"""
В этом модуле лежат набор представлений.

Разные view интернет-магазина по товарам, заказам и т.д.
"""

import logging
from timeit import default_timer
from csv import DictWriter

from django.core import serializers
from django.core.cache import cache

from django.contrib.auth.models import Group, User
from django.http import (HttpResponse,
                         HttpRequest,
                         HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView)
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.views import View

from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action

from django_filters.rest_framework import DjangoFilterBackend

from .serializers import ProductSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Product, Order, ProductImage
from .forms import GroupForm, ProductForm
from .common import save_csv_products

log = logging.getLogger(__name__)


@extend_schema(description='Product views CRUD')
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product.

    Полный CRUD для сущностей товара.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ['name', 'description', ]

    filterset_fields = [
        'name',
        'price',
        'quantity',
        'has_additional_guarantee',
        'archived',
    ]

    ordering_fields = [
        'name',
        'price',
        'quantity',
    ]

    @method_decorator(cache_page(60 * 1))
    def list(self, *args, **kwargs):
        print('Hello products list from cache...')
        return super().list(*args, **kwargs)

    @action(methods=['get', ], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type='text/csv')
        filename = 'products-export.csv'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            'name',
            'price',
            'quantity',
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @action(
        detail=False,
        methods=['post', ],
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES['file'].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary='Get one product by id',
        description='Retrieves **product**, returns 404 if not found.',
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description='Empty response, product by id not found.'),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


class ShopIndexView(View):
    """Представление для тестовой страницы продуктов."""

    # @method_decorator(cache_page(60 * 1))
    def get(self, request: HttpRequest) -> HttpResponse:
        """Получение продуктов."""
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
            "items": 1,
        }

        print('"shop index context" - this label for visualizing affect of cache ...', context)
        log.debug('Products for shop index: %s', products)
        log.info('Rendering shop index...')
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    """Отображение групп пользователей с разрешениями возможных действий."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Получение групп пользователей с разрншениями."""
        context = {
            'form': GroupForm(),
            'groups': Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        """Отправка данных группы в форму."""
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductsListView(ListView):
    """Получение списка продуктов."""

    template_name = 'shopapp/products-list.html'
    context_object_name = 'products'
    queryset = Product.objects.filter(archived=False)


class ProductDetailsView(DetailView):
    """Детальное отображение продукта."""

    template_name = 'shopapp/product_detail.html'
    # model = Product
    queryset = Product.objects.prefetch_related('images')
    context_object_name = 'product'


class ProductCreateView(CreateView):
    """Создание нового продукта."""

    permission_required = 'shop.add_product'
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        """Проверка валидности формы с данными нового продукта."""
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(UpdateView):
    """Обновление продукта."""

    model = Product
    form_class = ProductForm
    template_name_suffix = '_update_form'

    def get_success_url(self):
        """Переход по данному url в случае успешного обновления."""
        return reverse(
            'shopapp:product_detail',
            kwargs={'pk': self.object.pk},
        )

    def form_valid(self, form):
        """В случае валидности формы с данными, продукт обновляется."""
        response = super().form_valid(form)
        for image in form.files.getlist('images'):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )

        return response


class ProductDeleteView(DeleteView):
    """Удаление продукта."""

    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        """В случае валидности формы с данными, продукт удаляется."""
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save(update_fields=['archived'])
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    """Просмотр списка существующих заказов."""

    context_object_name = 'orders'
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
        .all()
    )


class OrdersDetailView(PermissionRequiredMixin, DetailView):
    """Детализация определённого заказа."""

    permission_required = 'shopapp.view_order'
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )


class OrderCreateView(CreateView):
    """Создание нового заказа."""

    model = Order
    fields = 'user', 'delivery_address', 'promocode', 'products'
    success_url = reverse_lazy('shopapp:order_list')


class OrderUpdateView(UpdateView):
    """Обновление существующего заказа."""

    model = Order
    fields = 'user', 'delivery_address', 'promocode', 'products'
    template_name_suffix = '_update_form'

    def get_success_url(self):
        """Переход по этому url в случае успешного обновления заказа."""
        return reverse(
            'shopapp:order_detail',
            kwargs={'pk': self.object.pk},
        )


class UserOrdersListView(ListView):
    model = Order
    template_name_suffix = "_user_list"
    context_object_name = 'orders'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.owner = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
        return context

    def get_queryset(self):
        self.owner = User.objects.filter(id=self.kwargs['pk']).first()
        queryset = Order.objects.filter(user_id=self.kwargs['pk']).all()
        return queryset


class UserOrdersJSONView(View):
    def get(self, request, *args, **kwargs):
        get_object_or_404(User, id=self.kwargs['pk'])

        cache_key = f"user_{self.kwargs['pk']}_orders_export_data"
        user_orders_as_json = cache.get(cache_key)

        if not user_orders_as_json:
            user_orders_as_json = serializers.serialize(
                'json', Order.objects.
                filter(user_id=self.kwargs['pk']).
                order_by('pk').all()
            )

            cache.set(cache_key, user_orders_as_json, 120)

        return HttpResponse(user_orders_as_json, content_type='application/json')


class OrderDeleteView(DeleteView):
    """Удаление заказа."""

    model = Order
    success_url = reverse_lazy('shopapp:order_list')


class ProductsExportDataView(View):
    """Просмотр данных по продуктам."""

    def get(self, request: HttpRequest) -> JsonResponse:
        """Отображение продуктов в формате JSON."""

        cache_key = 'products_export_data'
        products_data = cache.get(cache_key)
        if not products_data:
            products = Product.objects.order_by('pk').all()
            products_data = [
                {
                    'pk': product.pk,
                    'name': product.name,
                    'description': product.description,
                    'price': product.price,
                    'quantity': product.quantity,

                }
                for product in products
            ]
            elem = products_data[0]
            name = elem['name']
            print('name =', name)

            cache.set(cache_key, products_data, 60)

        return JsonResponse({'products': products_data})
