from django.db import models


class Slider(models.Model):
    slider = models.ImageField(verbose_name='Слайдер фото',
                               upload_to='photo')
    status = models.BooleanField(verbose_name='Статус',
                                 default=True)

    def __str__(self):
        return str(self.slider)

    class Meta:
        verbose_name = 'Слайдер фото'
        verbose_name_plural = 'Слайдер фото'
