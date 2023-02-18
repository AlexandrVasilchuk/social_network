from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
from PIL import Image


def image(name: str = Faker().bothify(text='????.gif')) -> SimpleUploadedFile:
    file = BytesIO()
    Image.new('RGBA', size=(1, 1), color=(155, 0, 0)).save(file, 'gif')
    file.name = name
    file.seek(0)
    return SimpleUploadedFile(
        name=name,
        content=file.read(),
        content_type='image/gif',
    )
