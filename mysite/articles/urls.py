from django.urls import path
from .views import (
  ArticleCreateView,
  ArticleDeleteView,
  ArticleDetailView,
  ArticleUpdateView,
  ArticleListView, 
)

urlpatterns =  [
  path("", ArticleListView.as_view(), name="web-article-list"),
  path("new/", ArticleCreateView.as_view(), name="web-article-create"),
  path("<slug:slug>", ArticleDetailView.as_view(), name="web-article-detail"),
  path("<slug:slug>/edit/", ArticleUpdateView.as_view(), name="web-article-update"),
  path("<slug:slug>/delete", ArticleDeleteView.as_view(), name="web-article-delete"),
]



