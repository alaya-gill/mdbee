from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


class ContentTypeSerializer(ModelSerializer):
    name=serializers.SerializerMethodField()
    value=serializers.SerializerMethodField()
    def get_value(self,obj):
        return gettext(str(obj))
    def get_name(self,obj):
        return gettext(str(obj).title())

    class Meta:
        model=ContentType
        fields=('name','value')
