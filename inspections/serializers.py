from rest_framework import serializers
from .models import Restaurant, Inspection


class InspectionSummarySerializer(serializers.Serializer):
    date = serializers.DateField(allow_null=True)
    grade = serializers.CharField(allow_blank=True)
    score = serializers.IntegerField(allow_null=True)
    summary = serializers.CharField(allow_blank=True)
    violation_code = serializers.CharField(allow_blank=True)
    action = serializers.CharField(allow_blank=True)
    critical_flag = serializers.CharField(allow_blank=True)


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
            "borough",
            "cuisine_description",
            "phone",
            "regraded_letter",
            "star_rating",
            "forbidden_years",
            "grading_explanations",
            "latest_inspection",
        ]


class InspectionDetailSerializer(serializers.ModelSerializer):
    """Full inspection details for restaurant detail view"""

    class Meta:
        model = Inspection
        fields = [
            "id",
            "date",
            "grade",
            "score",
            "summary",
            "violation_code",
            "action",
            "critical_flag",
        ]


class RestaurantDetailSerializer(serializers.ModelSerializer):
    """Restaurant with all inspection history"""

    inspections = InspectionDetailSerializer(many=True, read_only=True)
    latest_agency_grade = serializers.SerializerMethodField()

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
            "borough",
            "cuisine_description",
            "phone",
            "regraded_letter",
            "star_rating",
            "forbidden_years",
            "grading_explanations",
            "latest_agency_grade",
            "inspections",
        ]

    def get_latest_agency_grade(self, obj: Restaurant) -> str:
        inspection = obj.inspections.first()
        return inspection.grade if inspection else ""
