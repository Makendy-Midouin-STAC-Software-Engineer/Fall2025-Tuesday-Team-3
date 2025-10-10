import os
import datetime as dt
from typing import Dict, Any

import requests
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from inspections.models import Restaurant, Inspection

SODA_URL = "https://data.cityofnewyork.us/resource/43nn-pn8j.json"
PAGE_SIZE = 50000  # NYC API max limit

def norm(s: Any) -> str:
    return (s or "").strip()

class Command(BaseCommand):
    help = "Import NYC restaurant inspections into local DB."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=999999999, help="Max rows to import for this run.")
        parser.add_argument("--since", type=str, help="YYYY-MM-DD to import records with inspection_date >= since.")
        parser.add_argument("--token", type=str, help="Socrata app token (optional).")

    def handle(self, *args, **opts):
        total_limit = opts["limit"]
        since = opts.get("since")
        token = opts.get("token") or os.environ.get("SODA_APP_TOKEN")

        headers = {}
        if token:
            headers["X-App-Token"] = token

        params = {"$limit": PAGE_SIZE, "$offset": 0}
        if since:
            params["$where"] = f"inspection_date >= '{since}T00:00:00.000'"

        imported = 0
        while imported < total_limit:
            # Cap the final page
            page_limit = min(PAGE_SIZE, total_limit - imported)
            params["$limit"] = page_limit

            r = requests.get(SODA_URL, params=params, headers=headers, timeout=60)
            if r.status_code != 200:
                raise CommandError(f"NYC API error {r.status_code}: {r.text[:200]}")
            rows = r.json()
            if not rows:
                break

            self.stdout.write(self.style.NOTICE(f"Fetched {len(rows)} rows (offset {params['$offset']})"))
            self._ingest(rows)

            imported += len(rows)
            params["$offset"] += len(rows)

        self.stdout.write(self.style.SUCCESS(f"Imported ~{imported} rows."))

    @transaction.atomic
    def _ingest(self, rows):
        # Cache/lookup to avoid repeated queries per batch
        restaurant_cache: Dict[str, Restaurant] = {}
        inspections_to_create = []

        for row in rows:
            camis = norm(row.get("camis"))
            name = norm(row.get("dba"))
            boro = norm(row.get("boro"))
            building = norm(row.get("building"))
            street = norm(row.get("street"))
            zipcode = norm(row.get("zipcode"))
            cuisine = norm(row.get("cuisine_description"))
            grade = norm(row.get("grade"))
            violation_desc = norm(row.get("violation_description"))
            date_str = norm(row.get("inspection_date"))
            score_val = row.get("score")

            # Parse date
            insp_date = None
            if date_str:
                try:
                    # e.g., "2023-10-03T00:00:00.000"
                    insp_date = dt.date.fromisoformat(date_str.split("T")[0])
                except ValueError:
                    insp_date = None

            # Parse score
            score = None
            if score_val:
                try:
                    score = int(score_val)
                except (ValueError, TypeError):
                    pass

            # Compose address from NYC fields
            address = " ".join([p for p in [building, street] if p]).strip()
            city = boro if boro else ""

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
                        },
                    )
                    # If name/address changed, update light fields
                    changed = False
                    if name and restaurant.name != name:
                        restaurant.name = name; changed = True
                    if address and restaurant.address != address:
                        restaurant.address = address; changed = True
                    if zipcode and restaurant.zipcode != zipcode:
                        restaurant.zipcode = zipcode; changed = True
                    if changed:
                        restaurant.save(update_fields=["name", "address", "zipcode"])
                else:
                    restaurant, _ = Restaurant.objects.get_or_create(
                        name=name, address=address, zipcode=zipcode,
                        defaults={"city": city, "state": "NY"}
                    )
                restaurant_cache[key] = restaurant

            # Add to bulk list instead of creating one-by-one
            inspections_to_create.append(
                Inspection(
                    restaurant=restaurant,
                    date=insp_date or dt.date(1900,1,1),
                    grade=grade,
                    score=score,
                    summary=violation_desc,
                )
            )

        # Bulk create all inspections
        if inspections_to_create:
            Inspection.objects.bulk_create(inspections_to_create, batch_size=1000, ignore_conflicts=True)
