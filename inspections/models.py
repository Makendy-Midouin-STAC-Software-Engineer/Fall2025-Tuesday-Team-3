from django.db import models


class Restaurant(models.Model):
    camis = models.CharField(max_length=20, blank=True, default="", db_index=True)  # NYC unique ID
    name = models.CharField(max_length=255, db_index=True)
    address = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=64, blank=True, default="")
    state = models.CharField(max_length=2, blank=True, default="")
    zipcode = models.CharField(max_length=10, blank=True, default="")
    borough = models.CharField(max_length=64, blank=True, default="", db_index=True)
    cuisine_description = models.CharField(max_length=255, blank=True, default="", db_index=True)
    phone = models.CharField(max_length=20, blank=True, default="")
    regraded_letter = models.CharField(max_length=8, blank=True, default="")
    star_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    forbidden_years = models.JSONField(default=dict, blank=True)
    grading_explanations = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class Inspection(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="inspections")
    date = models.DateField()
    grade = models.CharField(max_length=2, blank=True, default="")
    score = models.PositiveIntegerField(null=True, blank=True)
    summary = models.TextField(blank=True, default="")
    violation_code = models.CharField(max_length=10, blank=True, default="")
    action = models.CharField(max_length=255, blank=True, default="")
    critical_flag = models.CharField(max_length=20, blank=True, default="")

    class Meta:
        ordering = ["-date"]  # Most recent first

    def __str__(self):
        return f"{self.restaurant.name} ({self.date})"
