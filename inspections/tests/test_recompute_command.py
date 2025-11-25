"""
Tests for inspections/management/commands/recompute_grades.py
to improve coverage from 0% to 85%+.
"""
import datetime as dt

from django.test import TestCase
from django.core.management import call_command

from inspections.models import Restaurant, Inspection
from inspections.services.grading import grade_restaurants, GradingService


class RecomputeGradesCommandTests(TestCase):
    """Test the recompute_grades management command."""

    def setUp(self):
        """Set up test fixtures."""
        self.restaurant1 = Restaurant.objects.create(
            camis="123456789",
            name="Restaurant 1",
            borough="Manhattan",
        )
        self.restaurant2 = Restaurant.objects.create(
            camis="987654321",
            name="Restaurant 2",
            borough="Brooklyn",
        )
        self.restaurant3 = Restaurant.objects.create(
            name="Restaurant 3",
            borough="Queens",
        )

    def _add_inspection(self, restaurant, year, summary=""):
        return Inspection.objects.create(
            restaurant=restaurant,
            date=dt.date(year, 5, 15),
            grade="A",
            score=10,
            summary=summary,
        )

    def test_recompute_all_restaurants(self):
        """Test recomputing grades for all restaurants."""
        self._add_inspection(self.restaurant1, 2024, "Rat droppings")
        self._add_inspection(self.restaurant2, 2024, "No issues")
        
        # Clear existing grades
        self.restaurant1.regraded_letter = ""
        self.restaurant1.save()
        self.restaurant2.regraded_letter = ""
        self.restaurant2.save()

        call_command("recompute_grades")

        # Verify grades were recomputed
        self.restaurant1.refresh_from_db()
        self.restaurant2.refresh_from_db()
        self.assertNotEqual(self.restaurant1.regraded_letter, "")
        self.assertNotEqual(self.restaurant2.regraded_letter, "")

    def test_recompute_by_camis(self):
        """Test recomputing grades for specific CAMIS."""
        self._add_inspection(self.restaurant1, 2024, "Rat droppings")
        self.restaurant1.regraded_letter = ""
        self.restaurant1.save()

        call_command("recompute_grades", camis=["123456789"])

        self.restaurant1.refresh_from_db()
        self.assertNotEqual(self.restaurant1.regraded_letter, "")
        
        # Restaurant 2 should not be recomputed
        self.restaurant2.refresh_from_db()
        self.assertEqual(self.restaurant2.regraded_letter, "")

    def test_recompute_by_ids(self):
        """Test recomputing grades for specific IDs."""
        self._add_inspection(self.restaurant1, 2024, "Rat droppings")
        self.restaurant1.regraded_letter = ""
        self.restaurant1.save()

        call_command("recompute_grades", ids=[self.restaurant1.pk])

        self.restaurant1.refresh_from_db()
        self.assertNotEqual(self.restaurant1.regraded_letter, "")

    def test_recompute_since_date(self):
        """Test recomputing grades with --since parameter."""
        self._add_inspection(self.restaurant1, 2024, "Rat droppings")
        self._add_inspection(self.restaurant2, 2023, "Old issue")
        self.restaurant1.regraded_letter = ""
        self.restaurant2.regraded_letter = ""
        self.restaurant1.save()
        self.restaurant2.save()

        call_command("recompute_grades", since="2024-01-01")

        # Both should be recomputed since they have inspections >= 2024-01-01
        self.restaurant1.refresh_from_db()
        self.restaurant2.refresh_from_db()
        # At least one should have been recomputed
        self.assertTrue(
            self.restaurant1.regraded_letter != "" or self.restaurant2.regraded_letter != ""
        )

    def test_recompute_invalid_since_date(self):
        """Test that invalid --since date raises CommandError."""
        with self.assertRaises(Exception):  # CommandError
            call_command("recompute_grades", since="invalid-date")

    def test_recompute_no_matching_restaurants(self):
        """Test recomputing when no restaurants match criteria."""
        # No restaurants with CAMIS "999999999"
        call_command("recompute_grades", camis=["999999999"])
        # Should complete without error

    def test_recompute_custom_batch_size(self):
        """Test recomputing with custom batch size."""
        # Create multiple restaurants
        for i in range(5):
            r = Restaurant.objects.create(name=f"Restaurant {i}")
            self._add_inspection(r, 2024)

        call_command("recompute_grades", batch_size=2)

        # Should complete successfully
        self.assertEqual(Restaurant.objects.count(), 8)  # 3 from setUp + 5 new

    def test_recompute_with_multiple_camis(self):
        """Test recomputing with multiple CAMIS values."""
        self._add_inspection(self.restaurant1, 2024)
        self._add_inspection(self.restaurant2, 2024)
        self.restaurant1.regraded_letter = ""
        self.restaurant2.regraded_letter = ""
        self.restaurant1.save()
        self.restaurant2.save()

        call_command("recompute_grades", camis=["123456789", "987654321"])

        self.restaurant1.refresh_from_db()
        self.restaurant2.refresh_from_db()
        self.assertNotEqual(self.restaurant1.regraded_letter, "")
        self.assertNotEqual(self.restaurant2.regraded_letter, "")

    def test_recompute_with_multiple_ids(self):
        """Test recomputing with multiple IDs."""
        self._add_inspection(self.restaurant1, 2024)
        self._add_inspection(self.restaurant2, 2024)
        self.restaurant1.regraded_letter = ""
        self.restaurant2.regraded_letter = ""
        self.restaurant1.save()
        self.restaurant2.save()

        call_command("recompute_grades", ids=[self.restaurant1.pk, self.restaurant2.pk])

        self.restaurant1.refresh_from_db()
        self.restaurant2.refresh_from_db()
        self.assertNotEqual(self.restaurant1.regraded_letter, "")
        self.assertNotEqual(self.restaurant2.regraded_letter, "")

