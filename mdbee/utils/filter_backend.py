from functools import reduce

import django.contrib.postgres.fields.jsonb
import simplejson
from dateutil.parser import parse
from django.db.models import Q, Lookup
from django.db.models.fields import Field
from rest_framework import filters

# from django.contrib.postgres.fields import Field


_operator_map = {
    "eq": lambda x, y: Q(**{x: y}),
    "neq": lambda x, y: ~Q(**{x: y}),
    "lt": lambda x, y: Q(**{x + "__lt": y}),
    "lte": lambda x, y: Q(**{x + "__lte": y}),
    "gt": lambda x, y: Q(**{x + "__gt": y}),
    "gte": lambda x, y: Q(**{x + "__gte": y}),
    "in": lambda x, y: Q(**{x + "__in": y}),
    "contains": lambda x, y: Q(**{x + "__contains": y}),
    "icontains": lambda x, y: Q(**{x + "__icontains": y}),
    "startswith": lambda x, y: Q(**{x + "__startswith": y}),
    "istartswith": lambda x, y: Q(**{x + "__istartswith": y}),
}


def get_clause(op, name, value):
    return _operator_map[op](name, value)


def valley_date(argument):
    '''
    I know its bad coding practice.
    But I like big puns and I can not lie.
    Ya'll brothers can't deny.
    '''
    try:
        return parse(argument)
    except ValueError as ve:
        return argument
    except Exception as e:
        return argument


def _apply_filters(queryset, filter_dict, q_form=None):
    """Apply filters from filter json found in url query parameters.

    # TODO: lacks support for neq, like, ilike
    # TODO: lacks support for model-provided filter maps...
    #       enzen-services has them on controllers but they'll go on
    #       models here, I guess.
    """
    and_filters = []
    for name, and_conditions in filter_dict.items():
        if name == "OR":
            sub_filter_dict_or_list = and_conditions
            and_filters.append(reduce(
                lambda x, y: apply_filters(queryset, y, q_form=True) | x,
                sub_filter_dict_or_list,
                Q()
            ))
        else:
            or_clause = None
            for or_conditions in and_conditions:
                sub_and_clause = None
                for operator, value in or_conditions.items():
                    #TODO: handle date filter by creating 'idateeq' filter
                    # if isinstance(value, str):
                        # value = valley_date(value)
                    new_clause = get_clause(operator, name, value)
                    if sub_and_clause is None:
                        sub_and_clause = new_clause
                    else:
                        sub_and_clause = sub_and_clause & new_clause
                if sub_and_clause is not None:
                    if or_clause is None:
                        or_clause = sub_and_clause
                    else:
                        or_clause = or_clause | sub_and_clause
            if or_clause is not None:
                and_filters.append(or_clause)
    if not q_form:
        for and_conditions in and_filters:
            queryset = queryset.filter(and_conditions)
        return queryset
    else:
        q = Q()
        for and_conditions in and_filters:
            q = q & and_conditions
        return q


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


class CommonFilterBackend(filters.BaseFilterBackend):
    """
    Filtering backend semi-compatible with the base enzen-services application.

    Filters are specified in GET params using params["filters"] = {...}

    This dict is of one of two forms:
    1.
        {
            "delivery_date": [
                {
                    "lte": "2018",
                    "gte": "2017"
                }
            ],
            "unit": [
                {
                    "eq": "item1"
                },
                {
                    "eq": "item2"
                }
            ],
            "OR": [
                {
                    "received_code": [
                        {
                            "contains": "qw"
                        }
                    ]
                },
                "received_code": [
                    {
                        "contains": "er"
                    }
                ]
            ]
        }

        Overall, filtering based on all keys is combined with an AND.
        Eg. in this case,
            select ... where delivery_date ... AND unit ...

        With each list, filters based on objects are combined with OR.
        Eg. In this case,
            select ... where unit = 'item1' OR unit = 'item2'

        Multiple operators specified in the object are combined with AND.
        Eg. In this case,
            select ... where delivery_date <= 2018 AND delivery_date >=2017

        A special key called OR treats its value in the same manner as specified
        if it's an object or as specified below if the value is a list.

        Nested OR's may or may not work. While it may seem obvious that they should,
        we're not sure whether we want to do that. We ARE recursing so it's supposed to work
        but don't take it for granted that we'll allow it.

    2.
        [
            {...}
        ]

        A list of objects to be treated exactly as stated above,
        and combined with AND, again.

        The way the two AND's are SUPPOSED to function is specifying how
        to contrain results in an M2M situation.

        The outer AND is supposed to say, for example, that a survey has to have a
        question with id 2 and some question that has an answer containing 'meow'.

        The inner AND, on the other hand, says that a survey has to have a
        question with id 2 and the answer to that question must contain 'meow'.

        It does not do this automatically and views inside apps are meant to enforce
        it manually.

        Commons may be able to do this automatically to some extent but
        needs testing and work to see if it works in this manner.
        The relevant documentation may be found at the link below, but the issue
        is we use Q objects and stuff, instead of chaining .filter calls.
        # https://docs.djangoproject.com/en/2.0/topics/db/queries/#spanning-multi-valued-relationships
    """

    def filter_queryset(self, request, queryset, view):
        filters = request.GET.get("filters", "")
        if not filters:
            return queryset
        filters = simplejson.loads(filters)
        # Old style filtering
        # for k, v in request.GET.items():
        #     if k in ["id", "password", "limit", "offset", "filters", "page"]:
        #         continue
        #     filters[k] = [{"eq": x} for x in v]
        filtered_queryset = apply_filters(queryset=queryset, filter_dict_or_list=filters)
        # We don't do normal distinct because it has edge case issues.
        # At least one that I know is that it fails if the model has jsonb fields.
        if hasattr(queryset.model, 'id'):
            return queryset.filter(id__in=filtered_queryset.values('id'))
        else:
            return filtered_queryset.distinct(*[x.lstrip('-') for x in view.get_ordering(request)])


@Field.register_lookup
class ArrayObjectFilter(Lookup):
    lookup_name = 'aof'

    def as_sql(self, compiler, connection):
        adapter = django.contrib.postgres.fields.jsonb.JsonAdapter(adapted='')
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        if type(rhs_params[0]) == type(adapter):
            name = rhs_params[0].adapted
        else:
            name = rhs_params[0]
        field_name, rhs_params = name.split('__', 1)
        params = lhs_params + [rhs_params]
        return ('''
            EXISTS (SELECT 1
            FROM jsonb_array_elements((%s)::jsonb) AS jae(objs)
            WHERE jae.objs->>'%s' = %s)
        ''' % (lhs, field_name, rhs)), params

# SELECT {reqs[0]} FROM (
# VALUES
# ('[{"uuid": "1234", "name": "boo"}]'::jsonb),
# ('[{"uuid": "4312", "name": "oob"}]'::jsonb))
# AS tbl(farmer)
# WHERE EXISTS (SELECT 1
# FROM jsonb_array_elements(%s) AS jae(objs)
# WHERE jae.objs->>'%s' = %s)
