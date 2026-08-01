from urllib.parse import urlparse

from rest_framework import serializers

from homeContent.utils import get_facebook_embed_url, get_youtube_embed_url
from .models import (
    Category,
    SubCategory,
    GalleryImage,
    Video,
)

# ==============================
# Read serializers
# ==============================


class SubCategoryReadSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    class Meta:
        model = SubCategory
        fields =[
            "id",
            "name",
            "description",
            "image",
            "category",
            "category_name",
        ]

class CategoryReadSerializer(serializers.ModelSerializer):
    subcategories = SubCategoryReadSerializer(
        many=True,
        read_only=True,
        source="sub_categories",
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "image",
            "subcategories",
        ]

class GalleryImageReadSerializer(serializers.ModelSerializer):

    sub_category_name = serializers.CharField(
        source="sub_category.name",
        read_only=True,
    )

    class Meta:
        model = GalleryImage
        fields = [
            "id",
            "sub_category",
            "sub_category_name",
            "image",
            "title",
            "order",
            "is_active",
            "created_at",
        ]


class VideoReadSerializer(serializers.ModelSerializer):

    sub_category_name = serializers.CharField(
        source="sub_category.name",
        read_only=True,
    )

    category_name = serializers.CharField(
        source="sub_category.category.name",
        read_only=True,
    )

    class Meta:
        model = Video
        fields = [
            "id",
            "sub_category",
            "sub_category_name",
            "category_name",
            "content_type",
            "platform",
            'title',
            'description',
            'embed_url',
            'thumbnail',
            'order',
            'is_active',
            "created_at",
        ]









# ==============================
# Write serializers
# ==============================


class CategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class SubCategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = "__all__"

class GalleryImageWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = "__all__"

class GalleryBulkCreateSerializer(serializers.Serializer):
    sub_category = serializers.PrimaryKeyRelatedField(
        queryset=SubCategory.objects.all()
    )

    images = serializers.ListField(
        child=serializers.ImageField(),
        allow_empty=False
    )

    title = serializers.CharField(
        required=False,
        allow_blank=True
    )

    is_active = serializers.BooleanField(
        default=True
    )


    def create(self, validated_data):

        images = validated_data.pop("images")

        gallery_images = []

        for image in images:
            gallery_images.append(
                GalleryImage(
                    image=image,
                    **validated_data
                )
            )

        return GalleryImage.objects.bulk_create(gallery_images)

class VideoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = "__all__"
        
    def validate_embed_url(self, value):
        return value.strip()

    def validate(self, attrs):
        platform = attrs.get(
            "platform",
            getattr(self.instance, "platform", None),
        )

        url = attrs.get(
            "embed_url",
            getattr(self.instance, "embed_url", None),
        )

        if not platform or not url:
            return attrs

        domain = urlparse(url).netloc.lower()

        platform_domains = {
            "youtube": (
                "youtube.com",
                "www.youtube.com",
                "youtu.be",
            ),
            "facebook": (
                "facebook.com",
                "www.facebook.com",
                "fb.watch",
            ),
        }

        allowed_domains = platform_domains.get(platform)

        if not allowed_domains:
            raise serializers.ValidationError(
                {
                    "platform": "Unsupported platform."
                }
            )

        if not any(
            domain == item or domain.endswith(f".{item}")
            for item in allowed_domains
        ):
            raise serializers.ValidationError(
                {
                    "embed_url": f"This URL does not belong to {platform.title()}."
                }
            )

        converters = {
            "youtube": get_youtube_embed_url,
            "facebook": get_facebook_embed_url,
        }

        attrs["embed_url"] = converters[platform](url)

        return attrs


# ==============================
# For Frontend serializers
# ==============================

class SubCategoryNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubCategory
        fields = (
            "id",
            "name",
            "image",
        )

class CategoryWithSubCategoriesSerializer(serializers.ModelSerializer):

    subcategories = SubCategoryNestedSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "image",
            "description",
            "subcategories",
        )

class FrontGalleryImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = GalleryImage
        fields = (
            "id",
            "image",
            "title",
        )

class FrontVideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Video
        fields = (
            "id",
            "title",
            "description",
            "content_type",
            "platform",
            "embed_url",
            "thumbnail",
        )