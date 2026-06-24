from django.contrib import admin

from wedding.models import WeddingDay, Artists, WeddingDishes, Slider, WeddingKids, CommentWedding, MoreWedding


@admin.register(WeddingDay)
class WeddingDayAdmin(admin.ModelAdmin):
    list_display = ['groom_name', 'bride_name', 'date', 'status', 'create_ad']


@admin.register(WeddingDishes)
class WeddingDishesAdmin(admin.ModelAdmin):
    list_display = ['title', 'time', 'wedding', 'dishes_type']


@admin.register(Artists)
class ArtistsAdmin(admin.ModelAdmin):
    list_display = ['name', 'type_is', 'wedding']


@admin.register(WeddingKids)
class WeddingKidsAdmin(admin.ModelAdmin):
    list_display = ['name', 'wedding', 'status']


@admin.register(MoreWedding)
class MoreWeddingAdmin(admin.ModelAdmin):
    list_display = ['name', 'wedding', 'status']


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    pass


@admin.register(CommentWedding)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'wedding', 'date_time']

    def formatted_date(self, obj):
        return obj.your_date_field.strftime('%Y-%m-%d %H:%M')
