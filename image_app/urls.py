from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from . import views

urlpatterns = [
    path("upload", views.upload_image, name="upload"), path(
        "edit/<int:id>", views.edit_image, name="edit")
]
