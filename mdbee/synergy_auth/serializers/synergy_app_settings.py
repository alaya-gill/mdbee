from rest_framework import serializers

from mdbee.synergy_auth.models import ApplicationSettings


class AppSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApplicationSettings
        fields = '__all__'


class AppSettingsAuditLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApplicationSettings
        fields = ('setting_name', 'value', 'pagination_class')
