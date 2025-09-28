from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'pageSize'  # Tên tham số truyền vào cho kích thước trang
    page_query_param = 'page'  # Tên tham số truyền vào cho số trang

    def get_paginated_response(self, data):
        return Response({
            'links': {
               'next': self.get_next_link(),
               'previous': self.get_previous_link()
            },
            'total': self.page.paginator.count,
            'page': self.page.number,
            'pageSize': self.page.paginator.per_page,
            'results': data
        })