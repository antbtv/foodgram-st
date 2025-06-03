from rest_framework.pagination import PageNumberPagination

from .constants import (
    PAGINATION_PAGE_SIZE,
    PAGINATION_PAGE_SIZE_QUERY_PARAM
)


class Paginator(PageNumberPagination):
    page_size = PAGINATION_PAGE_SIZE
    page_size_query_param = PAGINATION_PAGE_SIZE_QUERY_PARAM
