from django.contrib import admin
from .models import Article
# Register your models here.

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
  list_display = ("title", "owner", "created")
  search_fields = ("title", 'body')
  prepopulated_fields = {"slug": ("title",)}