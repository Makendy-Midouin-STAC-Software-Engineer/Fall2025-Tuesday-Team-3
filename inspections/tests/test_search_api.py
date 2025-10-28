"""
Tests for API views in the inspections app.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date

from inspections.models import Restaurant, Inspection


class RestaurantSearchViewTest(TestCase):
    """Test the restaurant search API endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create test restaurants
        self.restaurant1 = Restaurant.objects.create(
            camis="12345",
            name="Joe's Pizza",
            address="123 Main St",
            city="New York",
            state="NY",
            zipcode="10001",
            borough="Manhattan",
            cuisine_description="Pizza",
            phone="212-555-0100",
        )

        self.restaurant2 = Restaurant.objects.create(
            camis="67890",
            name="Burger King",
            address="456 Broadway",
            city="Brooklyn",
            state="NY",
            zipcode="11201",
            borough="Brooklyn",
            cuisine_description="American",
            phone="718-555-0200",
        )

        # Create inspections
        Inspection.objects.create(
            restaurant=self.restaurant1,
            date=date(2024, 1, 15),
            grade="A",
            score=12,
            summary="Clean and sanitary",
            violation_code="",
            action="",
            critical_flag="",
        )

        Inspection.objects.create(
            restaurant=self.restaurant2,
            date=date(2024, 2, 20),
            grade="B",
            score=15,
            summary="Minor violations",
            violation_code="10F",
            action="Violations cited",
            critical_flag="Critical",
        )

    def test_search_by_name(self):
        """Test searching by restaurant name."""
        url = reverse("restaurant-search")
        response = self.client.get(url, {"q": "Pizza"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Joe's Pizza")

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        url = reverse("restaurant-search")
        response = self.client.get(url, {"q": "joe's"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_with_borough_filter(self):
        """Test searching with borough filter."""
        url = reverse("restaurant-search")
        response = self.client.get(url, {"borough": "Manhattan"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["borough"], "Manhattan")

    def test_search_with_cuisine_filter(self):
        """Test searching with cuisine filter."""
        url = reverse("restaurant-search")
        response = self.client.get(url, {"cuisine": "Pizza"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["cuisine_description"], "Pizza")

    def test_search_multiple_filters(self):
        """Test searching with multiple filters."""
        url = reverse("restaurant-search")
        response = self.client.get(url, {"q": "Joe", "borough": "Manhattan"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_no_params_raises_error(self):
        """Test that search without params raises validation error."""
        url = reverse("restaurant-search")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_search_latest_inspection_included(self):
        """Test that latest inspection is included in results."""
        url = reverse("restaurant-search")
        response = self.client.get(url, {"q": "Pizza"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("latest_inspection", response.data[0])
        self.assertEqual(response.data[0]["latest_inspection"]["grade"], "A")

    def test_search_wildcard(self):
        """Test wildcard search with *."""
        url = reverse("restaurant-search")
        response = self.client.get(url, {"q": "*", "borough": "Manhattan"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class RestaurantDetailViewTest(TestCase):
    """Test the restaurant detail API endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        self.restaurant = Restaurant.objects.create(
            camis="11111",
            name="Test Restaurant",
            address="999 Test Ave",
            city="Queens",
            state="NY",
            zipcode="11101",
            borough="Queens",
            cuisine_description="Italian",
            phone="718-555-0300",
        )

        # Create multiple inspections
        Inspection.objects.create(
            restaurant=self.restaurant,
            date=date(2024, 1, 10),
            grade="A",
            score=10,
            summary="Good",
            violation_code="",
            action="",
            critical_flag="",
        )

        Inspection.objects.create(
            restaurant=self.restaurant,
            date=date(2024, 3, 15),
            grade="B",
            score=14,
            summary="Fair",
            violation_code="10F",
            action="Actions required",
            critical_flag="Critical",
        )

    def test_get_restaurant_detail(self):
        """Test retrieving restaurant detail with inspections."""
        url = reverse("restaurant-detail", kwargs={"pk": self.restaurant.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Restaurant")
        self.assertIn("inspections", response.data)
        self.assertEqual(len(response.data["inspections"]), 2)

    def test_get_nonexistent_restaurant_404(self):
        """Test getting non-existent restaurant returns 404."""
        url = reverse("restaurant-detail", kwargs={"pk": 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BoroughListViewTest(TestCase):
    """Test the borough list API endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        Restaurant.objects.create(name="Restaurant 1", borough="Manhattan")
        Restaurant.objects.create(name="Restaurant 2", borough="Brooklyn")
        Restaurant.objects.create(name="Restaurant 3", borough="Queens")
        Restaurant.objects.create(name="Restaurant 4", borough="Manhattan")

    def test_get_boroughs_list(self):
        """Test retrieving list of unique boroughs."""
        url = reverse("borough-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Brooklyn", response.data)
        self.assertIn("Manhattan", response.data)
        self.assertIn("Queens", response.data)
        # Should not have duplicates
        self.assertEqual(len(response.data), 3)

    def test_boroughs_sorted(self):
        """Test that boroughs are returned sorted."""
        url = reverse("borough-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sorted_boroughs = sorted(response.data)
        self.assertEqual(response.data, sorted_boroughs)


class ModelTests(TestCase):
    """Test model functionality."""

    def test_restaurant_str(self):
        """Test Restaurant __str__ method."""
        restaurant = Restaurant.objects.create(name="Test Place")
        self.assertEqual(str(restaurant), "Test Place")

    def test_inspection_str(self):
        """Test Inspection __str__ method."""
        restaurant = Restaurant.objects.create(name="Test Place")
        inspection = Inspection.objects.create(
            restaurant=restaurant, date=date(2024, 5, 1), grade="A"
        )
        expected = f"Test Place ({date(2024, 5, 1)})"
        self.assertEqual(str(inspection), expected)

    def test_inspection_ordering(self):
        """Test that inspections are ordered by date descending."""
        restaurant = Restaurant.objects.create(name="Test Place")

        Inspection.objects.create(restaurant=restaurant, date=date(2024, 1, 1))
        Inspection.objects.create(restaurant=restaurant, date=date(2024, 3, 1))
        Inspection.objects.create(restaurant=restaurant, date=date(2024, 2, 1))

        inspections = Inspection.objects.filter(restaurant=restaurant)
        dates = [inv.date for inv in inspections]

        self.assertEqual(dates, [date(2024, 3, 1), date(2024, 2, 1), date(2024, 1, 1)])
