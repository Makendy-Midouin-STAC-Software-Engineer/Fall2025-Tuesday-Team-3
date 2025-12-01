"""
Custom pagination classes for SafeEatsNYC API.
"""
from rest_framework.pagination import PageNumberPagination


class SafeEatsPageNumberPagination(PageNumberPagination):
    """
    Page number pagination with configurable page size.
    """
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

