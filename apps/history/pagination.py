from rest_framework.pagination import PageNumberPagination

class RecentlyViewedItemsPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    page_size = 20
    max_page_size = 40

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data['total_pages'] = self.page.paginator.num_pages
        return response
