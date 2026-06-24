from datetime import timedelta

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import TemplateView

from desire.models import OurDesire
from wedding.models import Artists, CommentWedding, Slider, WeddingDay, WeddingDishes


class WeddingCommentMixin:
    """Shared wedding lookup, comment context and safe comment creation."""

    def get_wedding(self):
        if not hasattr(self, "_wedding"):
            self._wedding = get_object_or_404(
                WeddingDay.objects.prefetch_related(
                    "wed_dish", "wedding_kids", "wedding_more"
                ),
                pk=self.kwargs["pk"],
                status=True,
            )
        return self._wedding

    def add_comment_context(self, context):
        wedding = self.get_wedding()
        now = timezone.localtime()
        wedding_date = timezone.localtime(wedding.date)
        end_date = wedding_date + timedelta(hours=24)
        remaining_seconds = max(0, int((end_date - now).total_seconds()))

        context.update(
            {
                "wedding": wedding,
                "wedding_pk": wedding,
                "comments": CommentWedding.objects.filter(wedding=wedding).order_by(
                    "-date_time"
                ),
                "current_datetime": now,
                "wedding_date": wedding_date,
                "end_date": end_date,
                "hours": remaining_seconds // 3600,
                "minutes": (remaining_seconds % 3600) // 60,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        wedding = self.get_wedding()
        text = request.POST.get("text", "").strip()
        name = request.POST.get("name", "").strip()[:255]
        table_value = request.POST.get("table", "").strip()

        if not text:
            return JsonResponse(
                {"message": "Напишите пожелание перед отправкой."}, status=400
            )

        table = int(table_value) if table_value.isdigit() else None
        if table is not None and table <= 0:
            table = None

        comment = CommentWedding.objects.create(
            wedding=wedding,
            name=name or None,
            table=table,
            text=text,
        )
        return JsonResponse(
            {
                "message": "Пожелание сохранено",
                "comment": {
                    "id": comment.pk,
                    "name": comment.name or "Гость",
                    "table": comment.table,
                    "text": comment.text,
                    "date_time": timezone.localtime(comment.date_time).isoformat(),
                },
            },
            status=201,
        )


class WeddingDetailView(WeddingCommentMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.add_comment_context(context)
        context["desire"] = OurDesire.objects.filter(status=True).order_by("-id").first()
        context["wedding_photo"] = Slider.objects.filter(wedding=self.get_wedding(), status=True)
        return context


class HotAppetizersList(WeddingCommentMixin, TemplateView):
    template_name = "kitchen.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wedding = self.get_wedding()
        self.add_comment_context(context)
        dishes = WeddingDishes.objects.filter(wedding=wedding).order_by("time")
        context.update(
            {
                "kitchen": dishes.filter(dishes_type="hot_snack"),
                "dishes": dishes.filter(dishes_type="dishes"),
                "second_dishes": dishes.filter(dishes_type="second_dishes"),
                "desert": dishes.filter(dishes_type="desert"),
                "wedding_photo": Slider.objects.filter(wedding=wedding, status=True),
            }
        )
        return context


class ArtistList(WeddingCommentMixin, TemplateView):
    template_name = "artists.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wedding = self.get_wedding()
        self.add_comment_context(context)
        artists = Artists.objects.filter(wedding=wedding).order_by("position")
        context.update(
            {
                "organizer": artists.filter(type_is="organizer"),
                "leading": artists.filter(type_is="leading"),
                "artists": artists.filter(type_is__in=["artist", "group"]),
                "dance_group": artists.filter(type_is="dance_group"),
                "wedding_photo": Slider.objects.filter(wedding=wedding, status=True),
            }
        )
        return context
