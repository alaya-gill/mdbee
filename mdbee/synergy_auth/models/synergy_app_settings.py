from django.contrib.postgres.fields import JSONField
from django.db.models import CharField, Model


class ApplicationSettings(Model):
    setting_name = CharField(max_length=255, unique=True)
    value = JSONField(default=dict)
    pagination_class = None

    def __str__(self):
        return self.setting_name.replace('_',' ').title()
