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

  def setUp(self):
    self.faker = Faker()
    self.user = User.objects.create_user(username="alice", password="test")
    self.other_user = User.objects.create_user(username="bob", password="test")

    #default headers (per your 'New Pattern')
    self.lang_hdr = {'HTTP_ACCEPT_LANGUAGE':"en-ca"}
    self.trace_hdr = {'HTTP_X_REQUEST_ID':"test-req-001"}

  def api_list_url(self):
    return reverse("article-list") # -> /api/articles
  
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

  # def test_should_return_paginated_articles_and_allow_search(self):
  #   target = self.make_article(title="Django CBV Patterns")
  #   self.make_article(title="Something Else")

  #   #search fro "CBV"
  #   url = self.api_list_url()
  #   response = self.client.get(
  #     url, { "q":"CBV"}, **self.lang_hdr, **self.trace_hdr 
  #   )
  #   print("------------------------------------------------")
  #   print("RESPONSE DATA", response.data)
  #   self.assertEqual(response.status_code, status.HTTP_200_OK)
  #   self.assertIn("count", response.data)
  #   self.assertIn("results", response.data)
  #   titles = [a["title"] for a in response.data["results"]]
  #   self.assertIn(target.title, titles)
  #   self.assertTrue(all("CBV" in t or "Cbv" in t or "cbv" in t for t in titles))

  # def test_should_not_create_article_when_unauthenticated(self):
  #   url = self.api_list_url()
  #   # print("(-------------------------------------------)")
  #   print('url', url, flush=True)
  #   payload = {"title":"My Post", "body":"Hello"}
  #   resp = self.client.post(url, payload, format="json", **self.lang_hdr, **self.trace_hdr)
  #   print("RESP", resp)
  #   self.assertEqual(resp.status_code,status.HTTP_401_UNAUTHORIZED)

  def test_should_create_article_when_authenticated(self):
    url = self.api_list_url()
    print('url', url, flush=True)
    payload = {"title":"My First", "body":"Hello API"}
    self.client.force_authenticate(user=self.user)
    
    resp = self.client.post(url, payload, format="json", **self.lang_hdr, **self.trace_hdr)
    print("Response--------------------------------------------", resp.data)
    self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
    self.assertEqual(resp.data["title"], payload["title"])
    self.assertIn("slug", resp.data)
    self.assertEqual(resp.data["owner"], str(self.user))

    get_resp = self.client.get(self.api_detail_url(resp.data["slug"]), **self.lang_hdr)
    self.assertEqual(get_resp.status_code, status.HTTP_200_OK)

# class TestArticleRetreiveUpdateDelete(BaseAPITestCase):
#   """
#   Group: /api/articles/{slug} {get retrieve , PATCH update, DELETE destroy}
#   Covers: 
#   - retrieve 200 and 404
#   - owner-only patch/delete (403 for non-owner)
#   - patch returns updated data; delete returns  204
#   """

#   def setUp(self):
#     super().setUp()
#     self.article = self.make_article(owner=self.user, title="Editable Title")

#   def test_should_retrieve_article_by_slug(self):
#     url = self.api_detail_url(self.article.slug)
#     resp = self.client.get(url, **self.land_hrd, **self.trace_hdr)
#     self.assertEqual(resp.status_code, status.HTTP_200_OK)
#     self.assertEqual(resp.data["title"],"Editable Title")

#   def test_should_return_404_when_slug_not_found(self):
#     url = self.api_detail_url("no-such-article")
#     resp = self.client.get(url, **self.lang_hdr)
#     self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

#   def test_should_patch_article_when_owner(self):
#     url = self.api_detail_url(self.article.slug)
#     self.client.force_authenticate(user=self.user)
#     resp = self.client.patch(url, {'title':'New Title'}, format="json",**self.lang_hdr)
#     self.assertEqual(resp.status_code, status.HTTP_200_OK)
#     self.assertEqual(resp.data['title'],"New Title")

#   def test_should_forbid_patch_when_not_owner(self):
#     url = self.api_detail_url(self.article.slug)
#     self.client.force_authenticate(user=self.other_user)
#     resp = self.client.patch(url, {'title':'Hack'}, format="json" , **self.lang_hdr)
#     self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

#   def test_should_delete_article_when_owner(self):
#     url = self.api_detail_url(self.article.slug)
#     self.client.force_authenticate(user=self.user)
#     resp = self.client.delete(url, **self.lang_hdr)
#     self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
#     # verify its gone
#     get_resp = self.client.get(url, **self.lang_hdr)
#     self.assertEqual(get_resp.status_code, status.HTTP_404_NOT_FOUND)

  
