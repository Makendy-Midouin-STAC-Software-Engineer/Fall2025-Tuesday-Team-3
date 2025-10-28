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

    def test_create_restaurant_all_fields(self):
        """Test creating a restaurant with all fields."""
        from inspections.models import Restaurant

        restaurant = Restaurant.objects.create(
            camis="99999",
            name="Full Restaurant",
            address="456 Full St",
            city="Brooklyn",
            state="NY",
            zipcode="11201",
            borough="Brooklyn",
            cuisine_description="Mexican",
            phone="718-555-9999"
        )
        self.assertEqual(restaurant.camis, "99999")
        self.assertEqual(restaurant.phone, "718-555-9999")

    def test_create_inspection(self):
        """Test creating an inspection."""
        from inspections.models import Restaurant, Inspection
        from datetime import date

        restaurant = Restaurant.objects.create(name="Test Restaurant")
        inspection = Inspection.objects.create(
            restaurant=restaurant,
            date=date(2024, 1, 1),
            grade="A",
            score=10,
            summary="Clean",
            violation_code="",
            action="",
            critical_flag=""
        )
        self.assertEqual(inspection.restaurant, restaurant)
        self.assertEqual(inspection.grade, "A")
        self.assertEqual(Inspection.objects.count(), 1)

    def test_create_inspection_all_fields(self):
        """Test creating an inspection with all fields."""
        from inspections.models import Restaurant, Inspection
        from datetime import date

        restaurant = Restaurant.objects.create(name="Test Restaurant")
        inspection = Inspection.objects.create(
            restaurant=restaurant,
            date=date(2024, 6, 15),
            grade="B",
            score=18,
            summary="Minor violations noted",
            violation_code="10F",
            action="Violations cited",
            critical_flag="Critical"
        )
        self.assertEqual(inspection.violation_code, "10F")
        self.assertEqual(inspection.action, "Violations cited")
        self.assertEqual(inspection.critical_flag, "Critical")

    def test_restaurant_inspection_relationship(self):
        """Test that restaurant inspections relationship works."""
        from inspections.models import Restaurant, Inspection
        from datetime import date

        restaurant = Restaurant.objects.create(name="Test Restaurant")
        Inspection.objects.create(
            restaurant=restaurant,
            date=date(2024, 1, 1),
            grade="A"
        )
        Inspection.objects.create(
            restaurant=restaurant,
            date=date(2024, 2, 1),
            grade="B"
        )
        
        self.assertEqual(restaurant.inspections.count(), 2)

    def test_restaurant_cascade_delete(self):
        """Test that deleting restaurant deletes inspections."""
        from inspections.models import Restaurant, Inspection
        from datetime import date

        restaurant = Restaurant.objects.create(name="Test Restaurant")
        Inspection.objects.create(
            restaurant=restaurant,
            date=date(2024, 1, 1),
            grade="A"
        )
        
        restaurant.delete()
        self.assertEqual(Inspection.objects.count(), 0)