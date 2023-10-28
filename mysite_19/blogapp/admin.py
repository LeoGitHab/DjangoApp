from django.contrib import admin

from .models import Article, Tag, Category, Author


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = 'id', 'title', 'pub_date', 'author', 'category',


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = 'name',


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'name',



@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = 'name', 'bio',
