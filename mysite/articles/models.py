from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.shortcuts import reverse

# Create your models here.

class Article(models.Model):
  owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  title = models.CharField(max_length=200)
  slug = models.SlugField(unique=True, max_length=220)
  body = models.TextField()
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)

  def save(self, *args, **kwargs):
    if not self.slug:
      base = slugify(self.title)[:200]
      candidate = base
      n = 1 
      while Article.objects.filter(slug=candidate).exists():
        n += 1
        candidate = f"{base} - {n} "
      self.slug = candidate
    super().save(*args, **kwargs)

  def get_absolute_url(self):
    return reverse("web-article-detail", kwargs={"slug": self.slug} )
  
  def __str__(self):
    return self.title
                   