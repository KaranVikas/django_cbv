from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import (
  extend_schema, extend_schema_view , OpenApiParameter, OpenApiResponse
)
from .permissions import isOwnerOrReadOnly
from articles.models import Article
from .serializers import ArticleCreateSerializer, ArticleSerializer, ArticleUpdateSerializer


Q_PARAM = OpenApiParameter(
  name="q", location=OpenApiParameter.QUERY, required=False, type=str,
  description='Case-insensitive title search.'
)

REQUEST_ID_HDR = OpenApiParameter(
  name="X-Request-ID", location=OpenApiParameter.HEADER, required=False, type=str,
  description="Optional correlation id for tracing."
)

@extend_schema_view(
  list=extend_schema(
    operation_id="ArticleList",
    tags=["articles"],
    description="List articles, optionally filtered by title string",
    parameters=[Q_PARAM,REQUEST_ID_HDR],
    responses={200: ArticleSerializer(many=True)},
  ),
  retrieve=extend_schema(
    operation_id="ArticleRetrieve",
    tags=["articles"],
    description="Retrieve a single article by slug",
    parameters=[
      OpenApiParameter("slug", OpenApiParameter.PATH, str, description="Article slug"),
      REQUEST_ID_HDR
    ],
    responses={200: ArticleSerializer, 404: OpenApiResponse(description='Not found')},
  ),
  create=extend_schema(
    operation_id='ArticleCreate',
    tags=["articles"],
    description="Create a new article. Authentication required. ",
    parameters=[REQUEST_ID_HDR],
    request=ArticleCreateSerializer,
    responses={201: ArticleCreateSerializer, 400: OpenApiResponse(description='Bad request')},
  ),
  partial_update=extend_schema(
    operation_id='ArticlePartialUpdate',
    tags=["articles"],
    description="Partially update an article you own.",
    parameters=[
      OpenApiParameter("slug", OpenApiParameter.PATH, str, description='Article slug'),
      REQUEST_ID_HDR,
    ],
    request=ArticleUpdateSerializer,
    responses={200: ArticleSerializer, 400: OpenApiResponse(description="Bad request"), 
               403: OpenApiResponse(description="Forbidden")},
  ),
  destroy=extend_schema(
    operation_id="ArticleDelete",
    tags=["articles"],
    description="Delete an article you own",
    parameters=[
      OpenApiParameter("slug",OpenApiParameter.PATH, str, description="Article slug"),
      REQUEST_ID_HDR,
    ],
    responses={204: OpenApiResponse(description='Deleted'), 403: OpenApiResponse(description='Forbidden')},
  ),
)
class ArticleViewSet(
  mixins.ListModelMixin,
  mixins.CreateModelMixin,
  mixins.RetrieveModelMixin,
  mixins.DestroyModelMixin,
  mixins.UpdateModelMixin,
  viewsets.GenericViewSet
):
  """Why a ViewSet?
    - One class encapsulates all CRUD operations.
    - Router auto-generates clean URLs.
    - drf-spectacular can document each action with @extend_schema
  """

  permission_classes = [IsAuthenticatedOrReadOnly, isOwnerOrReadOnly]
  serializer_class = ArticleSerializer
  lookup_field = "slug"
  lookup_url_kwarg = "slug"

  def get_queryset(self):
    qs = Article.objects.select_related("owner").order_by("-created")
    q = self.request.query_params.get("q")
    return qs.filter(title__icontains=q) if q else qs

  def get_serializer_class(self):
    if self.action == 'create':
      return ArticleCreateSerializer
    if self.action in {'partial_update', 'update'}:
      return ArticleUpdateSerializer
    return ArticleSerializer
  
  def perform_create(self, serializer):
    #owner = current user
    serializer.save(owner=self.request.user)

  #PATCH /api/articles/{slug}

  def partial_update(self, request, *args , **kwargs):
    kwargs['partial'] = True
    return super().update(request, *args , **kwargs)