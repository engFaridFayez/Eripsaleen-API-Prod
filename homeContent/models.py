from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="categories/",blank=True,null=True)
    description = models.TextField(null=True,blank=True)
    class Meta:
        ordering = ["id"]
    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True,blank=True)
    image = models.ImageField(upload_to="sub_categories/",null=True,blank=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name="sub_categories")
    def __str__(self):
        return self.name



class GalleryImage(models.Model):
    sub_category = models.ForeignKey(SubCategory,on_delete=models.CASCADE,related_name="gallery_images")
    image = models.ImageField(upload_to="gallery/",blank=True,null=True)
    title = models.CharField(max_length=255,blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order","-created_at"]
    def __str__(self):
        return self.title or f"Image #{self.pk}"

class Video(models.Model):

    CONTENT_TYPES = [
    ("video", "Video"),
    ("podcast", "Podcast"),
    ("reel", "Reel"),
]

    PLATFORM_CHOICES = [
        ("youtube", "YouTube"),
        ("facebook", "Facebook"),
    ]

    sub_category = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name="videos",
    )

    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPES,
    )
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
    )

    title = models.CharField(max_length=200,blank=True)
    description = models.TextField(blank=True,null=True)
    embed_url = models.URLField()

    thumbnail = models.ImageField(
        upload_to="videos/thumbnails/",
        blank=True,
        null=True,
    )

    order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title