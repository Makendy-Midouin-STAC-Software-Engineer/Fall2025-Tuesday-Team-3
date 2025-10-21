# Create your views here.
from django.db.models import OuterRef, Subquery
from django.db import models
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

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
        borough = (self.request.query_params.get("borough") or "").strip()
        cuisine = (self.request.query_params.get("cuisine") or "").strip()
        
        # Allow wildcard search for filter-only searches
        if q == "*":
            q = ""
        
        if not q and not borough and not cuisine:
            raise ValidationError({"detail": "At least one search parameter (q, borough, or cuisine) is required"})

        # Subquery for the most recent inspection (not just graded)
        # Filter out placeholder dates (1900-01-01)
        latest_qs = (
            Inspection.objects
            .filter(restaurant=OuterRef("pk"))
            .exclude(date__year=1900)  # Filter out placeholder dates
            .order_by("-date")
            .values("date", "grade", "score", "summary", "violation_code")[:1]
        )

        # Build base queryset
        if q:
            queryset = Restaurant.objects.filter(name__icontains=q)
        else:
            queryset = Restaurant.objects.all()
        
        # Add borough filter if provided
        if borough:
            queryset = queryset.filter(borough__iexact=borough)
            
        # Add cuisine filter if provided
        if cuisine:
            queryset = queryset.filter(cuisine_description__icontains=cuisine)

        # Annotate fields directly so the serializer can read them
        return (
            queryset
            .annotate(
                latest_date=Subquery(latest_qs.values("date")),
                latest_grade=Subquery(latest_qs.values("grade")),
                latest_score=Subquery(latest_qs.values("score")),
                latest_summary=Subquery(latest_qs.values("summary")),
                latest_violation_code=Subquery(latest_qs.values("violation_code")),
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
                    "borough": r.borough,
                    "cuisine_description": r.cuisine_description,
                    "latest_inspection": {
                        "date": getattr(r, "latest_date", None),
                        "grade": getattr(r, "latest_grade", "") or "",
                        "score": getattr(r, "latest_score", None),
                        "summary": getattr(r, "latest_summary", "") or "",
                        "violation_code": getattr(r, "latest_violation_code", "") or "",
                    },
                })
            return data

        if page is not None:
            return self.get_paginated_response(serialize(page))
        return Response(serialize(queryset))


class RestaurantDetailView(RetrieveAPIView):
    """
    GET /api/restaurants/<id>/
    Returns full restaurant details including all inspection history.
    """
    queryset = Restaurant.objects.prefetch_related(
        models.Prefetch(
            'inspections',
            queryset=Inspection.objects.exclude(date__year=1900).order_by('-date')
        )
    )
    serializer_class = RestaurantDetailSerializer


class BoroughListView(ListAPIView):
    """
    GET /api/restaurants/boroughs/
    Returns list of unique boroughs for filter dropdown.
    """
    def get(self, request, *args, **kwargs):
        boroughs = Restaurant.objects.exclude(borough="").values_list('borough', flat=True).distinct().order_by('borough')
        return Response(list(boroughs))
