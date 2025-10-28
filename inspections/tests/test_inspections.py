"""
Comprehensive tests for inspections app to achieve 85%+ coverage.
"""

from unittest.mock import patch, Mock
from django.test import TestCase, Client
from django.urls import reverse
from django.core.management import call_command
from django.core.management.base import CommandError
from rest_framework import status
from datetime import date, datetime as dt

from inspections.models import Restaurant, Inspection


class RestaurantSearchViewTests(TestCase):
    """Test restaurant search endpoint coverage."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        self.restaurant1 = Restaurant.objects.create(
            camis="12345",
            name="Joe's Pizza",
            address="123 Main St, Bronx",
            city="Bronx",
            state="NY",
            zipcode="10451",
            borough="Bronx",
            cuisine_description="Pizza",
            phone="718-555-0100",
        )

        self.restaurant2 = Restaurant.objects.create(
            camis="67890",
            name="Burger Palace",
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
            summary="Clean",
            violation_code="10F",
            action="No action",
            critical_flag="",
        )

        Inspection.objects.create(
            restaurant=self.restaurant2,
            date=date(2024, 2, 20),
            grade="B",
            score=15,
            summary="Minor issues",
            violation_code="",
            action="Actions required",
            critical_flag="Critical",
        )

    def test_search_by_name(self):
        """Test searching by restaurant name."""
        response = self.client.get("/api/restaurants/search/", {"q": "Pizza"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], "Joe's Pizza")

    def test_search_by_borough(self):
        """Test searching by borough only."""
        response = self.client.get("/api/restaurants/search/", {"borough": "Bronx"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["borough"], "Bronx")

    def test_search_by_cuisine(self):
        """Test searching by cuisine only."""
        response = self.client.get("/api/restaurants/search/", {"cuisine": "American"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertIn("American", data[0]["cuisine_description"])

    def test_search_all_parameters(self):
        """Test searching with all parameters."""
        response = self.client.get(
            "/api/restaurants/search/", {"q": "Pizza", "borough": "Bronx", "cuisine": "Pizza"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_search_no_parameters_raises_error(self):
        """Test that search without any parameters raises ValidationError."""
        response = self.client.get("/api/restaurants/search/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.json())

    def test_search_wildcard(self):
        """Test wildcard search with *."""
        response = self.client.get("/api/restaurants/search/", {"q": "*", "borough": "Bronx"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        response = self.client.get("/api/restaurants/search/", {"q": "joe's"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_search_with_latest_inspection_data(self):
        """Test that latest inspection data is included."""
        response = self.client.get("/api/restaurants/search/", {"q": "Pizza"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()[0]
        self.assertIn("latest_inspection", data)
        self.assertEqual(data["latest_inspection"]["grade"], "A")


class RestaurantDetailViewTests(TestCase):
    """Test restaurant detail endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

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

        Inspection.objects.create(
            restaurant=self.restaurant,
            date=date(2024, 1, 1),
            grade="A",
            score=10,
            summary="Good",
            violation_code="",
            action="",
            critical_flag="",
        )

        Inspection.objects.create(
            restaurant=self.restaurant,
            date=date(2024, 3, 1),
            grade="B",
            score=14,
            summary="Fair",
            violation_code="10F",
            action="Actions required",
            critical_flag="Critical",
        )

    def test_get_restaurant_detail(self):
        """Test retrieving restaurant details with inspection history."""
        response = self.client.get(f"/api/restaurants/{self.restaurant.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["name"], "Test Restaurant")
        self.assertIn("inspections", data)
        self.assertEqual(len(data["inspections"]), 2)

    def test_get_nonexistent_restaurant_404(self):
        """Test getting non-existent restaurant returns 404."""
        response = self.client.get("/api/restaurants/99999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BoroughListViewTests(TestCase):
    """Test borough list endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        Restaurant.objects.create(name="Restaurant 1", borough="Manhattan")
        Restaurant.objects.create(name="Restaurant 2", borough="Brooklyn")
        Restaurant.objects.create(name="Restaurant 3", borough="Queens")
        Restaurant.objects.create(name="Restaurant 4", borough="Manhattan")
        Restaurant.objects.create(name="Restaurant 5", borough="")

    def test_get_boroughs_list(self):
        """Test retrieving list of unique boroughs."""
        response = self.client.get("/api/restaurants/boroughs/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("Brooklyn", data)
        self.assertIn("Manhattan", data)
        self.assertIn("Queens", data)
        self.assertNotIn("", data)
        self.assertEqual(len(data), 3)


class ImportNYCInspectionsCommandTests(TestCase):
    """Test the import_nyc_inspections management command."""

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    def test_import_valid_data(self, mock_get):
        """Test importing valid JSON data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "camis": "50012345",
                "dba": "Test Restaurant",
                "boro": "Manhattan",
                "building": "123",
                "street": "Main Street",
                "zipcode": "10001",
                "cuisine_description": "Italian",
                "inspection_date": "2024-01-15T00:00:00.000",
                "grade": "A",
                "score": "12",
                "violation_description": "Clean",
            },
            {
                "camis": "50012345",
                "dba": "Test Restaurant",
                "boro": "Manhattan",
                "building": "123",
                "street": "Main Street",
                "zipcode": "10001",
                "cuisine_description": "Italian",
                "inspection_date": "2024-02-20T00:00:00.000",
                "grade": "B",
                "score": "18",
                "violation_description": "Minor issues",
            },
        ]
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=5)

        self.assertEqual(Restaurant.objects.count(), 1)
        self.assertEqual(Inspection.objects.count(), 2)

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    def test_import_stops_on_empty_rows(self, mock_get):
        """Test that import stops when no rows are returned."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        initial_count = Inspection.objects.count()
        call_command("import_nyc_inspections", limit=10)

        self.assertEqual(Inspection.objects.count(), initial_count)

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    def test_import_raises_error_on_non_200(self, mock_get):
        """Test that CommandError is raised for non-200 responses."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        with self.assertRaises(CommandError):
            call_command("import_nyc_inspections", limit=5)

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    def test_import_parses_fields(self, mock_get):
        """Test that various fields are parsed correctly."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "camis": "60012345",
                "dba": "Quality Restaurant",
                "boro": "Brooklyn",
                "building": "456",
                "street": "Park Avenue",
                "zipcode": "11201",
                "cuisine_description": "American",
                "inspection_date": "2024-03-10T00:00:00.000",
                "grade": "A",
                "score": "10",
                "violation_description": "Excellent",
            }
        ]
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=5)

        restaurant = Restaurant.objects.first()
        self.assertEqual(restaurant.name, "Quality Restaurant")
        self.assertEqual(restaurant.camis, "60012345")
        self.assertEqual(restaurant.borough, "Brooklyn")
        self.assertEqual(restaurant.cuisine_description, "American")

        inspection = Inspection.objects.first()
        self.assertEqual(inspection.date, date(2024, 3, 10))
        self.assertEqual(inspection.grade, "A")
        self.assertEqual(inspection.score, 10)
        self.assertEqual(inspection.summary, "Excellent")

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    def test_import_with_token(self, mock_get):
        """Test import with app token."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=5, token="test-token")

        mock_get.assert_called()
        call_args = mock_get.call_args
        self.assertIn("X-App-Token", call_args.kwargs["headers"])

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    def test_import_with_since_parameter(self, mock_get):
        """Test import with since parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=5, since="2024-01-01")

        mock_get.assert_called()
        call_args = mock_get.call_args
        self.assertIn("$where", call_args.kwargs["params"])

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    def test_import_handles_invalid_date(self, mock_get):
        """Test that invalid dates are handled gracefully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "camis": "70012345",
                "dba": "Test Restaurant",
                "inspection_date": "invalid-date",
                "score": "15",
            }
        ]
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=5)

        inspection = Inspection.objects.first()
        self.assertEqual(inspection.date, date(1900, 1, 1))

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    def test_import_handles_invalid_score(self, mock_get):
        """Test that invalid scores are handled gracefully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "camis": "80012345",
                "dba": "Test Restaurant",
                "inspection_date": "2024-01-01T00:00:00.000",
                "score": "not-a-number",
            }
        ]
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=5)

        inspection = Inspection.objects.first()
        self.assertIsNone(inspection.score)
