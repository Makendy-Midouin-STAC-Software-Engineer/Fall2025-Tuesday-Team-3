from django.urls import path
from .views import RestaurantSearchView, RestaurantDetailView, BoroughListView

urlpatterns = [
    path("search/", RestaurantSearchView.as_view(), name="restaurant-search"),
    path("boroughs/", BoroughListView.as_view(), name="borough-list"),
    path("<int:pk>/", RestaurantDetailView.as_view(), name="restaurant-detail"),
]
