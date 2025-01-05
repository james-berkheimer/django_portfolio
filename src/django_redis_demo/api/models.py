import os

from django.db import models
from PIL import Image


class MediaThumbnail(models.Model):
    image = models.ImageField(upload_to="thumbnails/", blank=True)
    movie_thumb_url = models.URLField(blank=True, unique=True)  # Ensure movie_thumb_url is unique
    print(f"movie_thumb_url: {movie_thumb_url}")

    def save(self, *args, **kwargs):
        print(f"Saving image: {self.image} {self.pk}")

        # If the object already exists and the image is updated
        print(f"self.pk: {self.pk}")
        print(f"self.image: {self.image}")
        if self.pk and self.image:
            existing_image = MediaThumbnail.objects.get(pk=self.pk).image
            print(f"Existing image: {existing_image}")
            print(f"Existing image url: {existing_image.url}")
            print(f"Self image url: {self.image.url}")
            # If the image has changed
            if existing_image and existing_image.url != self.image.url:
                super().save(*args, **kwargs)
                self.resize_image()
        else:
            super().save(*args, **kwargs)
            self.resize_image()

    def resize_image(self):
        img = Image.open(self.image.path)

        width, height = img.size
        desired_ratio = 1.5
        max_width = 150
        new_height = round(max_width * desired_ratio)

        if width > max_width:
            img = img.resize((max_width, new_height))
            img.save(self.image.path)
