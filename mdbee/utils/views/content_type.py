from django.contrib.contenttypes.models import ContentType
from django.db.migrations import Migration
from rest_framework import generics
from rest_framework.response import Response

from mdbee.utils.serializers.content_type import ContentTypeSerializer


class ContentTypeView(generics.GenericAPIView):
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer

    def get(self, request, *args, **kwargs):
        default_content_types=[obj for obj in self.get_queryset() if str(obj)!='migration']
        unr_classes=[ContentType.objects.get_for_model(unr_class) for unr_class in UNREGISTERED_CLASSES if unr_class is not Migration]
        unregistered_classes=[unr_class for unr_class in unr_classes if str(unr_class)!='migration']
        final_content_types=[obj.id for obj in default_content_types if obj not in unregistered_classes]
        queryset=self.get_queryset().filter(id__in=final_content_types)

        queryset = queryset.order_by('-model')
        queryset=self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
