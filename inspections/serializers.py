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


# ✨ New detail serializer for restaurant details
class InspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspection
        fields = ['date', 'grade', 'score', 'summary']


class RestaurantDetailSerializer(serializers.ModelSerializer):
    inspections = InspectionSerializer(many=True, source='inspection_set')

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'city', 'state', 'zipcode', 'cuisine', 'inspections']
