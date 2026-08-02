from rest_framework import viewsets , status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.permissions import ReadOnlyOrAdmin
from .models import (
    Category,
    SubCategory,
    GalleryImage,
    Video,
)

from .serializers import (
    CategoryReadSerializer,
    CategoryWriteSerializer,
    FrontGalleryImageSerializer,
    FrontVideoSerializer,
    SubCategoryReadSerializer,
    SubCategoryWriteSerializer,
    GalleryImageReadSerializer,
    GalleryImageWriteSerializer,
    VideoReadSerializer,
    VideoWriteSerializer,
    CategoryWithSubCategoriesSerializer,
    GalleryBulkCreateSerializer
)

class CategoryView(viewsets.ModelViewSet):
    permission_classes = [ReadOnlyOrAdmin]
    queryset = Category.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CategoryWriteSerializer
        return CategoryReadSerializer

class SubCategoryView(viewsets.ModelViewSet):
    permission_classes = [ReadOnlyOrAdmin]
    queryset = SubCategory.objects.select_related(
        "category",
    )

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return SubCategoryWriteSerializer
        return SubCategoryReadSerializer

class GalleryImageView(viewsets.ModelViewSet):
    permission_classes = [ReadOnlyOrAdmin]
    queryset = GalleryImage.objects.select_related(
        "sub_category",
    )

    def get_serializer_class(self):
        if self.action == "bulk_create":
            return GalleryBulkCreateSerializer

        if self.action in ["create", "update", "partial_update"]:
            return GalleryImageWriteSerializer

        return GalleryImageReadSerializer

    @action(
        detail=False,
        methods=["post"],
        url_path="bulk-create",
    )
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        gallery_images = serializer.save()

        return Response(
            GalleryImageReadSerializer(
                gallery_images,
                many=True,
                context=self.get_serializer_context(),
            ).data,
            status=status.HTTP_201_CREATED,
        )

class VideoView(viewsets.ModelViewSet):
    permission_classes = [ReadOnlyOrAdmin]
    queryset = Video.objects.select_related(
        "sub_category",
        "sub_category__category",
    )

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return VideoWriteSerializer
        return VideoReadSerializer


class FrontCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [ReadOnlyOrAdmin]
    queryset = Category.objects.prefetch_related(
        "subcategories",
    )

    serializer_class = CategoryWithSubCategoriesSerializer

class FrontGalleryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [ReadOnlyOrAdmin]
    serializer_class = FrontGalleryImageSerializer

    def get_queryset(self):
        queryset = (
            GalleryImage.objects.filter(is_active=True)
            .select_related(
                "sub_category",
                "sub_category__category",
            )
        )

        sub_category = self.request.query_params.get("sub_category")

        if sub_category:
            queryset = queryset.filter(
                sub_category=sub_category,
            )

        return queryset

class FrontVideoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [ReadOnlyOrAdmin]
    serializer_class = FrontVideoSerializer

    def get_queryset(self):
        queryset = (
            Video.objects.filter(is_active=True)
            .select_related(
                "sub_category",
                "sub_category__category",
            )
        )

        content_type = self.request.query_params.get(
            "content_type"
        )

        sub_category = self.request.query_params.get(
            "sub_category"
        )

        if content_type:
            queryset = queryset.filter(
                content_type=content_type,
            )

        if sub_category:
            queryset = queryset.filter(
                sub_category=sub_category,
            )

        return queryset