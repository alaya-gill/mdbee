import six

from rest_framework.pagination import PageNumberPagination, CursorPagination


class CustomCursorPagination(CursorPagination):
    max_page_size = 10000
    page_size = 100
    # ordering = 'id'


class CursorPaginationMixin:
    """Add support for cursor pagination, much more efficient.

    ONLY WORKS WHEN THE ID IS MADE USING POSTGRES' SEQUENCES
    SO THEY'RE ALWAYS INCREASING.

    SO take care for example if importing data into the table
    that already has ids.

    Caveats: no page count, orders on id only.
    Use next/previous links to navigate pages,
    not page_number.

    If the mixin is used with a viewset, make sure the mixin
    is appears first in the inheritance order.

    Uses only the "limit" argument to set page size,
    does not use a page argument.
    """

    # TODO: Override get_page_size or set self.page_size_query_param instead of
    # what's done currently.

    def get_ordering(self, request, queryset=None, view=None):
        if self.request.GET.get('cursor_pagination'):
            return ('id', )
        else:
            return super().paginator.get_ordering(request, queryset, view)

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if self.request.GET.get('cursor_pagination'):
            if not hasattr(self, '_paginator'):
                self._paginator = getattr(self, 'cursor_pagination_class', CustomCursorPagination)()
                self._paginator.ordering = self.get_ordering(self.request)
                self._paginator.page_size = min(
                    int(self.request.GET.get('limit', self._paginator.page_size)),
                    self._paginator.max_page_size)
                return self._paginator
        return super().paginator


class PageLimitPagination(PageNumberPagination):
    """Pagination support using page numbers and sizes.

    Ordering logic based on rest framework's cursorpagination class.
    """

    # TODO: optimize

    page_size_query_param = 'limit'
    max_page_size = 1000
    page_query_param = 'page'
    ordering = '-created_on'

    def paginate_queryset(self, queryset, request, view=None):
        ordering = self.get_ordering(request, queryset, view)
        queryset = queryset.order_by(*ordering)
        return super().paginate_queryset(queryset, request=request, view=view)

    def get_ordering(self, request, queryset, view):
        """
        Return a tuple of strings, that may be used in an `order_by` method.
        """
        # ordering_filters = [
        #     filter_cls for filter_cls in getattr(view, 'filter_backends', [])
        #     if hasattr(filter_cls, 'get_ordering')
        # ]
        #
        # if ordering_filters:
        #     # If a filter exists on the view that implements `get_ordering`
        #     # then we defer to that filter to determine the ordering.
        #     filter_cls = ordering_filters[0]
        #     filter_instance = filter_cls()
        #     ordering = filter_instance.get_ordering(request, queryset, view)
        #     assert ordering is not None, (
        #         'Using cursor pagination, but filter class {filter_cls} '
        #         'returned a `None` ordering.'.format(
        #             filter_cls=filter_cls.__name__
        #         )
        #     )

        # The default is to check if the request provides what to order by.

        # The fallback case is to check for an `ordering` attribute
        # on this pagination instance.
        ordering = request.query_params.get('sort_by')
        if not ordering:
            ordering = self.ordering
        else:
            sort_type = request.query_params.get('sort_order', 'asc').lower()
            if sort_type == 'asc':
                ordering = ordering.lstrip('-')
            elif sort_type == 'desc' and not ordering.startswith('-'):
                ordering = '-{}'.format(ordering)
        assert ordering is not None, (
            'Using PageLimit pagination, but no ordering attribute was declared '
            'in the request or on the pagination class.'
        )
        # assert '__' not in ordering, (
        #     'Cursor pagination does not support double underscore lookups '
        #     'for orderings. Orderings should be an unchanging, unique or '
        #     'nearly-unique field on the model, such as "-created" or "pk".'
        # )

        assert isinstance(ordering, (six.string_types, list, tuple)), (
            'Invalid ordering. Expected string or tuple, but got {type}'.format(
                type=type(ordering).__name__
            )
        )

        if isinstance(ordering, six.string_types):
            return (ordering,)
        return tuple(ordering)
