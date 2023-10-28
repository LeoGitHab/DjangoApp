from django.db import models
from django.urls import reverse


class Author(models.Model):
    """
    Модель Author предсьавляет автора,
    и краткую инфо по нему.
    """

    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=100, db_index=True)
    bio = models.TextField(null=False, blank=True, db_index=True)

    # def __repr__(self):
    #     return f'{type(self).__name__}({self.name!r}, {self.bio!r})'

    def __str__(self):
        return f'{self.name}'


class Category(models.Model):
    """
    Модель Category представляет категорию статьи автора.
    """

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=40, db_index=True)

    def __str__(self):
        return f'{self.name}'


class Tag(models.Model):
    """
    Модель Tag представляет собой тэг, который можно назначить статье.
    """

    name = models.CharField(max_length=20, db_index=True)

    def __str__(self):
        return f'{self.name}'


class Article(models.Model):
    """
    Модель Article представляет собой статью.
    """

    title = models.CharField(max_length=200, db_index=True)
    content = models.TextField(null=False, blank=True, db_index=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)

    def get_absolute_url(self):
        return reverse('blogapp:article_detail', kwargs={'pk': self.pk})

    def __repr__(self):
        return f'{self.title}'
