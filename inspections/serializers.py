from rest_framework import serializers
from .models import Restaurant, Inspection


class InspectionSummarySerializer(serializers.Serializer):
    date = serializers.DateField(allow_null=True)
    grade = serializers.CharField(allow_blank=True)
    score = serializers.IntegerField(allow_null=True)
    summary = serializers.CharField(allow_blank=True)


class RestaurantSearchSerializer(serializers.ModelSerializer):
    latest_inspection = InspectionSummarySerializer()

    class Meta:
        model = Restaurant
        fields = [
            "id",
            "name",
            "address",
            "city",
            "state",
            "zipcode",
            "latest_inspection",
        ]


class InspectionDetailSerializer(serializers.ModelSerializer):
    """Full inspection details for restaurant detail view"""
    class Meta:
        model = Inspection
        fields = ["id", "date", "grade", "score", "summary"]


class RestaurantDetailSerializer(serializers.ModelSerializer):
    """Restaurant with all inspection history"""
    inspections = InspectionDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            "id",
            "camis",
            "name",
            "address",
            "city",
            "state",
            "zipcode",
            "inspections",
        ]