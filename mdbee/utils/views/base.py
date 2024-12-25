from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ..pagination import CursorPaginationMixin


class ResponseInfo(object):
    def __init__(self, user=None, **args):
        self.response = {
            "success": args.get('status', True),
            "status_code": args.get('error', 200),
            "data": args.get('data', []),
            "message": args.get('message', 'success')
        }


class ResponseModelViewSet(ModelViewSet):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(ResponseModelViewSet, self).__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        response_data = super(ResponseModelViewSet, self).list(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["success"] = True
        if not response_data.data:
            self.response_format["message"] = "List empty"
        return Response(self.response_format, content_type="text/html")

    def retrieve(self, request, *args, **kwargs):
        response_data = super(ResponseModelViewSet, self).retrieve(
            request, *args, **kwargs)
        self.response_format["data"] = {"result": response_data.data}
        self.response_format["success"] = True
        if not response_data.data:
            self.response_format["message"] = "Empty"
        return Response(self.response_format, content_type="text/html")


    def create(self, request, *args, **kwargs):
        response_data = super(ResponseModelViewSet, self).create(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = True
        return Response(self.response_format, content_type="text/html")


    def update(self, request, *args, **kwargs):
        response_data = super(ResponseModelViewSet, self).update(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = True

        return Response(self.response_format, content_type="text/html")


    def destroy(self, request, *args, **kwargs):
        response_data = super(ResponseModelViewSet, self).destroy(
            request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = True
        return Response(self.response_format, content_type="text/html")


class BaseViewset(CursorPaginationMixin, ResponseModelViewSet):

    lookup_field = 'slug'
    action_serializers = dict()

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(BaseViewset, self).__init__(**kwargs)

    def get_serializer_class(self):
        if self.action and self.action in self.action_serializers:
            return self.action_serializers[self.action]
        else:
            return self.action_serializers['default']

    def create(self, request, *args, **kwargs):
        if request.data \
            and request.data.get(self.lookup_field) \
                and self.get_queryset().filter(**{self.lookup_field: request.data[self.lookup_field]}).first():
            kwargs.update({self.lookup_field: request.data[self.lookup_field]})
            self.kwargs.update(
                {self.lookup_field: request.data[self.lookup_field]})
            # return super().update(request, *args, **kwargs)
            # as opposed to self.update because we don't ever want to get stuck looping between update and create
            # ok so we've relented. Have faith.
            return self.update(request, *args, **kwargs)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        lookup_val = self.request.parser_context.get(
            'kwargs', {}).get(self.lookup_field)
        if not lookup_val:
            lookup_val = request.data and request.data.get(self.lookup_field)
        if lookup_val \
                and not self.get_queryset().filter(**{self.lookup_field: lookup_val}).first():
            del kwargs[self.lookup_field]
            # return super().create(request, *args, **kwargs)
            # as opposed to self.create because we don't ever want to get stuck looping between update and create
            # ok so we've relented. Have faith.
            try:
                return self.create(request, *args, **kwargs)
            except Exception as e:
                # So if the record is deleted, for example, the above will fail, as the requester is trying to
                # update a queryset it doesn't have access to (get_queryset generally excludes is_deleted).
                # Allowing this is messed up, but a compromise is to just fake it (this way teh tablet keeps working).
                # We just record the event in sentry instead.
                return Response(data=dict())
        return super().update(request, *args, **kwargs)
