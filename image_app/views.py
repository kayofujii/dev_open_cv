import hashlib
import os.path

import cv2
from django.conf import settings
from django.shortcuts import redirect, render
from PIL import Image, ImageDraw, ImageFilter

from .forms import ImageForm
from .models import UploadedImage


def upload_image(request):
    params = {}
    params["form"] = ImageForm()
    params["uploaded_images"] = UploadedImage.objects.all().order_by(
        '-uploaded_at')
    if request.method == "POST":
        form = ImageForm(request.POST)
        if form.is_valid():
            uploaded_image = UploadedImage()
            uploaded_image.name = form.cleaned_data["name"]
            uploaded_image.image = request.FILES.get("image")
            uploaded_image.product_im = request.FILES.get("product_im")
            uploaded_image.save()
            return redirect("upload")

    return render(request, "image_app/index.html", params)


def edit_image(request, id):
    params = {}
    uploaded_image = UploadedImage.objects.get(id=id)
    if "button_gray" in request.POST:
        recognize_face(uploaded_image)
        # change_gray(uploaded_image)
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


def get_tmp_image_path(before_im, dir):
    os.makedirs(str(settings.BASE_DIR) +
                f"/media/tmp/{dir}", exist_ok=True)
    return f"/media/tmp/{dir}/%s%s" % (
        hashlib.sha1(
            (before_im.name + before_im.image.url).encode("utf-8")).hexdigest(),
        ".png",
    )


def recognize_face(uploaded_image):
    # https://note.nkmk.me/image-processing/
    # 参考:https://note.nkmk.me/python-opencv-face-detection-haar-cascade/
    face_cascade = cv2.CascadeClassifier(
        settings.OPENCV_PATH + '/data/haarcascades/haarcascade_frontalface_default.xml')

    url = uploaded_image.image.url
    path = str(settings.BASE_DIR) + url
    src = cv2.imread(path)
    # src_gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(src)

    for x, y, w, h in faces:
        # cv2.rectangle(src, (x, y), (x + w, y + h), (255, 0, 0), 2)
        # face = src[y: y + h, x: x + w]
        # face = src[y-130:y+h+80, x-80:x+w+80]
        face = src[y-15:y+h+30, x-15:x+w+30]
        # face_gray = src_gray[y: y + h, x: x + w]
    im_rgba = face.copy()
    print(im_rgba)

    # opencv→pillow変換 https://qiita.com/derodero24/items/f22c22b22451609908ee
    im_rgba = cv2.cvtColor(im_rgba, cv2.COLOR_BGR2RGB)
    im_rgba = Image.fromarray(im_rgba)
    # 丸を作成
    im_a = Image.new("L", im_rgba.size, 0)
    draw = ImageDraw.Draw(im_a)
    draw.ellipse((0, 0, im_rgba.size[0]+10, im_rgba.size[0]+10), fill=255)
    im_a = im_a.filter(ImageFilter.GaussianBlur(4))
    # draw.ellipse((0, 0, 300, 400), fill=255)

    # 丸に顔をいれる
    im_rgba.putalpha(im_a)
    # im_rgba_crop = im_rgba.crop((0, 0, 300, 400))
    im_rgba_crop = im_rgba.crop(
        (0, 0, im_rgba.size[0]+20, im_rgba.size[0]+20))
    im_rgba_crop.save(str(settings.BASE_DIR) +
                      get_tmp_image_path(uploaded_image, 'crop'))

    pro_path = str(settings.BASE_DIR) + uploaded_image.product_im.url
    pro_im = Image.open(pro_path)
    copy_pro_im = pro_im.copy()
    copy_pro_im.paste(im_rgba_crop, (100, 50))
    copy_pro_im.save(str(settings.BASE_DIR) +
                     get_tmp_image_path(uploaded_image, 'paste'))

    # im_rgba_crop.save(str(settings.BASE_DIR) +
    #                   get_tmp_image_path(uploaded_image))

    output = str(settings.BASE_DIR) + '/media' + \
        get_image_path(uploaded_image)

    cv2.imwrite(output, face)
