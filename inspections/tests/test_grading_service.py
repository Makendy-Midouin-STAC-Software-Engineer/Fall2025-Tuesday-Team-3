import datetime as dt

from django.conf import settings
from django.test import TestCase

from inspections.models import Restaurant, Inspection
from inspections.services.grading import GradingService, grade_restaurants


class TestGradingService(TestCase):
    def setUp(self):
        self.service = GradingService()
        self.restaurant = Restaurant.objects.create(
            camis="12345678",
            name="Test Restaurant",
            address="1 Test Way",
            city="New York",
            state="NY",
            zipcode="10001",
            borough="Manhattan",
            cuisine_description="Test",
        )

    def _inspection(self, year: int, summary: str = "Routine inspection") -> Inspection:
        date = dt.date(year, 1, 1)
        return Inspection.objects.create(
            restaurant=self.restaurant,
            date=date,
            grade="A",
            score=5,
            summary=summary,
        )

    def test_lowest_grade_for_recent_forbidden(self):
        self._inspection(2025, "Evidence of rat droppings in kitchen")
        result = self.service.grade_restaurant(self.restaurant)
        self.assertEqual(result.regraded_letter, settings.LOWEST_GRADE)
        self.assertEqual(result.star_rating, 1)
        self.assertIn("RULE_1_LOWEST_RECENT", result.explanations["rules_applied"])
        self.assertTrue(result.forbidden_years["2025"])
        self.assertIsNone(result.forbidden_years["2024"])

    def test_grade_b_when_only_2023_forbidden(self):
        self._inspection(2023, "Rodent infestation noted")
        self._inspection(2024, "Routine inspection with no issues")
        self._inspection(2025, "Routine inspection with no issues")
        result = self.service.grade_restaurant(self.restaurant)
        self.assertEqual(result.regraded_letter, "B")
        self.assertEqual(result.star_rating, 2)
        self.assertIn("RULE_2_B_2023_ONLY", result.explanations["rules_applied"])
        self.assertTrue(result.forbidden_years["2023"])
        self.assertFalse(result.forbidden_years["2024"])
        self.assertFalse(result.forbidden_years["2025"])

    def test_grade_a_when_only_old_forbidden(self):
        self._inspection(2021, "Mouse observed near storage")
        self._inspection(2023, "Routine inspection")
        self._inspection(2024, "Routine inspection")
        self._inspection(2025, "Routine inspection")
        result = self.service.grade_restaurant(self.restaurant)
        self.assertEqual(result.regraded_letter, "A")
        self.assertIn("RULE_3_A_OLD_ONLY", result.explanations["rules_applied"])
        self.assertEqual(result.star_rating, 2)
        self.assertTrue(result.forbidden_years["2021"])
        self.assertFalse(result.forbidden_years["2023"])

    def test_unknown_when_no_inspections(self):
        result = self.service.grade_restaurant(self.restaurant)
        self.assertEqual(result.regraded_letter, "Unknown")
        self.assertEqual(result.star_rating, 2)
        self.assertIn("RULE_UNKNOWN_NO_DATA", result.explanations["rules_applied"])
        self.assertIn("STARS_2_DEFAULT", result.explanations["rules_applied"])

    def test_negation_suppresses_forbidden_hit(self):
        self._inspection(2025, "No rats observed during inspection")
        result = self.service.grade_restaurant(self.restaurant)
        self.assertEqual(result.regraded_letter, "A")
        self.assertFalse(result.forbidden_years["2025"])
        self.assertEqual(result.explanations["forbidden_hits"], [])
        self.assertGreater(len(result.explanations["negations"]), 0)
        negation_terms = {entry["negation"] for entry in result.explanations["negations"]}
        self.assertIn("no", negation_terms)

    def test_grade_restaurants_updates_persisted_fields(self):
        self._inspection(2025, "Rat infestation found")
        grade_restaurants([self.restaurant], service=self.service)
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.regraded_letter, settings.LOWEST_GRADE)
        self.assertEqual(self.restaurant.star_rating, 1)
        self.assertTrue(self.restaurant.forbidden_years["2025"])

