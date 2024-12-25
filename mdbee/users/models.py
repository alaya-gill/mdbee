import json

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.db.models import CASCADE
from django.db.models import CharField, DateTimeField, ForeignKey, TextField, BooleanField, PROTECT, DateField
from django.db.models import Model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group
from django.core.validators import EmailValidator
from django.urls import reverse
from django.utils import timezone
from django_extensions.db.fields import AutoSlugField
from pytz import common_timezones

from mdbee.users.manager import UserManager
from mdbee.utils.timezone import datetime_converter

SUPER_ADMIN_USER_ID = 1



def slugify(content):
    return content.replace('_', '-').lower()


class User(AbstractUser):
    # First Name and Last Name do not cover name patterns
    # around the globe.
    def __str__(self):
        return self.email

    first_name = CharField(max_length=255)
    last_name = CharField(max_length=255)
    # not the account, field specific to contact
    company = CharField(max_length=255, null=True, blank=True)
    email = CharField(
        _('email address'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer.'),
        validators=[EmailValidator],
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    country = CharField(max_length=255, null=True, blank=True)
    city = CharField(max_length=255, null=True, blank=True)
    state = CharField(max_length=255, null=True, blank=True)
    zipcode = CharField(max_length=11, null=True, blank=True)
    address = TextField(max_length=512, null=True, blank=True)
    phone = CharField(max_length=15)

    slug = AutoSlugField(max_length=255, db_index=True, allow_unicode=True, unique=True, populate_from=[
        'first_name', 'last_name'], slugify_function=slugify)
    created_by = ForeignKey('self', on_delete=CASCADE,
                            related_name="+", default=SUPER_ADMIN_USER_ID, null=True, blank=True)
    created_on = DateTimeField(default=timezone.now)
    updated_by = ForeignKey('self', on_delete=CASCADE,
                            related_name="+", default=SUPER_ADMIN_USER_ID, null=True, blank=True)
    updated_on = DateTimeField(default=timezone.now)

    disable_notification = BooleanField(default=False)
    date_of_birth = DateField(null=True, blank=True)

    is_active = BooleanField(default=True)

    REQUIRED_FIELDS = ['first_name', 'last_name',
                       'phone']

    USERNAME_FIELD = 'email'

    EMAIL_FIELD = 'email'

    objects = UserManager()

    # def __init__(self, *args, **kwargs):
    #     super(User, self).__init__(*args, **kwargs)
    #     all_fields = [f.name for f in self._meta.fields]
    #     for field in all_fields:
    #         setattr(self, '__original_%s' % field, getattr(self, field))

    # def changed(self):
    #     changed_dict = dict()
    #     all_fields = [f.name for f in self._meta.fields]
    #     for field in all_fields:
    #         orig = '__original_%s' % field
    #         if getattr(self, orig) != getattr(self, field):
    #             changed_dict[field] = {"old": getattr(
    #                 self, orig), "new": getattr(self, field)}
    #     return changed_dict

    def get_absolute_url(self):
        return reverse("users:user-detail", kwargs={"slug": self.slug})



class UserPreviousPassword(Model):
    user = ForeignKey(User, on_delete=PROTECT, related_name="previous_passwords")
    old_password = CharField(_('old_password'), max_length=128)

    def __str__(self):
        return self.user.email

