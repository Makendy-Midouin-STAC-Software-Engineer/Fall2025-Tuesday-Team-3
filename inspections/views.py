# Create your views here.
from django.db.models import OuterRef, Subquery
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound

from .models import Restaurant, Inspection
from .serializers import RestaurantSearchSerializer, RestaurantDetailSerializer


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

        latest_qs = (
            Inspection.objects
            .filter(restaurant=OuterRef("pk"))
            .exclude(grade="")
            .order_by("-date")
            .values("date", "grade", "score", "summary")[:1]
        )

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


class RestaurantDetailView(RetrieveAPIView):
    """
    GET /api/restaurants/{id}/
    Returns detailed information about a specific restaurant including all inspections.
    """
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            restaurant = self.get_object()

            inspections = Inspection.objects.filter(restaurant=restaurant).order_by('-date')
            inspections_data = [
                {
                    'id': i.id,
                    'date': i.date,
                    'grade': i.grade,
                    'score': i.score,
                    'summary': i.summary,
                }
                for i in inspections
            ]

            data = {
                'id': restaurant.id,
                'camis': getattr(restaurant, 'camis', None),
                'name': restaurant.name,
                'address': restaurant.address,
                'city': restaurant.city,
                'state': restaurant.state,
                'zipcode': restaurant.zipcode,
                'full_address': f"{restaurant.address}, {restaurant.city}, {restaurant.state} {restaurant.zipcode}".strip(', '),
                'inspections': inspections_data,
                'total_inspections': len(inspections_data),
                'latest_inspection': inspections_data[0] if inspections_data else None,
            }

            return Response(data)

        except Restaurant.DoesNotExist:
            raise NotFound("Restaurant not found")
