"""Tests for serializers in the inspections app."""

from django.test import TestCase
from datetime import date

from inspections.models import Restaurant, Inspection
from inspections.serializers import (
    RestaurantSearchSerializer,
    RestaurantDetailSerializer,
    InspectionSummarySerializer,
    InspectionDetailSerializer,
)


class InspectionSummarySerializerTest(TestCase):
    """Test InspectionSummarySerializer."""

    def test_serialize_inspection_data(self):
        """Test serializing inspection summary data."""
        data = {
            "date": date(2024, 1, 15),
            "grade": "A",
            "score": 12,
            "summary": "Clean",
            "violation_code": "10F",
            "action": "No action needed",
            "critical_flag": ""
        }
        serializer = InspectionSummarySerializer(data=data)
        self.assertTrue(serializer.is_valid())


class InspectionDetailSerializerTest(TestCase):
    """Test InspectionDetailSerializer."""

    def setUp(self):
        """Set up test data."""
        self.restaurant = Restaurant.objects.create(name="Test Restaurant")
        self.inspection = Inspection.objects.create(
            restaurant=self.restaurant,
            date=date(2024, 3, 1),
            grade="B",
            score=15,
            summary="Minor issues",
            violation_code="10F",
            action="Violations cited",
            critical_flag="Critical"
        )

    def test_serialize_inspection_instance(self):
        """Test serializing an inspection instance."""
        serializer = InspectionDetailSerializer(self.inspection)
        data = serializer.data
        
        self.assertEqual(data["grade"], "B")
        self.assertEqual(data["score"], 15)
        self.assertEqual(data["violation_code"], "10F")
        self.assertEqual(data["action"], "Violations cited")


class RestaurantSearchSerializerTest(TestCase):
    """Test RestaurantSearchSerializer."""

    def setUp(self):
        """Set up test data."""
        self.restaurant = Restaurant.objects.create(
            camis="123",
            name="Test Restaurant",
            address="123 Test St",
            city="New York",
            state="NY",
            zipcode="10001",
            borough="Manhattan",
            cuisine_description="American",
            phone="212-555-0100"
        )

        Inspection.objects.create(
            restaurant=self.restaurant,
            date=date(2024, 1, 1),
            grade="A",
            score=10
        )

    def test_serialize_restaurant_with_latest_inspection(self):
        """Test serializing restaurant with latest inspection."""
        # Annotate restaurant with latest inspection data
        from django.db.models import OuterRef, Subquery

        latest_qs = Inspection.objects.filter(
            restaurant=OuterRef("pk")
        ).order_by("-date").values(
            "date", "grade", "score", "summary",
            "violation_code", "action", "critical_flag"
        )[:1]
        
        restaurant = Restaurant.objects.annotate(
            latest_date=Subquery(latest_qs.values("date")),
            latest_grade=Subquery(latest_qs.values("grade")),
            latest_score=Subquery(latest_qs.values("score")),
            latest_summary=Subquery(latest_qs.values("summary")),
            latest_violation_code=Subquery(latest_qs.values("violation_code")),
            latest_action=Subquery(latest_qs.values("action")),
            latest_critical_flag=Subquery(latest_qs.values("critical_flag")),
        ).first()

        serializer = RestaurantSearchSerializer(restaurant)
        data = serializer.data

        self.assertEqual(data["name"], "Test Restaurant")
        self.assertEqual(data["borough"], "Manhattan")
        self.assertIn("latest_inspection", data)


class RestaurantDetailSerializerTest(TestCase):
    """Test RestaurantDetailSerializer."""

    def setUp(self):
        """Set up test data."""
        self.restaurant = Restaurant.objects.create(
            name="Detailed Restaurant",
            borough="Brooklyn",
            cuisine_description="Italian"
        )

        Inspection.objects.create(
            restaurant=self.restaurant,
            date=date(2024, 1, 1),
            grade="A"
        )
        
        Inspection.objects.create(
            restaurant=self.restaurant,
            date=date(2024, 2, 1),
            grade="B"
        )

    def test_serialize_restaurant_with_inspections(self):
        """Test serializing restaurant with inspection history."""
        # Fetch with prefetch_related
        from django.db import models
        from inspections.views import RestaurantDetailView

        queryset = Restaurant.objects.prefetch_related(
            models.Prefetch(
                "inspections",
                queryset=Inspection.objects.exclude(date__year=1900).order_by("-date")
            )
        )
        
        restaurant = queryset.first()
        serializer = RestaurantDetailSerializer(restaurant)
        data = serializer.data
        
        self.assertEqual(data["name"], "Detailed Restaurant")
        self.assertIn("inspections", data)
        self.assertEqual(len(data["inspections"]), 2)

