
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import Group


class UserManager(BaseUserManager):

    def _create_user(self, email, first_name, last_name, phone, password=None,
                     is_admin=False, is_staff=True, is_active=True, **extra_fields):
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")
        if not first_name:
            raise ValueError("User must have a first name")
        if not last_name:
            raise ValueError("User must have a last name")
        if not phone:
            raise ValueError("User must have a phone number")

        # is_system flag represents the Dental Bee system, any thing that is auto generated is done by this user
        is_system = False
        try:
            is_system = extra_fields.pop('is_system')
        except KeyError:
            pass
        
        email = email.lower()
        user = self.model(
            email=self.normalize_email(email)
        )
        user.username = email
        user.first_name = first_name
        user.last_name = last_name
        user.name = first_name + " " + last_name
        user.phone = phone

        user.set_password(password)  # change password to hash
        user.staff = is_staff
        user.active = is_active
        user.is_admin = is_admin

        for k, v in extra_fields.items():
            setattr(user, k, v)

        if user.is_admin:
            user.created_by = None
            user.updated_by = None

        user.save(using=self._db)


        # no need to generate widgets for this user, see comment above about is_system flag
        if is_system:
            return user


        return user

    # for circaidance admin
    def create_superuser(self, email, first_name, last_name, phone, password=None,
                         **extra_fields):
        return self._create_user(email, first_name, last_name, phone, password,
                                 is_admin=True, is_staff=True, is_active=True,)

    # for super admin user
    def create_superadmin(self, email, first_name, last_name, phone, password=None,
                          **extra_fields):
        return self._create_user(email, first_name, last_name, phone, password,
                                 is_admin=True, is_staff=True, is_active=False,)

    # for all other users
    def create_user(self, email, first_name, last_name, phone, password=None,
                    **extra_fields):
        return self._create_user(email, first_name, last_name, phone, password,
                                 is_admin=False, is_staff=True, is_active=True,
                                 **extra_fields)
