# Create your views here.
from django.conf import settings
from django.db.models import OuterRef, Subquery
from django.db import models
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Restaurant, Inspection
from .serializers import RestaurantSearchSerializer, RestaurantDetailSerializer
from inspections.services.grading import ALLOWED_YEARS


class RestaurantSearchView(ListAPIView):
    """
    GET /api/restaurants/search/?q=<term>
    Returns restaurants whose name matches <term> (case-insensitive),
    each annotated with its latest inspection summary.
    """

    serializer_class = RestaurantSearchSerializer

    def _resolve_display_mode(self) -> str:
        requested = (self.request.query_params.get("display") or "").strip().lower()
        if getattr(settings, "STAR_DISPLAY_ENABLED", False) and requested == "stars":
            return "stars"
        return "letter"

    def get_queryset(self):
        q = (self.request.query_params.get("q") or "").strip()
        borough = (self.request.query_params.get("borough") or "").strip()
        cuisine = (self.request.query_params.get("cuisine") or "").strip()

        # Allow wildcard search for filter-only searches
        if q == "*":
            q = ""

        if not q and not borough and not cuisine:
            raise ValidationError(
                {"detail": "At least one search parameter (q, borough, or cuisine) is required"}
            )

        # Subquery for the most recent inspection (not just graded)
        # Filter out placeholder dates (1900-01-01)
        latest_qs = (
            Inspection.objects.filter(restaurant=OuterRef("pk"))
            .exclude(date__year=1900)  # Filter out placeholder dates
            .order_by("-date")
            .values(
                "date", "grade", "score", "summary", "violation_code", "action", "critical_flag"
            )[:1]
        )

        # Build base queryset
        if q:
            queryset = Restaurant.objects.filter(name__icontains=q)
        else:
            queryset = Restaurant.objects.all()

        # Add borough filter if provided
        if borough:
            # Search for borough in the address field (e.g., "Bronx" in "123 Main St, Bronx, NY")
            queryset = queryset.filter(address__icontains=borough)

        # Add cuisine filter if provided
        if cuisine:
            queryset = queryset.filter(cuisine_description__icontains=cuisine)

        # Annotate fields directly so the serializer can read them
        return queryset.annotate(
            latest_date=Subquery(latest_qs.values("date")),
            latest_grade=Subquery(latest_qs.values("grade")),
            latest_score=Subquery(latest_qs.values("score")),
            latest_summary=Subquery(latest_qs.values("summary")),
            latest_violation_code=Subquery(latest_qs.values("violation_code")),
            latest_action=Subquery(latest_qs.values("action")),
            latest_critical_flag=Subquery(latest_qs.values("critical_flag")),
        ).order_by("name")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        display_mode = self._resolve_display_mode()
        base_year_map = {str(year): None for year in ALLOWED_YEARS}

        def serialize(qs, mode):
            data = []
            for r in qs:
                regraded_letter = (r.regraded_letter or "").strip() or "Unknown"
                star_rating = r.star_rating if r.star_rating is not None else 2
                year_map = base_year_map.copy()
                if isinstance(r.forbidden_years, dict):
                    year_map.update(r.forbidden_years)
                display_value = star_rating if mode == "stars" else regraded_letter
                display_source = "star_rating" if mode == "stars" else "regraded_letter"
                data.append(
                    {
                        "id": r.id,
                        "name": r.name,
                        "address": r.address,
                        "city": r.city,
                        "state": r.state,
                        "zipcode": r.zipcode,
                        "borough": r.borough,
                        "cuisine_description": r.cuisine_description,
                        "phone": r.phone,
                        "regraded_letter": regraded_letter,
                        "star_rating": star_rating,
                        "forbidden_years": year_map,
                        "grading_explanations": getattr(r, "grading_explanations", {}) or {},
                        "display_mode": mode,
                        "display_source": display_source,
                        "display_value": display_value,
                        "original_agency_grade": getattr(r, "latest_grade", "") or "",
                        "latest_inspection": {
                            "date": getattr(r, "latest_date", None),
                            "grade": getattr(r, "latest_grade", "") or "",
                            "score": getattr(r, "latest_score", None),
                            "summary": getattr(r, "latest_summary", "") or "",
                            "violation_code": getattr(r, "latest_violation_code", "") or "",
                            "action": getattr(r, "latest_action", "") or "",
                            "critical_flag": getattr(r, "latest_critical_flag", "") or "",
                        },
                    }
                )
            return data

        if page is not None:
            return self.get_paginated_response(serialize(page, display_mode))
        return Response(serialize(queryset, display_mode))


class RestaurantDetailView(RetrieveAPIView):
    """
    GET /api/restaurants/<id>/
    Returns full restaurant details including all inspection history.
    """

    queryset = Restaurant.objects.prefetch_related(
        models.Prefetch(
            "inspections", queryset=Inspection.objects.exclude(date__year=1900).order_by("-date")
        )
    )
    serializer_class = RestaurantDetailSerializer

    def _resolve_display_mode(self) -> str:
        requested = (self.request.query_params.get("display") or "").strip().lower()
        if getattr(settings, "STAR_DISPLAY_ENABLED", False) and requested == "stars":
            return "stars"
        return "letter"

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        data = response.data
        display_mode = self._resolve_display_mode()
        regraded_letter = (data.get("regraded_letter") or "").strip() or "Unknown"
        star_rating = data.get("star_rating", None)
        if star_rating is None:
            star_rating = 2
        display_value = star_rating if display_mode == "stars" else regraded_letter
        data["display_mode"] = display_mode
        data["display_source"] = "star_rating" if display_mode == "stars" else "regraded_letter"
        data["display_value"] = display_value
        data.setdefault("original_agency_grade", data.get("latest_agency_grade", ""))
        response.data = data
        return response


class BoroughListView(ListAPIView):
    """
    GET /api/restaurants/boroughs/
    Returns list of unique boroughs for filter dropdown.
    """

    def get(self, request, *args, **kwargs):
        boroughs = (
            Restaurant.objects.exclude(borough="")
            .values_list("borough", flat=True)
            .distinct()
            .order_by("borough")
        )
        return Response(list(boroughs))
