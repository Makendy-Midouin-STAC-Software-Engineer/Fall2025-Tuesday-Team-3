# Create your views here.
from django.db.models import OuterRef, Subquery
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound

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


class RestaurantDetailView(RetrieveAPIView):
    """
    GET /api/restaurants/{id}/
    Returns detailed information about a specific restaurant including all inspections.
    """
    serializer_class = RestaurantSearchSerializer

    def get_queryset(self):
        return Restaurant.objects.all()

    def retrieve(self, request, *args, **kwargs):
        try:
            restaurant = self.get_object()
            
            # Get all inspections for this restaurant, ordered by date (most recent first)
            inspections = Inspection.objects.filter(restaurant=restaurant).order_by('-date')
            
            # Prepare inspection data
            inspections_data = []
            for inspection in inspections:
                inspections_data.append({
                    'id': inspection.id,
                    'date': inspection.date,
                    'grade': inspection.grade,
                    'score': inspection.score,
                    'summary': inspection.summary,
                })
            
            # Prepare restaurant data
            data = {
                'id': restaurant.id,
                'camis': restaurant.camis,
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