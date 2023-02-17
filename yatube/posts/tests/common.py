from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from faker import Faker


def image() -> SimpleUploadedFile:
    name = Faker().bothify(text='????.gif')
    file = BytesIO()
    image = Image.new('RGBA', size=(1, 1), color=(155, 0, 0))
    image.save(file, 'gif')
    file.name = name
    file.seek(0)
    return SimpleUploadedFile(
        name=name,
        content=file.read(),
        content_type='image/gif',
    )
