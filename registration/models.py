from django.db import models
from django.contrib.auth.models import User
from PIL import Image
# Create your models here.

class Profile(models.Model):
    #one to one relationship
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='profile_pics')
    phone_number = models.CharField(max_length=10, unique=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    #overriding save method from the base class
    # def save(self, *args, **kwargs):
    #         super(Profile, self).save(*args, **kwargs)

    #         image = Image.open(self.image.path)
    #         if image.height > 300 or image.width > 300:
    #             output_size = (300, 300)
    #             image.thumbnail(output_size)
    #             image.save(self.image.path)


    # def save(self, *args, **kwargs):
    #     super(Profile, self).save(*args, **kwargs)
    #     img = Image.open(self.image)
    #     if img.height > 300 or img.width > 300:
    #         from django.core.files.base import ContentFile
    #         from io import BytesIO
    #         output_size = (300, 300)
    #         img.thumbnail(output_size)
    #         thumb_io = BytesIO()
    #         img.save(thumb_io, img.format)
    #         file_name = self.image.name
    #         self.image.save(
    #                    file_name,
    #                     ContentFile(
    #                                 thumb_io.getvalue()),
    #                     save=False)
    #         super(Profile, self).save(*args, **kwargs)
    