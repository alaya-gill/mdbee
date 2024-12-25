from collections import defaultdict
from functools import reduce

from django.db.models import Q
from rest_framework import filters

from .filter_backend import apply_filters, _apply_filters

non_search_fields = ['logentry', 'id', 'password',
    'last_login', 'is_admin', 'is_staff',
    'username', 'date_joined', 'slug', 'created_by',
    'updated_by', 'created_on', 'updated_on',
    'is_admin', 'groups', 'user_permissions', 'account']

def apply_filters(queryset, filter_dict_or_list, q_form=False):
    """
    Unless you know what you're doing, q_form should be false on the first invocation.
    """
    if isinstance(filter_dict_or_list, dict):
        return _apply_filters(queryset=queryset, filter_dict=filter_dict_or_list, q_form=q_form)
    elif isinstance(filter_dict_or_list, list):
        if not q_form:
            return queryset.filter(
                reduce(
                    lambda x, y: x & y,
                    [_apply_filters(queryset=queryset, filter_dict=fd, q_form=True) for fd in filter_dict_or_list],
                    Q()))
        else:
            return reduce(
                lambda x, y: x & y,
                [_apply_filters(queryset=queryset, filter_dict=fd, q_form=True) for fd in filter_dict_or_list],
                Q())
    else:
        raise ValueError("filter_dict_or_list must be like a dict or list, found %s" % str(type(filter_dict_or_list)))


class CommonSearchBackend(filters.BaseFilterBackend):
    """
        # https://docs.djangoproject.com/en/2.0/topics/db/queries/#spanning-multi-valued-relationships
    """
    def filter_queryset(self, request, queryset, view):
        search_value = request.GET.get("search", "")
        if not search_value:
            return queryset

        model = queryset.model._meta
        fields = [f.name for f in model.get_fields(False, False)]
        search_filters = defaultdict(list)
        for field in fields:
            if field in non_search_fields:
                fields.remove(field)
            else:
                search_p = {}
                search_p["icontains"] = search_value
                search_param = defaultdict(list)
                search_param[field].append(search_p)
                search_filters["OR"].append(search_param)

        # filters = simplejson.loads(filters)
        # Old style filtering
        # for k, v in request.GET.items():
        #     if k in ["id", "password", "limit", "offset", "filters", "page"]:
        #         continue
        #     filters[k] = [{"eq": x} for x in v]
        filtered_queryset = apply_filters(queryset=queryset, filter_dict_or_list=search_filters)
        # We don't do normal distinct because it has edge case issues.
        # At least one that I know is that it fails if the model has jsonb fields.
        if hasattr(queryset.model, 'id'):
            return queryset.filter(id__in=filtered_queryset.values('id'))
        else:
            return filtered_queryset.distinct(*[x.lstrip('-') for x in view.get_ordering(request)])
