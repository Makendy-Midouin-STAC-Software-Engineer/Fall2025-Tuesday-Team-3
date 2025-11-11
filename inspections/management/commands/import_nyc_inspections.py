import os
import datetime as dt
from typing import Dict, Any

import requests
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from inspections.models import Restaurant, Inspection
from inspections.services.grading import GradingService, grade_restaurants

SODA_URL = "https://data.cityofnewyork.us/resource/43nn-pn8j.json"
PAGE_SIZE = 5000
ALLOWED_START_DATE = dt.date(2021, 1, 1)
ALLOWED_END_DATE = dt.date(2025, 12, 31)
ALLOWED_YEARS = {2021, 2022, 2023, 2024, 2025}


def norm(s: Any) -> str:
    return (s or "").strip()


class Command(BaseCommand):
    help = "Import NYC restaurant inspections into local DB."

    def __init__(self):
        super().__init__()
        self.grading_service = GradingService()

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", type=int, default=None, help="Max rows to import for this run (default: no limit, import all data)."
        )
        parser.add_argument(
            "--since", type=str, help="YYYY-MM-DD to import records with inspection_date >= since."
        )
        parser.add_argument("--token", type=str, help="Socrata app token (optional).")

    def handle(self, *args, **opts):
        total_limit = opts["limit"]
        since = opts.get("since")
        token = opts.get("token") or os.environ.get("SODA_APP_TOKEN")

        headers = {}
        if token:
            headers["X-App-Token"] = token

        params = {"$limit": PAGE_SIZE, "$offset": 0}

        where_clauses = [
            f"inspection_date >= '{ALLOWED_START_DATE.isoformat()}T00:00:00.000'",
            f"inspection_date <= '{ALLOWED_END_DATE.isoformat()}T23:59:59.999'",
        ]
        if since:
            params["$where"] = f"inspection_date >= '{since}T00:00:00.000'"

        imported = 0
        while total_limit is None or imported < total_limit:
            # Cap the final page if limit is set
            if total_limit is not None:
                page_limit = min(PAGE_SIZE, total_limit - imported)
                params["$limit"] = page_limit
            else:
                params["$limit"] = PAGE_SIZE

            r = requests.get(SODA_URL, params=params, headers=headers, timeout=60)
            if r.status_code != 200:
                raise CommandError(f"NYC API error {r.status_code}: {r.text[:200]}")
            rows = r.json()
            if not rows:
                break

            self.stdout.write(
                self.style.NOTICE(f"Fetched {len(rows)} rows (offset {params['$offset']})")
            )
            self._ingest(rows)

            imported += len(rows)
            params["$offset"] += len(rows)

        self.stdout.write(self.style.SUCCESS(f"Imported ~{imported} rows."))

    @transaction.atomic
    def _ingest(self, rows):
        # Cache/lookup to avoid repeated queries per batch
        restaurant_cache: Dict[str, Restaurant] = {}
        restaurants_to_update: Dict[int, Restaurant] = {}

        for row in rows:
            camis = norm(row.get("camis"))
            name = norm(row.get("dba"))
            boro = norm(row.get("boro"))
            building = norm(row.get("building"))
            street = norm(row.get("street"))
            zipcode = norm(row.get("zipcode"))
            cuisine = norm(row.get("cuisine_description"))
            grade = norm(row.get("grade"))
            score_str = norm(row.get("score"))
            violation_desc = norm(row.get("violation_description"))
            date_str = norm(row.get("inspection_date"))

            # Parse date
            insp_date = None
            if date_str:
                try:
                    # e.g., "2023-10-03T00:00:00.000"
                    insp_date = dt.date.fromisoformat(date_str.split("T")[0])
                except ValueError:
                    insp_date = None

            # Skip inspections outside allowed range
            if not insp_date or insp_date.year not in ALLOWED_YEARS:
                continue

            # Parse score
            score = None
            if score_str:
                try:
                    score = int(score_str)
                except (ValueError, TypeError):
                    score = None

            # Compose address from NYC fields
            address = " ".join([p for p in [building, street] if p]).strip()
            city = boro if boro else ""
            violation_code = norm(row.get("violation_code"))
            action = norm(row.get("action"))
            critical_flag = norm(row.get("critical_flag"))

            # Find or create Restaurant (prefer camis)
            key = camis or f"{name}|{address}|{zipcode}"
            if key in restaurant_cache:
                restaurant = restaurant_cache[key]
            else:
                if camis:
                    restaurant, _ = Restaurant.objects.get_or_create(
                        camis=camis,
                        defaults={
                            "name": name,
                            "address": address,
                            "city": city,
                            "state": "NY",
                            "zipcode": zipcode,
                            "borough": boro,
                            "cuisine_description": cuisine,
                        },
                    )
                    # If name/address changed, update light fields
                    changed = False
                    if name and restaurant.name != name:
                        restaurant.name = name
                        changed = True
                    if address and restaurant.address != address:
                        restaurant.address = address
                        changed = True
                    if zipcode and restaurant.zipcode != zipcode:
                        restaurant.zipcode = zipcode
                        changed = True
                    if boro and restaurant.borough != boro:
                        restaurant.borough = boro
                        changed = True
                    if cuisine and restaurant.cuisine_description != cuisine:
                        restaurant.cuisine_description = cuisine
                        changed = True
                    if changed:
                        restaurant.save(update_fields=["name", "address", "zipcode", "borough", "cuisine_description"])
                else:
                    restaurant, _ = Restaurant.objects.get_or_create(
                        name=name,
                        address=address,
                        zipcode=zipcode,
                        defaults={
                            "city": city,
                            "state": "NY",
                            "borough": boro,
                            "cuisine_description": cuisine,
                        },
                    )
                restaurant_cache[key] = restaurant

            # Create Inspection (no strict de-dup unless you want it)
            Inspection.objects.create(
                restaurant=restaurant,
                date=insp_date or dt.date(1900, 1, 1),
                grade=grade,
                score=score,
                summary=violation_desc,
                violation_code=violation_code,
                action=action,
                critical_flag=critical_flag,
            )
            if restaurant.pk:
                restaurants_to_update[restaurant.pk] = restaurant

        if restaurants_to_update:
            grade_restaurants(restaurants_to_update.values(), service=self.grading_service)
