import datetime as dt

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from inspections.models import Restaurant, Inspection
from inspections.services.grading import grade_restaurants, GradingService


class TestRestaurantAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.restaurant = Restaurant.objects.create(
            camis="987654321",
            name="Sample Spot",
            address="123 Example Ave",
            city="New York",
            state="NY",
            zipcode="10002",
            borough="Manhattan",
            cuisine_description="American",
        )

    def _add_inspection(self, year: int, summary: str, grade: str = "A"):
        Inspection.objects.create(
            restaurant=self.restaurant,
            date=dt.date(year, 5, 15),
            grade=grade,
            score=10,
            summary=summary,
        )

    def _regrade(self):
        grade_restaurants([self.restaurant], service=GradingService())
        self.restaurant.refresh_from_db()

    def test_search_returns_regraded_fields_with_default_letter_display(self):
        self._add_inspection(2025, "Rat droppings observed in pantry", grade="C")
        self._regrade()

        url = reverse("restaurant-search")
        response = self.client.get(url, {"q": "sample"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreaterEqual(len(payload["results"]), 1)
        result = payload["results"][0]

        self.assertEqual(result["regraded_letter"], settings.LOWEST_GRADE)
        self.assertEqual(result["star_rating"], 1)
        self.assertEqual(result["display_mode"], "letter")
        self.assertEqual(result["display_value"], settings.LOWEST_GRADE)
        self.assertEqual(result["display_source"], "regraded_letter")
        self.assertEqual(result["original_agency_grade"], "C")
        self.assertIn("forbidden_years", result)
        self.assertTrue(result["forbidden_years"]["2025"])

    @override_settings(STAR_DISPLAY_ENABLED=True)
    def test_search_supports_star_display(self):
        self._add_inspection(2021, "No pests observed")
        self._add_inspection(2022, "No pests observed")
        self._add_inspection(2023, "No pests observed")
        self._add_inspection(2024, "No pests observed")
        self._add_inspection(2025, "No pests observed")
        self._regrade()

        url = reverse("restaurant-search")
        response = self.client.get(url, {"q": "sample", "display": "stars"})
        self.assertEqual(response.status_code, 200)
        result = response.json()["results"][0]

        self.assertEqual(result["display_mode"], "stars")
        self.assertEqual(result["display_source"], "star_rating")
        self.assertEqual(result["display_value"], 4)
        self.assertEqual(result["star_rating"], 4)
        self.assertEqual(result["regraded_letter"], "A")

    @override_settings(STAR_DISPLAY_ENABLED=True)
    def test_detail_endpoint_includes_display_fields(self):
        self._add_inspection(2023, "Rodent infestation noted")
        self._add_inspection(2024, "No pests observed")
        self._add_inspection(2025, "No pests observed")
        self._regrade()

        url = reverse("restaurant-detail", kwargs={"pk": self.restaurant.pk})
        response = self.client.get(url, {"display": "stars"})
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["display_mode"], "stars")
        self.assertEqual(data["display_source"], "star_rating")
        self.assertEqual(data["display_value"], 2)
        self.assertEqual(data["star_rating"], 2)
        self.assertEqual(data["regraded_letter"], "B")
        self.assertEqual(data["original_agency_grade"], "A")
        self.assertIn("forbidden_years", data)
        self.assertTrue(data["forbidden_years"]["2023"])

