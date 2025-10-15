from django.urls import path
from .views import RestaurantSearchView, RestaurantFilterView

urlpatterns = [
    path("search/", RestaurantSearchView.as_view(), name="restaurant-search"),
    path("filter/", RestaurantFilterView.as_view(), name="restaurant-filter"),
]
