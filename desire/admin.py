from django.contrib import admin

from desire.models import OurDesire


@admin.register(OurDesire)
class OurDesireAdmin(admin.ModelAdmin):
    pass
