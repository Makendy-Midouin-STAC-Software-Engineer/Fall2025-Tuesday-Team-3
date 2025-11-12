import datetime as dt

from django.core.management.base import BaseCommand, CommandError
from django.db import models

from inspections.models import Restaurant, Inspection
from inspections.services.grading import GradingService, grade_restaurants, ALLOWED_YEARS


class Command(BaseCommand):
    help = "Recompute deterministic grade overrides and star ratings for restaurants."

    def add_arguments(self, parser):
        parser.add_argument(
            "--camis",
            nargs="+",
            help="Restrict recomputation to specific CAMIS identifiers.",
        )
        parser.add_argument(
            "--ids",
            nargs="+",
            type=int,
            help="Restrict recomputation to specific Restaurant primary keys.",
        )
        parser.add_argument(
            "--since",
            type=str,
            help="Only recompute restaurants with inspections on or after YYYY-MM-DD.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=200,
            help="Number of restaurants to process per batch.",
        )

    def handle(self, *args, **options):
        camis = options.get("camis")
        ids = options.get("ids")
        since = options.get("since")
        batch_size = options.get("batch_size") or 200

        queryset = Restaurant.objects.all()

        if camis:
            queryset = queryset.filter(camis__in=camis)
        if ids:
            queryset = queryset.filter(id__in=ids)

        if since:
            try:
                since_date = dt.datetime.strptime(since, "%Y-%m-%d").date()
            except ValueError as exc:
                raise CommandError(f"Invalid --since date '{since}': {exc}") from exc
            queryset = queryset.filter(inspections__date__gte=since_date)

        queryset = queryset.distinct().order_by("id")

        total = queryset.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("No restaurants matched the selection criteria."))
            return

        self.stdout.write(self.style.NOTICE(f"Recomputing grades for {total} restaurant(s)..."))

        inspection_prefetch = models.Prefetch(
            "inspections",
            queryset=Inspection.objects.filter(date__year__in=ALLOWED_YEARS).order_by("-date"),
        )
        service = GradingService()

        processed = 0
        while processed < total:
            batch = list(
                queryset[processed : processed + batch_size].prefetch_related(inspection_prefetch)
            )
            grade_restaurants(batch, service=service)
            processed += len(batch)
            self.stdout.write(
                self.style.SUCCESS(f"Processed {processed}/{total} restaurants for recomputation.")
            )

        self.stdout.write(self.style.SUCCESS("Grade recomputation completed."))

