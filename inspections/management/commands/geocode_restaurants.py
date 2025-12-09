"""
Django management command to geocode restaurant addresses.

This command uses Nominatim (OpenStreetMap's free geocoding service) to
convert restaurant addresses to latitude/longitude coordinates.

Usage:
    python manage.py geocode_restaurants
    python manage.py geocode_restaurants --limit 100
    python manage.py geocode_restaurants --missing-only
"""
import time
import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from inspections.models import Restaurant


class Command(BaseCommand):
    help = "Geocode restaurant addresses to get latitude/longitude coordinates"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit the number of restaurants to geocode",
        )
        parser.add_argument(
            "--missing-only",
            action="store_true",
            help="Only geocode restaurants that don't have coordinates",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=1.0,
            help="Delay between requests in seconds (default: 1.0, required by Nominatim)",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        missing_only = options["missing_only"]
        delay = max(1.0, options["delay"])  # Nominatim requires at least 1 second between requests

        # Build queryset
        queryset = Restaurant.objects.all()
        if missing_only:
            queryset = queryset.filter(latitude__isnull=True, longitude__isnull=True)
        
        if limit:
            queryset = queryset[:limit]

        total = queryset.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("No restaurants to geocode."))
            return

        self.stdout.write(f"Geocoding {total} restaurant(s)...")
        self.stdout.write(f"Using {delay}s delay between requests (Nominatim requirement)")

        success_count = 0
        error_count = 0
        skipped_count = 0

        for idx, restaurant in enumerate(queryset, 1):
            # Skip if already has coordinates
            if restaurant.latitude and restaurant.longitude:
                skipped_count += 1
                self.stdout.write(f"[{idx}/{total}] Skipping {restaurant.name} (already geocoded)")
                continue

            # Build address string
            address_parts = [
                restaurant.address,
                restaurant.city,
                restaurant.state,
                restaurant.zipcode,
                "New York, NY",  # Add context for better geocoding
            ]
            address = ", ".join(part for part in address_parts if part)

            if not address:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f"[{idx}/{total}] {restaurant.name}: No address data")
                )
                continue

            try:
                # Geocode using Nominatim (free, no API key required)
                url = "https://nominatim.openstreetmap.org/search"
                params = {
                    "q": address,
                    "format": "json",
                    "limit": 1,
                    "addressdetails": 1,
                }
                headers = {
                    "User-Agent": "SafeEatsNYC/1.0 (Educational Project)",  # Required by Nominatim
                }

                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()

                data = response.json()
                if not data:
                    error_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"[{idx}/{total}] {restaurant.name}: No results found")
                    )
                    continue

                result = data[0]
                lat = float(result["lat"])
                lng = float(result["lon"])

                # Update restaurant
                with transaction.atomic():
                    restaurant.latitude = lat
                    restaurant.longitude = lng
                    restaurant.save(update_fields=["latitude", "longitude"])

                success_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[{idx}/{total}] {restaurant.name}: {lat:.6f}, {lng:.6f}"
                    )
                )

                # Respect rate limit (1 request per second)
                if idx < total:
                    time.sleep(delay)

            except requests.RequestException as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f"[{idx}/{total}] {restaurant.name}: {str(e)}")
                )
            except (KeyError, ValueError, IndexError) as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f"[{idx}/{total}] {restaurant.name}: Invalid response - {str(e)}")
                )

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"Successfully geocoded: {success_count}"))
        self.stdout.write(self.style.WARNING(f"Skipped (already geocoded): {skipped_count}"))
        self.stdout.write(self.style.ERROR(f"Errors: {error_count}"))
        self.stdout.write("=" * 60)

