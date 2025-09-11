# Crud + permissions + params + pagination

from django.urls import reverse
from django.contrib.auth import get_user_model
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

from articles.models import Article

User = get_user_model()

class BaseAPITestCase(APITestCase):
  """
  Common  setup: 
    - self.faker for generating fake data
    - self.user (author/owner)
    - self.other_user (not the owner)
    - convenience helpers
  """

  def setup(self):
    self.faker = Faker()
    self.user = User.objects.create_user(username="alice", password="test")
    self.other_user = User.objects.create_user(username="bob", password="test")

    #default headers (per your 'New Pattern')
    self.lang_hdr = {'HTTP_ACCEPT_LANGUAGE':"en-ca"}
    self.trace_hdr = {'HTTP_X_REQUEST_ID':"test-req-001"}

    def api_list_url(self):
      return reverse("article_list") # -> /api/articles
    
    def api_detail_url(self, slug:str):
      return reverse("article-detail", kwargs={"slug":slug}) # -> /api/articles/{slug}

    def make_article(self, owner=None, title=None, body=None):
      owner = owner or self.user
      title = title or self.faker.sentence(nb_words=4)
      body = body or self.faker.paragraph(nb_sentences=3)
      #slug  will be auto-generated in model.save()
      return Article.objects.create(owner=owner, title=title, slug="", body=body)
    
class TestArticleListCreate(BaseAPITestCase):
  """
  Group: /api/articles/ (GET list, POST create)
   Covers:
    - pagination envelope (count/next/previous/results)
    - query filtering via ?q=
    - create requires auth (401 when unauthenticated)
    - create returns 201 and includes slug + owner
  """

  def test_should_return_paginated_articles_and_allow_search(self):
    target = self.make_article(title="Django CBV Patterns")
    self.make_article(title="Something Else")

    #search fro "CBV"
    url = self.api_list_url()
    response = self.client.get(
      url, { "q":"CBV"}, **self.lang_hdr, **self.trace_hdr 
    )

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertIn("count", response.data)
    self.assertIn("results", response.data)
    titles = [a["title"] for a in response.data["results"]]
    self.assertIn(target.title, titles)
    self.assertTrue(all("CBV" in t or "Cbv" in t or "cbv" in t for t in titles))

  def test_should_not_create_article_when_unauthenticated(self):
    url = self.api_list_url()
    payload = {"title":"My Post", "body":"Hello"}
    resp = self.client.post(url, payload, format="json", **self.lang_hdr, **self.trace_hdr)
    self.assertEqual(resp.status_code,status.HTTP_401_UNAUTHORIZED)

  def test_should_create_article_when_authenticated(self):
    url = self.api_list_url()
    payload = {"title":"My First", "body":"Hello API"}

    self.client.force_authenticate(user=self.user)
    resp = self.client.post(url, payload, format="json", **self.lang_hdr, **self.trace_hdr)

    self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
    self.assertEqual(resp.data["title"], payload["title"])
    self.assertIn("slug", resp.data)
    self.assertEqual(resp.data["owner"], str(self.user))

    get_resp = self.client.get(self.api_detail_url(resp.data["slug"]), **self.lang_hdr)
    self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
    


