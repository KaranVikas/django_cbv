from django.urls import path
from .views import (
  ArticleCreateView,
  ArticleDeleteView,
  ArticleDetailView,
  ArticleListView, 
)

urlpatterns =  [
  path("", ArticleListView.as_view, name="article-list"),
  path("articles/new/", ArticleCreateView.as_view, name="article-create"),
  path("articles/<slug:slug>", ArticleDetailView.as_view, name="article-detail"),
  path("articles/<slug:slug/edit>", ArticleCreateView.as_view, name="article-update"),
  path("articles/<slug:slug/delete>", ArticleDeleteView.as_view, name="article-delete"),

]