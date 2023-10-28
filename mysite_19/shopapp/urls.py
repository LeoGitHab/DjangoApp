from django.urls import path, include

from rest_framework.routers import DefaultRouter


from .views import (
    ShopIndexView,
    GroupsListView,
    ProductDetailsView,
    ProductsListView,
    OrdersListView,
    OrdersDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    OrderCreateView,
    OrderUpdateView,
    OrderDeleteView,
    ProductsExportDataView,
    ProductViewSet,
    UserOrdersListView,
    UserOrdersJSONView,
)

app_name = "shopapp"

routers = DefaultRouter()
routers.register('products', ProductViewSet)

urlpatterns = [
    # path('', cache_page(60 * 2)(ShopIndexView.as_view()), name='index'),
    path('', ShopIndexView.as_view(), name='index'),

    path('api/', include(routers.urls)),

    path('groups/', GroupsListView.as_view(), name='groups'),
    path('products/', ProductsListView.as_view(), name='products_list'),
    path('products/export/', ProductsExportDataView.as_view(), name='products-export'),
    path('products/<int:pk>/', ProductDetailsView.as_view(), name='product_detail'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/archive/', ProductDeleteView.as_view(), name='product_delete'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('orders/', OrdersListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrdersDetailView.as_view(), name='order_detail'),
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/update/', OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='order_delete'),
    path('users/<int:pk>/orders/', UserOrdersListView.as_view(), name='order_user_list'),
    path('users/<int:pk>/orders/export/', UserOrdersJSONView.as_view(), name='order_user_json')
]
