from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryView,
    FrontGalleryViewSet,
    FrontVideoViewSet,
    SubCategoryView,
    GalleryImageView,
    VideoView,
    FrontCategoryViewSet
)

router = DefaultRouter()

router.register(
    r"categories",
    CategoryView,
    basename="media-category",
)

router.register(
    r"sub-categories",
    SubCategoryView,
    basename="media-sub-category",
)

router.register(
    r"gallery",
    GalleryImageView,
    basename="gallery-image",
)

router.register(
    r"videos",
    VideoView,
    basename="video",
)
router.register(
    r"frontend/categories",
    FrontCategoryViewSet,
    basename="frontend-category",
)
router.register(
    r"frontend/gallery",
    FrontGalleryViewSet,
    basename="frontend-gallery",
)

router.register(
    r"frontend/videos",
    FrontVideoViewSet,
    basename="frontend-video",
)
urlpatterns = [
    path("", include(router.urls)),
]