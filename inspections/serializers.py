from rest_framework import serializers
from .models import Restaurant


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