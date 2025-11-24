"""
Basic smoke tests for SafeEatsNYC Django app.
"""

from django.test import TestCase
from django.contrib.auth.models import User


class SmokeTest(TestCase):
    """Basic smoke test to verify Django runs correctly."""

    def test_true_is_true(self):
        """Simple assertion that True is True."""
        self.assertTrue(True)

    def test_restaurant_model_exists(self):
        """Verify Restaurant model is importable."""
        from inspections.models import Restaurant

        self.assertIsNotNone(Restaurant)

    def test_inspection_model_exists(self):
        """Verify Inspection model is importable."""
        from inspections.models import Inspection

        self.assertIsNotNone(Inspection)

    def test_create_restaurant(self):
        """Test creating a restaurant in the database."""
        from inspections.models import Restaurant

        restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            address="123 Test St",
            city="New York",
            state="NY",
            zipcode="10001",
            borough="Manhattan",
            cuisine_description="American",
        )
        self.assertEqual(restaurant.name, "Test Restaurant")
        self.assertEqual(Restaurant.objects.count(), 1)

    def test_restaurant_str_method(self):
        """Test Restaurant __str__ method for coverage."""
        from inspections.models import Restaurant

        restaurant = Restaurant.objects.create(name="Test Restaurant")
        self.assertEqual(str(restaurant), "Test Restaurant")

    def test_inspection_str_method(self):
        """Test Inspection __str__ method for coverage."""
        import datetime as dt
        from inspections.models import Restaurant, Inspection

        restaurant = Restaurant.objects.create(name="Test Restaurant")
        inspection = Inspection.objects.create(
            restaurant=restaurant,
            date=dt.date(2024, 5, 15),
        )
        expected = "Test Restaurant (2024-05-15)"
        self.assertEqual(str(inspection), expected)