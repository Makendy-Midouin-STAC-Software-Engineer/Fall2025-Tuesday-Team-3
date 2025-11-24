"""
Comprehensive tests for inspections/management/commands/import_nyc_inspections.py
to improve coverage from 0% to 85%+.

Note: We only mock the external API call (requests.get) since we can't call the real NYC API in tests.
All database operations use real Django models.
"""
import datetime as dt
from unittest.mock import patch, Mock

from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError

from inspections.models import Restaurant, Inspection


class ImportNYCInspectionsCommandTests(TestCase):
    """Test the import_nyc_inspections management command."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_response_data = [
            {
                "camis": "123456789",
                "dba": "Test Restaurant",
                "boro": "Manhattan",
                "building": "123",
                "street": "Main St",
                "zipcode": "10001",
                "cuisine_description": "Italian",
                "grade": "A",
                "score": "10",
                "violation_description": "No violations",
                "inspection_date": "2024-05-15T00:00:00.000",
                "violation_code": "10A",
                "action": "No action required",
                "critical_flag": "N",
            },
            {
                "camis": "987654321",
                "dba": "Another Restaurant",
                "boro": "Brooklyn",
                "building": "456",
                "street": "Oak Ave",
                "zipcode": "11201",
                "cuisine_description": "American",
                "grade": "B",
                "score": "15",
                "violation_description": "Minor violations",
                "inspection_date": "2024-06-20T00:00:00.000",
                "violation_code": "10B",
                "action": "Violations were cited",
                "critical_flag": "Y",
            },
        ]

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    @patch("inspections.management.commands.import_nyc_inspections.grade_restaurants")
    def test_import_valid_data(self, mock_grade, mock_get):
        """Test importing valid inspection data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_response_data
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=2)

        # Verify restaurants were created
        self.assertEqual(Restaurant.objects.count(), 2)
        restaurant1 = Restaurant.objects.get(camis="123456789")
        self.assertEqual(restaurant1.name, "Test Restaurant")
        self.assertEqual(restaurant1.borough, "Manhattan")
        self.assertEqual(restaurant1.address, "123 Main St")

        # Verify inspections were created
        self.assertEqual(Inspection.objects.count(), 2)
        inspection1 = Inspection.objects.get(restaurant=restaurant1)
        self.assertEqual(inspection1.grade, "A")
        self.assertEqual(inspection1.score, 10)
        self.assertEqual(inspection1.date, dt.date(2024, 5, 15))

        # Verify grading was called
        mock_grade.assert_called_once()

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    def test_import_stops_on_empty_rows(self, mock_get):
        """Test that import stops when no rows are returned."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []  # Empty response
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=100)

        # Should have made one API call and stopped
        self.assertEqual(mock_get.call_count, 1)
        self.assertEqual(Restaurant.objects.count(), 0)

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    def test_import_handles_non_200_response(self, mock_get):
        """Test that non-200 responses raise CommandError."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_get.return_value = mock_response

        with self.assertRaises(CommandError) as cm:
            call_command("import_nyc_inspections", limit=10)
        self.assertIn("NYC API error 500", str(cm.exception))

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    @patch("inspections.management.commands.import_nyc_inspections.grade_restaurants")
    def test_import_parses_fields_correctly(self, mock_grade, mock_get):
        """Test that all fields are parsed correctly from API response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [self.mock_response_data[0]]
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=1)

        restaurant = Restaurant.objects.get(camis="123456789")
        self.assertEqual(restaurant.name, "Test Restaurant")
        self.assertEqual(restaurant.borough, "Manhattan")
        self.assertEqual(restaurant.city, "Manhattan")  # boro maps to city
        self.assertEqual(restaurant.state, "NY")
        self.assertEqual(restaurant.zipcode, "10001")
        self.assertEqual(restaurant.cuisine_description, "Italian")
        self.assertEqual(restaurant.address, "123 Main St")

        inspection = Inspection.objects.get(restaurant=restaurant)
        self.assertEqual(inspection.grade, "A")
        self.assertEqual(inspection.score, 10)
        self.assertEqual(inspection.summary, "No violations")
        self.assertEqual(inspection.violation_code, "10A")
        self.assertEqual(inspection.action, "No action required")
        self.assertEqual(inspection.critical_flag, "N")

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    @patch("inspections.management.commands.import_nyc_inspections.grade_restaurants")
    def test_import_uses_token_when_provided(self, mock_grade, mock_get):
        """Test that token is included in headers when provided."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=1, token="test-token-123")

        # Verify token was included in headers
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("headers", call_args.kwargs)
        self.assertEqual(call_args.kwargs["headers"]["X-App-Token"], "test-token-123")

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    @patch("inspections.management.commands.import_nyc_inspections.grade_restaurants")
    @patch.dict("os.environ", {"SODA_APP_TOKEN": "env-token-456"})
    def test_import_uses_env_token_when_no_arg(self, mock_grade, mock_get):
        """Test that environment variable token is used when no arg provided."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=1)

        # Verify env token was used
        call_args = mock_get.call_args
        self.assertEqual(call_args.kwargs["headers"]["X-App-Token"], "env-token-456")

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    @patch("inspections.management.commands.import_nyc_inspections.grade_restaurants")
    def test_import_respects_limit(self, mock_grade, mock_get):
        """Test that limit parameter is respected."""
        # Create response with more data than limit
        large_response = self.mock_response_data * 3  # 6 items
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = large_response
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=3)

        # Should only import up to limit
        self.assertLessEqual(Restaurant.objects.count(), 3)

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    @patch("inspections.management.commands.import_nyc_inspections.grade_restaurants")
    def test_import_handles_since_parameter(self, mock_grade, mock_get):
        """Test that since parameter filters by date."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=1, since="2024-01-01")

        # Verify $where parameter was set
        call_args = mock_get.call_args
        self.assertIn("params", call_args.kwargs)
        params = call_args.kwargs["params"]
        self.assertIn("$where", params)
        self.assertIn("2024-01-01", params["$where"])

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    @patch("inspections.management.commands.import_nyc_inspections.grade_restaurants")
    def test_import_handles_invalid_dates(self, mock_grade, mock_get):
        """Test that invalid dates are handled gracefully."""
        invalid_data = [
            {
                "camis": "123456789",
                "dba": "Test Restaurant",
                "boro": "Manhattan",
                "inspection_date": "invalid-date",
                "grade": "A",
            }
        ]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = invalid_data
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=1)

        # Should skip invalid dates (year not in ALLOWED_YEARS)
        self.assertEqual(Inspection.objects.count(), 0)

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    @patch("inspections.management.commands.import_nyc_inspections.grade_restaurants")
    def test_import_handles_invalid_scores(self, mock_grade, mock_get):
        """Test that invalid scores are handled gracefully."""
        invalid_data = [
            {
                "camis": "123456789",
                "dba": "Test Restaurant",
                "boro": "Manhattan",
                "inspection_date": "2024-05-15T00:00:00.000",
                "score": "not-a-number",
                "grade": "A",
            }
        ]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = invalid_data
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=1)

        # Should create inspection with None score
        inspection = Inspection.objects.first()
        self.assertIsNone(inspection.score)

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    @patch("inspections.management.commands.import_nyc_inspections.grade_restaurants")
    def test_import_handles_missing_camis(self, mock_grade, mock_get):
        """Test that restaurants without CAMIS are created using name/address."""
        data_no_camis = [
            {
                "dba": "No CAMIS Restaurant",
                "boro": "Queens",
                "building": "789",
                "street": "Pine Rd",
                "zipcode": "11101",
                "cuisine_description": "Japanese",
                "inspection_date": "2024-05-15T00:00:00.000",
                "grade": "A",
            }
        ]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = data_no_camis
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=1)

        # Should create restaurant using name/address/zipcode as key
        self.assertEqual(Restaurant.objects.count(), 1)
        restaurant = Restaurant.objects.first()
        self.assertEqual(restaurant.name, "No CAMIS Restaurant")
        self.assertEqual(restaurant.camis, "")  # Empty CAMIS

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    @patch("inspections.management.commands.import_nyc_inspections.grade_restaurants")
    def test_import_updates_existing_restaurant(self, mock_grade, mock_get):
        """Test that existing restaurants are updated with new data."""
        # Create existing restaurant
        existing = Restaurant.objects.create(
            camis="123456789",
            name="Old Name",
            address="Old Address",
            borough="Old Borough",
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [self.mock_response_data[0]]
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=1)

        # Should update existing restaurant
        existing.refresh_from_db()
        self.assertEqual(existing.name, "Test Restaurant")
        self.assertEqual(existing.address, "123 Main St")
        self.assertEqual(existing.borough, "Manhattan")
        # Should still be same restaurant
        self.assertEqual(Restaurant.objects.count(), 1)

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    @patch("inspections.management.commands.import_nyc_inspections.grade_restaurants")
    def test_import_filters_by_allowed_years(self, mock_grade, mock_get):
        """Test that inspections outside allowed years are skipped."""
        data_old_date = [
            {
                "camis": "123456789",
                "dba": "Test Restaurant",
                "boro": "Manhattan",
                "inspection_date": "2020-05-15T00:00:00.000",  # Before 2021
                "grade": "A",
            }
        ]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = data_old_date
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=1)

        # Should skip inspections outside allowed years
        self.assertEqual(Inspection.objects.count(), 0)

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    @patch("inspections.management.commands.import_nyc_inspections.grade_restaurants")
    def test_import_pagination(self, mock_grade, mock_get):
        """Test that pagination works correctly."""
        # First page
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = self.mock_response_data
        # Second page (empty)
        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = []

        mock_get.side_effect = [mock_response1, mock_response2]

        call_command("import_nyc_inspections", limit=10)

        # Should have made 2 API calls
        self.assertEqual(mock_get.call_count, 2)
        # Should have imported from first page
        self.assertEqual(Restaurant.objects.count(), 2)

    @patch("inspections.management.commands.import_nyc_inspections.requests.get")
    @patch("inspections.management.commands.import_nyc_inspections.grade_restaurants")
    def test_import_handles_empty_fields(self, mock_grade, mock_get):
        """Test that empty/null fields are handled correctly."""
        data_empty_fields = [
            {
                "camis": "",
                "dba": "Test",
                "boro": "",
                "building": "",
                "street": "",
                "zipcode": "",
                "cuisine_description": "",
                "inspection_date": "2024-05-15T00:00:00.000",
                "grade": "",
                "score": "",
            }
        ]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = data_empty_fields
        mock_get.return_value = mock_response

        call_command("import_nyc_inspections", limit=1)

        # Should still create restaurant and inspection with empty fields
        self.assertEqual(Restaurant.objects.count(), 1)
        restaurant = Restaurant.objects.first()
        self.assertEqual(restaurant.camis, "")
        self.assertEqual(restaurant.borough, "")

