from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .common import save_csv_products, save_csv_orders
from .models import Product, Order, ProductImage
from .admin_mixins import ExportAsMixins
from .forms import CSVImportForm


class OrderInline(admin.TabularInline):
    model = Product.orders.through


# class OrderInline(admin.StackedInline):
#     model = Product


class ProductInline(admin.StackedInline):
    model = ProductImage


@admin.action(description='Archive products')
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description='Unarchive products')
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsMixins):
    change_list_template = 'shopapp/products_change_list.html'
    actions = [
        mark_archived,
        mark_unarchived,
        'export_csv',
    ]
    inlines = [
        OrderInline,
        ProductInline,
    ]
    list_display = 'pk', 'name', 'price', 'quantity', 'date_received', 'description_short', 'archived',
    list_display_links = 'pk', 'name',
    ordering = '-name', '-pk',
    search_fields = 'name', 'description',
    fieldsets = [
        (None, {
            'fields': ('name', 'description'),
        }),
        ('Price-count options', {
            'fields': ('price', 'quantity'),
            'classes': ('wide', 'collapse',),
        }),
        ('Images', {
            'fields': ('preview',),
        }),
        ('Choose additional guarantee options', {
            'fields': ('has_additional_guarantee',),
            'classes': ('collapse',),
            'description': ("Choose this option for adding additional guarantee.",),
        }),
        ('Extra options', {
            'fields': ('archived',),
            'classes': ('collapse',),
            'description': ("Extra option. Field 'archived' for sort delete.",),
        }),
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 50:
            return obj.description
        return obj.description[:50] + '...'

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == 'GET':
            form = CSVImportForm()
            context = {
                'form': form,
            }
            return render(request, 'admin/csv_form.html', context)

        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                'form': form,
            }
            return render(request, 'admin/csv_form.html', context, status=400)

        save_csv_products(
            form.files['csv_file'].file,
            encoding=request.encoding,
        )

        # reader = DictReader(csv_file)

        # products = [
        #     Product(**row)
        #     for row in reader
        # ]
        # Product.objects.bulk_create(products)
        self.message_user(request, 'Data from csv was imported.')
        return redirect('..')

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                'import-products-csv/',
                self.import_csv,
                name='import_products_csv',
            )
        ]
        return new_urls + urls


# class ProductInline(admin.TabularInline):
# class ProductInline(admin.StackedInline):
#     model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin, ExportAsMixins):
    change_list_template = 'shopapp/orders_change_list.html'
    inlines = [
        ProductInline,
    ]
    list_display = 'delivery_address', 'promocode', 'created_at', 'user_verbose',

    def get_queryset(self, request):
        return Order.objects.select_related('user').prefetch_related('products')

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == 'GET':
            form = CSVImportForm()
            context = {
                'form': form,
            }
            return render(request, 'admin/csv_form.html', context)

        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                'form': form,
            }
            return render(request, 'admin/csv_form.html', context, status=400)

        save_csv_orders(
            form.files['csv_file'].file,
            encoding=request.encoding,
        )

        self.message_user(request, 'Data from csv was imported.')
        return redirect('..')

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                'import-orders-csv/',
                self.import_csv,
                name='import_orders_csv',
            )
        ]
        return new_urls + urls
