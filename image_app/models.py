import hashlib
import os.path

from django.db import models


def get_image_path(instance, filename):
    return "images/%s%s" % (
        hashlib.sha1((instance.name + filename).encode("utf-8")).hexdigest(),
        os.path.splitext(filename)[1],
    )


class UploadedImage(models.Model):
    name = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    edit_image = models.ImageField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
