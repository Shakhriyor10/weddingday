from django.db import models

from wedding.choices import GUEST_TYPE, DISHES_TYPE, WEDDING_TYPE


class Slider(models.Model):
    mob_photo = models.ImageField(verbose_name='Слайдер фона для мобильного',
                                  upload_to='background')
    wedding = models.ForeignKey('WeddingDay',
                                verbose_name='Свадьба',
                                related_name='photo',
                                on_delete=models.CASCADE)
    status = models.BooleanField(verbose_name='Статус',
                                 default=True)

    def __str__(self):
        return str(self.wedding)

    class Meta:
        verbose_name = 'Слайдер фото'
        verbose_name_plural = 'Слайдер фото'


class WeddingKids(models.Model):
    name = models.CharField(verbose_name='Имя фамилия',
                            max_length=255)
    wedding = models.ForeignKey('WeddingDay',
                                verbose_name='Свадьба',
                                on_delete=models.CASCADE,
                                related_name='wedding_kids')
    status = models.BooleanField(verbose_name='Статус',
                                 default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Свадьба детей'
        verbose_name_plural = 'Свадьба детей'


class MoreWedding(models.Model):
    name = models.CharField(verbose_name='Имя фамилия',
                            max_length=255)
    wedding = models.ForeignKey('WeddingDay',
                                verbose_name='Свадьба',
                                on_delete=models.CASCADE,
                                related_name='wedding_more')
    status = models.BooleanField(verbose_name='Статус',
                                 default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Кушалок туй'
        verbose_name_plural = 'Кушалок туй'


class WeddingDay(models.Model):
    groom_name = models.CharField(verbose_name='Имя жениха',
                                  max_length=255)
    image_groom = models.ImageField(verbose_name='Фото Жениха',
                                    upload_to='photo',
                                    blank=True,
                                    null=True)
    bride_name = models.CharField(verbose_name='Имя невесты',
                                  max_length=255,
                                  blank=True,
                                  null=True)
    image_bride = models.ImageField(verbose_name='Фото Невесты',
                                    upload_to='photo',
                                    blank=True,
                                    null=True)
    first_folder = models.CharField(verbose_name='Заменя первой папки',
                                    max_length=255,
                                    blank=True,
                                    null=True)
    second_folder = models.CharField(verbose_name='Заменя второй папки',
                                     max_length=255,
                                     blank=True,
                                     null=True)
    date = models.DateTimeField(verbose_name='Дата и время свадьбы')
    # time = models.TimeField(verbose_name='Время свадьбы')
    logo = models.ImageField(upload_to='logo', blank=True, null=True)
    status = models.BooleanField(verbose_name='Статус',
                                 default=0)
    create_ad = models.DateField(auto_now_add=True, verbose_name='Создано')
    wedding_type = models.CharField(verbose_name='Тип свадьбы',
                                    choices=WEDDING_TYPE,
                                    default='wedding',
                                    max_length=255)
    congratulations = models.TextField(verbose_name='Поздравление',
                                       blank=True, null=True)
    link_telegram = models.CharField(verbose_name='Ссылка телеграма',
                                     max_length=255,
                                     blank=True,
                                     null=True)
    link_inst = models.CharField(verbose_name='Ссылка инстаграм',
                                 max_length=255,
                                 blank=True,
                                 null=True)
    link_facebook = models.CharField(verbose_name='Ссылка фейзбук',
                                     max_length=255,
                                     blank=True,
                                     null=True)
    restaurant = models.CharField(verbose_name='Ресторан',
                                  max_length=255,
                                  blank=True,
                                  null=True)

    def __str__(self):
        return f"{self.groom_name} и {self.bride_name}"

    class Meta:
        verbose_name = 'Свадьбу'
        verbose_name_plural = 'Свадьбы'


class WeddingDishes(models.Model):
    title = models.CharField(verbose_name='Название(Блюдо)',
                             max_length=255)
    description = models.TextField(verbose_name='Описание',
                                   blank=True,
                                   null=True)
    photo = models.ImageField(verbose_name='Фото',
                              upload_to='photo')
    time = models.TimeField(verbose_name='Время подачи')
    wedding = models.ForeignKey('WeddingDay', verbose_name='На свадьбу',
                                related_name='wed_dish',
                                on_delete=models.SET_NULL,
                                null=True)
    dishes_type = models.CharField(verbose_name='Категория блюд',
                                   max_length=255,
                                   choices=DISHES_TYPE,
                                   default='hot_snack'
                                   )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Блюда, Десерты и горячие закуски'
        verbose_name_plural = 'Блюда, Десерты и горячие закуски'


class Artists(models.Model):
    name = models.CharField(verbose_name='Название(Группы), или Имя Артиста',
                            max_length=255)
    type_is = models.CharField(verbose_name='Тип гостей',
                               choices=GUEST_TYPE, default='artist',
                               max_length=255)
    wedding = models.ForeignKey('WeddingDay', verbose_name='Свадьба',
                                on_delete=models.SET_NULL,
                                null=True,
                                related_name='artist')
    photo = models.ImageField(verbose_name='Фото', upload_to='Photo')
    description = models.TextField(verbose_name='Описание',
                                   blank=True,
                                   null=True)
    position = models.SmallIntegerField(verbose_name='Позиция',
                                        default=0)
    link = models.CharField(verbose_name='Ссылка', max_length=255,
                            blank=True, null=True)
    entry_time = models.TimeField(verbose_name='Время вступление',
                                  blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Артисты, выдущие и группы'
        verbose_name_plural = 'Артисты, выдущие и группы'


class CommentWedding(models.Model):
    name = models.CharField(verbose_name='Имя',
                            max_length=255,
                            blank=True,
                            null=True)
    table = models.IntegerField(verbose_name='Стол(номер)',
                                blank=True,
                                null=True)
    text = models.TextField(verbose_name='Пожелание')
    wedding = models.ForeignKey('WeddingDay', verbose_name='Свадьба',
                                on_delete=models.CASCADE)
    date_time = models.DateTimeField(verbose_name='Время созданно',
                                     auto_now_add=True, )

    # the_end_comment = models.DateTimeField(verbose_name='Дата и время свадьбы закончиться')

    def __str__(self):
        return str(self.date_time)

    class Meta:
        verbose_name = 'Комментарий к событию'
        verbose_name_plural = 'Комментарий к событию'
