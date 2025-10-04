from django.db import models
class Restaurant(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    address = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=64, blank=True, default="")
    state = models.CharField(max_length=2, blank=True, default="")
    zipcode = models.CharField(max_length=10, blank=True, default="")


    def __str__(self):
        return self.name


class Inspection(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="inspections"
    )
    date = models.DateField()
    grade = models.CharField(max_length=2, blank=True, default="")
    score = models.PositiveIntegerField(null=True, blank=True)
    summary = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.restaurant.name} ({self.date})"
