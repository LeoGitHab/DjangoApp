from django.urls import path, include

from rest_framework.routers import DefaultRouter


from .views import (
    ArticlesListView,
    ArticlesDetailView,
    LatestArticlesFeed,
)

app_name = "blogapp"

urlpatterns = [
    path('articles/', ArticlesListView.as_view(), name='articles_list'),
    path('article/<int:pk>/', ArticlesDetailView.as_view(), name='article_detail'),
    path('articles/latest/feed/', LatestArticlesFeed(), name='articles_feed'),
]
