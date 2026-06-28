from datetime import timedelta

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from desire.models import OurDesire
from wedding.models import Artists, CommentWedding, Slider, WeddingDay, WeddingDishes


COMMENT_IDS_SESSION_KEY = "wedding_comment_ids"


def get_session_comment_ids(request):
    return [
        int(comment_id)
        for comment_id in request.session.get(COMMENT_IDS_SESSION_KEY, [])
        if str(comment_id).isdigit()
    ]


def remember_session_comment(request, comment):
    comment_ids = get_session_comment_ids(request)
    if comment.pk not in comment_ids:
        comment_ids.append(comment.pk)
    request.session[COMMENT_IDS_SESSION_KEY] = comment_ids
    request.session.modified = True


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
        start_date = wedding_date - timedelta(days=7)
        end_date = wedding_date + timedelta(days=7)
        remaining_seconds = max(0, int((end_date - now).total_seconds()))
        session_comment_ids = set(get_session_comment_ids(self.request))
        comments = list(CommentWedding.objects.filter(wedding=wedding).order_by("-date_time"))
        for comment in comments:
            comment.can_delete = comment.pk in session_comment_ids

        context.update(
            {
                "wedding": wedding,
                "wedding_pk": wedding,
                "comments": comments,
                "current_datetime": now,
                "comment_start_date": start_date,
                "wedding_date": wedding_date,
                "end_date": end_date,
                "comments_open": start_date <= now <= end_date,
                "hours": remaining_seconds // 3600,
                "minutes": (remaining_seconds % 3600) // 60,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        wedding = self.get_wedding()
        text = request.POST.get("text", "").strip()
        name = request.POST.get("name", "").strip()[:255]
        now = timezone.localtime()
        wedding_date = timezone.localtime(wedding.date)
        start_date = wedding_date - timedelta(days=7)
        end_date = wedding_date + timedelta(days=7)

        if not start_date <= now <= end_date:
            return JsonResponse(
                {"message": "Izoh qoldirish faqat to'ydan 7 kun oldin va 7 kun keyin mumkin."},
                status=403,
            )
        if not text:
            return JsonResponse(
                {"message": "Izoh matnini yozing."},
                status=400,
            )
        comment = CommentWedding.objects.create(
            wedding=wedding,
            name=name or None,
            text=text,
        )
        remember_session_comment(request, comment)
        return JsonResponse(
            {
                "message": "Izoh saqlandi",
                "comment": {
                    "id": comment.pk,
                    "name": comment.name or "Mehmon",
                    "text": comment.text,
                    "date_time": timezone.localtime(comment.date_time).isoformat(),
                    "can_delete": True,
                    "delete_url": f"/{wedding.pk}/comments/{comment.pk}/delete/",
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
                "third_dishes": dishes.filter(dishes_type="third_dishes"),
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


@require_POST
def delete_comment(request, pk, comment_pk):
    wedding = get_object_or_404(WeddingDay, pk=pk, status=True)
    comment = get_object_or_404(CommentWedding, pk=comment_pk, wedding=wedding)
    comment_ids = get_session_comment_ids(request)
    if comment.pk not in comment_ids:
        return JsonResponse({"message": "Bu izohni o'chirish mumkin emas."}, status=403)

    comment.delete()
    request.session[COMMENT_IDS_SESSION_KEY] = [
        comment_id for comment_id in comment_ids if comment_id != comment.pk
    ]
    request.session.modified = True
    return JsonResponse({"message": "Izoh o'chirildi."})
