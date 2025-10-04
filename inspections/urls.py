from django.urls import path
from .views import RestaurantSearchView

urlpatterns = [
    path("search/", RestaurantSearchView.as_view(), name="restaurant-search"),
]