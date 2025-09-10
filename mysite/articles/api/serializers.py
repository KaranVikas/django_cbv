from rest_framework import serializers
from articles.models import Article

class ArticleSerializer(serializers.ModelSerializer):
  owner = serializers.StringRelatedField(read_only=True)

  class Meta:
    model = Article
    fields = ["title","slug","body","owner","created", "updated"]
    read_only_fields = ["slug","owner", "created", "updated"]
  
class ArticleCreateSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Article
    fields = ["title","body"]

class ArticleUpdateSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Article
    fields = ["title","body"]
