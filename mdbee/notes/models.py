from django.db.models import *
from django_extensions.db.fields import AutoSlugField, slugify

from mdbee.utils.models import AbstractBaseModel
from mdbee.users.models import User
# Create your models here.

class Note(AbstractBaseModel):
    title = CharField(max_length=255)
    description = CharField(max_length=512)
    user = ForeignKey(User, on_delete=SET_NULL, related_name='notes', 
                      null=True, blank=True)
    slug = AutoSlugField(max_length=255, db_index=True, allow_unicode=True, unique=True, populate_from=[
                         'user__id', 'title'], slugify_function=slugify)

    def __str__(self):
        return self.title