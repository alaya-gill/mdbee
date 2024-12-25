import json
from uuid import uuid4

from django.conf import settings
from django.db.models import DO_NOTHING
from django.db.models import DateTimeField, BigAutoField, ForeignKey, \
    TextField, BooleanField, IntegerField, UUIDField
from django.db.models import Model
from django.utils import timezone
from django_extensions.db.fields import AutoSlugField

from mdbee.utils.timezone import datetime_converter

SUPER_ADMIN_USER_ID = 1


def slugify(content):
    return content.replace('_', '-').lower()


class AbstractBaseModel(Model):
    id = BigAutoField(primary_key=True)
    slug = AutoSlugField(max_length=255, db_index=True, allow_unicode=True, unique=True, populate_from=[
                         'first_name', 'last_name'], slugify_function=slugify)
    created_by = ForeignKey(
        "users.User", on_delete=DO_NOTHING, related_name="+")
    created_on = DateTimeField(default=timezone.now)
    updated_by = ForeignKey(
        "users.User", on_delete=DO_NOTHING, related_name="+")
    updated_on = DateTimeField(default=timezone.now)

    class Meta:
        abstract = True
        
    def changed(self):
        changed_dict = dict()
        all_fields = [f.name for f in self._meta.fields]
        for field in all_fields:
            orig = "__original_%s" % field
            if getattr(self, orig) != getattr(self, field):
                changed_dict[field] = {"old": str(getattr(
                    self, orig)), "new": str(getattr(self, field))}
        
        return json.dumps(changed_dict, default=datetime_converter)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_on = timezone.now()#.strftime('%d/%m/%Y %H:%M:%S')
        self.updated_on = timezone.now()#.strftime('%d/%m/%Y %H:%M:%S')
        return super(AbstractBaseModel, self).save(*args, **kwargs)
