import logging

from rest_framework.serializers import ModelSerializer, IntegerField

# Get an instance of a logger
logger = logging.getLogger(__name__)


def has_field(model, fieldname, approx=True):
    if approx:
        return hasattr(model, fieldname)
    return list(filter(lambda x: x.name == fieldname, model._meta.fields))


class DummyRequest:
    session = None


class BaseSerializer(ModelSerializer):
    created_by_id = IntegerField(required=False, allow_null=True)

    class Meta:
        exclude = ['id']
        lookup_field = 'slug'

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    def _get_calling_user(self, default=None):
        # return self.context.get('request', DummyRequest()).session.get('user_id', default)
        try:
            return self.context["request"].user.id
        except Exception:
            logger.error('Something went wrong!')
            return None

    def update(self, instance, validated_data):
        if self.context.get('request') and has_field(self.Meta.model, 'updated_by'):
            # TODO: check if below line should be self.instance or instance
            instance.updated_by_id = self._get_calling_user() or 1
        validated_data.pop('created_by_id', None)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        if self.context.get('request') and has_field(self.Meta.model, 'created_by'):
            validated_data['created_by_id'] = self._get_calling_user() or 1
        if self.context.get('request') and has_field(self.Meta.model, 'updated_by'):
            validated_data['updated_by_id'] = self._get_calling_user() or 1
        return super().create(validated_data)

    # def to_representation(self, instance):
    #     ret = super(ModelSerializer, self).to_representation(instance)
    #     # check the request is list view or detail view
    #     is_list_view = isinstance(self.instance, list)
    #     extra_ret = {'key': 'list value'} if is_list_view else {'key': 'single value'}
    #     ret.update(extra_ret)
    #     return ret
