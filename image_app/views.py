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
        uploaded_image.edit_image = f"{uploaded_image.name}_{uploaded_image.id}_gray.jpg"
        uploaded_image.save()
        return redirect("upload")
    return render(request, "image_app/index.html", params)


def change_gray(uploaded_image):
    url = uploaded_image.image.url
    path = str(settings.BASE_DIR) + url

    img = cv2.imread(path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    output = str(settings.BASE_DIR) + f"/media/{uploaded_image.name}_{uploaded_image.id}_gray.jpg"
    cv2.imwrite(output, img_gray)
