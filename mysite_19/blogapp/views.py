from django.contrib.syndication.views import Feed
from django.views.generic import ListView, DetailView
from django.urls import reverse, reverse_lazy

from .models import Article


class ArticlesListView(ListView):
    """Получение списка статей."""

    template_name = 'blogapp/article-list.html'
    queryset = (
        Article.objects
        .filter(pub_date__isnull=False)
        .order_by('pk')
    )


class ArticlesDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = 'Blog Articles (latest)'
    description = 'Updates on changes and addition blog articles'
    link = reverse_lazy("blogapp:articles_list")

    def items(self):
        return (
            Article.objects
            .filter(pub_date__isnull=False)
            .order_by('-pub_data')[:5]
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:200]

    # def item_link(self, item: Article):
    #     return reverse('blogapp:article_detail', kwargs={'pk': item.pk})

# class ArticlesListView(ListView):
#     """Получение списка статей."""
#
#     template_name = 'blogapp/articles_list.html'
#     context_object_name = 'articles'
#     # queryset = Article.objects.all()
#
#     queryset = (
#         Article.objects
#         .select_related("author", "category")
#         .prefetch_related("tags")
#         .defer('content', 'author__bio')
#     )
