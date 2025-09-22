from django.contrib import messages 
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import ArticleForm
from .models import Article
# Create your views here.

class ArticleListView(ListView):
  model = Article
  paginate_by = 10
  ordering = "-created"
  template_name = "articles/articles_list.html" # optional

  def get_queryset(self):
    qs = super().get_queryset().select_related("owner")
    q = self.request.GET.get("q")
    return qs.filter(title__icontains=q) if q else qs

class ArticleDetailView(DetailView):
  model = Article
  slug_field = "slug"
  slug_url_kwarg = "slug"

class OwnerRequiredMixin(UserPassesTestMixin):
  """ Allow only the owner to update/delete """

  def test_func(self):
    obj = self.get_object()
    return obj.owner == self.request.user
  
class ArticleCreateView(LoginRequiredMixin, CreateView):
  model = Article
  fields = ["title","body"]
  form_class = ArticleForm

  #success_url optional ; CBV will use get_absolute_url by default
  def form_valid(self, form):
    form.instance.owner = self.request.user
    messages.success(self.request, "Article created.")
    return super().form_valid(form)
  
class ArticleUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
  model = Article
  fields = ["title","body"]
  from_class = ArticleForm
  
  def form_valid(self, form):
    form.instance.owner = self.request.user
    messages.success(self.request, "Article updated.")
    return super().form_valid(form)
  
class ArticleDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
  model = Article
  success_url = reverse_lazy("article-list")

  def delete(self, request, *args, **kwargs):
    messages.success(self.request, "Article deleted.")
    return super().delete(request, *args, **kwargs)