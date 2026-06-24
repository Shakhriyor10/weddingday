from django.db import models


class OurDesire(models.Model):
    text = models.TextField(verbose_name='Поздравления')
    status = models.BooleanField(verbose_name='Статус',
                                 default=True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Поздравления'
        verbose_name_plural = 'Поздравления'
