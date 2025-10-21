from django.urls import path
from .views import RestaurantSearchView, RestaurantDetailView

urlpatterns = [
    path("search/", RestaurantSearchView.as_view(), name="restaurant-search"),
    path("<int:pk>/", RestaurantDetailView.as_view(), name="restaurant-detail"),
]