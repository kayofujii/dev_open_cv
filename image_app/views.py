import hashlib
import os.path

import cv2
from django.conf import settings
from django.shortcuts import redirect, render

from .forms import ImageForm
from .models import UploadedImage


def upload_image(request):
    params = {}
    params["form"] = ImageForm()
    params["uploaded_images"] = UploadedImage.objects.all()
    if request.method == "POST":
        form = ImageForm(request.POST)
        if form.is_valid():
            uploaded_image = UploadedImage()
            uploaded_image.name = form.cleaned_data["name"]
            uploaded_image.image = request.FILES.get("image")
            uploaded_image.save()
            return redirect("upload")

    return render(request, "image_app/index.html", params)


def edit_image(request, id):
    params = {}
    uploaded_image = UploadedImage.objects.get(id=id)
    if "button_gray" in request.POST:
        change_gray(uploaded_image)
        uploaded_image.edit_image = get_image_path(uploaded_image)
        print(get_image_path(uploaded_image))
        uploaded_image.save()
        return redirect("upload")
    return render(request, "image_app/index.html", params)


def change_gray(uploaded_image):
    url = uploaded_image.image.url
    path = str(settings.BASE_DIR) + url

    img = cv2.imread(path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    output = str(settings.BASE_DIR) + '/media' + \
        get_image_path(uploaded_image)
    print(output)
    cv2.imwrite(output, img_gray)


def get_image_path(before_im):
    return "/images/%s%s" % (
        hashlib.sha1(
            (before_im.name + before_im.image.url).encode("utf-8")).hexdigest(),
        os.path.splitext(before_im.image.url)[1],
    )
