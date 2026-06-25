from datetime import timedelta
from datetime import time

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from wedding.models import CommentWedding, WeddingDay, WeddingDishes


class WeddingCommentTests(TestCase):
    def setUp(self):
        wedding_date = timezone.now() - timedelta(hours=1)
        self.first_wedding = WeddingDay.objects.create(
            groom_name="Алишер",
            bride_name="Малика",
            date=wedding_date,
            status=True,
        )
        self.second_wedding = WeddingDay.objects.create(
            groom_name="Шахриёр",
            bride_name="Зарина",
            date=wedding_date,
            status=True,
        )

    def test_comment_is_attached_to_wedding_from_url(self):
        response = self.client.post(
            reverse("hot_appetizers", kwargs={"pk": self.first_wedding.pk}),
            {"name": "Гость", "table": "7", "text": "Счастья молодым!"},
        )

        self.assertEqual(response.status_code, 201)
        comment = CommentWedding.objects.get()
        self.assertEqual(comment.wedding, self.first_wedding)
        self.assertNotEqual(comment.wedding, self.second_wedding)
        self.assertEqual(comment.table, 7)

    def test_each_page_uses_its_own_wedding(self):
        self.client.get(reverse("singers", kwargs={"pk": self.first_wedding.pk}))
        self.client.get(reverse("singers", kwargs={"pk": self.second_wedding.pk}))
        self.client.post(
            reverse("singers", kwargs={"pk": self.first_wedding.pk}),
            {"text": "Комментарий к первой свадьбе"},
        )

        self.assertEqual(
            CommentWedding.objects.get().wedding_id, self.first_wedding.pk
        )

    def test_empty_comment_is_rejected(self):
        response = self.client.post(
            reverse("home", kwargs={"pk": self.first_wedding.pk}), {"text": "  "}
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(CommentWedding.objects.exists())

    def test_uploaded_logo_has_priority_over_default_monogram(self):
        self.first_wedding.logo.name = "logo/custom-wedding-logo.png"
        self.first_wedding.save(update_fields=["logo"])

        response = self.client.get(
            reverse("home", kwargs={"pk": self.first_wedding.pk})
        )

        self.assertContains(response, "/media/logo/custom-wedding-logo.png")
        self.assertNotContains(response, "img/oz-monogram.webp")

    def test_default_monogram_is_used_without_uploaded_logo(self):
        response = self.client.get(
            reverse("home", kwargs={"pk": self.second_wedding.pk})
        )

        self.assertContains(response, "img/oz-monogram.webp")

    def test_base_page_includes_spa_navigation_assets(self):
        response = self.client.get(
            reverse("home", kwargs={"pk": self.first_wedding.pk})
        )

        self.assertContains(response, 'id="spa-container"')
        self.assertContains(response, "js/spa-navigation.js")

    def test_kitchen_shows_third_dishes_section(self):
        WeddingDishes.objects.create(
            wedding=self.first_wedding,
            title="Uchinchi maxsus taom",
            description="Mehmonlar uchun alohida taom",
            photo="photo/third-dish.jpg",
            time=time(21, 30),
            dishes_type="third_dishes",
        )

        response = self.client.get(
            reverse("hot_appetizers", kwargs={"pk": self.first_wedding.pk})
        )

        self.assertContains(response, "Uchinchi taom")
        self.assertContains(response, "Uchinchi maxsus taom")
