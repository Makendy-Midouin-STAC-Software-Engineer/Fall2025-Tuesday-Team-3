# Create your views here.
from django.db.models import OuterRef, Subquery
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Restaurant, Inspection
from .serializers import RestaurantSearchSerializer


class RestaurantSearchView(ListAPIView):
    """
    GET /api/restaurants/search/?q=<term>
    Returns restaurants whose name matches <term> (case-insensitive),
    each annotated with its latest inspection summary.
    """
    serializer_class = RestaurantSearchSerializer

    def get_queryset(self):
        q = (self.request.query_params.get("q") or "").strip()
        if not q:
            raise ValidationError({"detail": "q is required"})

        # Subquery for the most recent GRADED inspection for each restaurant
        # If no graded inspection exists, annotations below will be null/empty
        latest_qs = (
            Inspection.objects
            .filter(restaurant=OuterRef("pk"))
            .exclude(grade="")
            .order_by("-date")
            .values("date", "grade", "score", "summary")[:1]
        )

        # Annotate fields directly so the serializer can read them
        return (
            Restaurant.objects.filter(name__icontains=q)
            .annotate(
                latest_date=Subquery(latest_qs.values("date")),
                latest_grade=Subquery(latest_qs.values("grade")),
                latest_score=Subquery(latest_qs.values("score")),
                latest_summary=Subquery(latest_qs.values("summary")),
            )
            .order_by("name")
        )

    def list(self, request, *args, **kwargs):
        # Run parent ListAPIView logic, but map annotations into nested field
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        def serialize(qs):
            data = []
            for r in qs:
                data.append({
                    "id": r.id,
                    "name": r.name,
                    "address": r.address,
                    "city": r.city,
                    "state": r.state,
                    "zipcode": r.zipcode,
                    "latest_inspection": {
                        "date": getattr(r, "latest_date", None),
                        "grade": getattr(r, "latest_grade", "") or "",
                        "score": getattr(r, "latest_score", None),
                        "summary": getattr(r, "latest_summary", "") or "",
                    },
                })
            return data

        if page is not None:
            return self.get_paginated_response(serialize(page))

        return Response(serialize(queryset))