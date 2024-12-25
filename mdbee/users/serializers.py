from datetime import datetime

import pytz
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import IntegrityError, transaction
from django.utils.translation import gettext, gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.exceptions import ValidationError

from mdbee.users import utils
from mdbee.users.compat import get_user_email, get_user_email_field_name
from mdbee.users.conf import settings
from mdbee.users.models import UserPreviousPassword
from mdbee.users.utils import compare_password
from mdbee.utils.serializers.base import BaseSerializer

from django.contrib.auth.models import Group, Permission

from mdbee.users.utils import compare_password
from mdbee.users.models import UserPreviousPassword

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)


class UserSummarySerializer(BaseSerializer):
    account = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    user_default_type = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()

    def get_groups(self,obj):
        """
        Returns Group Names of User
        @param obj: Object of Model User
        @type obj: Object User Model
        @return: Group Names of User
        @rtype: str
        """
        return [grp for grp in obj.groups.values_list('name',flat=True)]
    
    def get_user_default_type(self,obj):
        """
        Returns Actual User Type (Contact or User)
        @param obj: Object of Model
        @type obj: Object: User Model
        @return: Actual User Type (Contact or User)
        @rtype: str
        """
        return obj.user_type
    def get_user_type(self,obj):
        """
        Returns Translated User Type (Contact or User)
        @param obj: Object of Model
        @type request: Object: User Model
        @return: Translated User Type (Contact or User)
        @rtype: str
        """
        return obj.get_user_type_display()
    def get_name(self, obj):
        return obj.first_name + ' ' + obj.last_name

    def get_account(self, obj):
        if obj.account:
            return obj.account.account_name
        else:
            return None

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'account',
            'slug',
            'name',
            'user_type',
            'id',
            'email',
            'user_default_type',
            'groups'
        )




class UserSerializer(BaseSerializer):
    name = serializers.SerializerMethodField()
    timezone_number = serializers. SerializerMethodField()
    
    def get_active_status(self, obj):
        return obj.get_is_active_display()

    def get_name(self, obj):
        return obj.first_name + ' ' + obj.last_name

    def get_timezone_number(self, obj):
        return datetime.now(pytz.timezone('UTC')).strftime('%z')


    def update(self, instance, validated_data):
        if settings.SEND_ACTIVATION_EMAIL and validated_data.get('email_field', None):
            instance_email = get_user_email(instance)
            if instance_email != validated_data['email_field']:
                instance.is_active = False
                instance.save(update_fields=["is_active"])
        return super().update(instance, validated_data)

    class Meta:
        model = User
        # fields = '__all__'
        exclude = ['password', 'is_staff', 'created_on',
                   'updated_on', 'created_by', 'updated_by', 'username', 'user_permissions']
        # read_only_fields = ('user_type',)
        lookup_field = 'slug'


def search(name, arr):
    for p in arr:
        if p.name == name:
            return True
    return False


class UserListSerializer(BaseSerializer):
    is_active = serializers.CharField(source='get_is_active_display')
    user_type = serializers.SerializerMethodField()
    is_active= serializers.SerializerMethodField()

    def get_is_active(self, obj):
        return obj.get_is_active_display()

    def get_user_type(self, obj):
        return obj.get_user_type_display()
    class Meta:
        model = User
        fields = (
            'name', 'account_name', 'account_number', 'hq_account_number', 'user_groups', 'user_type', 'is_active',
            'city',
            'state', 'created_on', 'updated_on', 'updated_by', 'contact_associated_account')


class UserWritableSerializer(BaseSerializer):
    groups = serializers.SlugRelatedField(slug_field='name', many=True, queryset=Group.objects.all(), required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)

    def validate(self, attrs):
        if attrs.get("groups", None):
            account_users = User.objects.filter(account=self.instance.account)
            is_account_admin = False
            account_admin = None
            # for account_user in account_users:
            #     if account_user.groups.filter(name='Account Admin').count() > 0:
            #         account_admin = account_user
            #         is_account_admin = True
            #         break

            # for group in attrs["groups"]:
            #     if group.name == 'Account Admin' and is_account_admin:
            #         if account_admin != self.instance:
            #             raise serializers.ValidationError({"groups": "This account already has account admin"})
            if self.instance.user_type!='Contact':
                account=None
                if account.users.filter(groups__name='Account Admin').count() > 1:
                    is_account_admin=True
                if self.instance not in account.users.filter(groups__name='Account Admin'):
                    for group in attrs["groups"]:
                        if group.name == 'Account Admin' and is_account_admin:
                                raise serializers.ValidationError({"groups": "This account already has account admin"})



        return super().validate(attrs)

    def update(self, instance, validated_data):
        if "timezone" in validated_data:
            self.context["request"].session['django_timezone'] = validated_data["timezone"]

        return super().update(instance, validated_data)

    class Meta:
        model = User
        exclude = ['password', 'is_staff', 'created_on', 'updated_on', 'created_by',
                   'updated_by', 'id', 'username', 'email', 'date_joined', 'last_login', 'slug']


# Creating System Users while creating an account
class UserCreateSerializer(BaseSerializer):
    groups = serializers.SlugRelatedField(slug_field='name', many=True, queryset=Group.objects.all())

    default_error_messages = {
        "cannot_create_user": settings.CONSTANTS.messages.CANNOT_CREATE_USER_ERROR
    }

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
            "address1",
            "address2",
            "address3",
            "city",
            "state",
            "country",
            "timezone",
            "zipcode",
            "phone2",
            "company",
            "title",
            'date_of_birth',

        )

    def validate(self, attrs):
        # user = User.objects.create(**attrs)
        # password = attrs.get("password")

        # try:
        #     validate_password(password, None)
        # except django_exceptions.ValidationError as e:
        #     serializer_error = serializers.as_serializer_error(e)
        #     raise serializers.ValidationError(
        #         {"password": serializer_error["non_field_errors"]}
        #     )
        super().validate(attrs)
        if not attrs.get('password'):
            attrs["password"] = User.objects.make_random_password()

        return attrs

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")

        return user

    def perform_create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            context = {"user": user}
            to = [get_user_email(user)]
            if settings.SEND_ACTIVATION_EMAIL:
                user.is_active = False
                user.save(update_fields=["is_active"])
                settings.EMAIL.activation_set_password(self.context.get('request'), context).send(to)
            # if settings.SEND_ACTIVATION_EMAIL:
            #     user.is_active = False
            #     user.save(update_fields=["is_active"])
        return user

    # def _get_calling_user(self, default=None):
    #     request = self.context.get('request', None)
    # request.


# Creating System Contacts (System Contact Signup)
class UserCreatePasswordRetypeSerializer(UserCreateSerializer):
    default_error_messages = {
        "password_mismatch": settings.CONSTANTS.messages.PASSWORD_MISMATCH_ERROR
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"] = serializers.CharField(
            style={"input_type": "password"}
        )
        self.fields["re_password"] = serializers.CharField(
            style={"input_type": "password"}
        )

    def validate(self, attrs):
        password = attrs.get("password")

        try:
            validate_password(password, None)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error["non_field_errors"]}
            )

        self.fields.pop("re_password", None)
        re_password = attrs.pop("re_password")
        attrs['username'] = attrs['email']
        attrs = super().validate(attrs)
        if attrs["password"] == re_password:
            return attrs
        else:
            self.fail("password_mismatch")

exclude = ['password', 'is_staff', 'created_on',
                   'updated_on', 'created_by', 'updated_by', 'username', 'user_permissions']
        
# Creating System Users, seperately
class SystemUserCreateSerializer(UserCreateSerializer):
    default_error_messages = {
        "password_mismatch": settings.CONSTANTS.messages.PASSWORD_MISMATCH_ERROR
    }
    
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'city',
            'state',
            'country',
            'zipcode',
            'address',
            'phone',
            "is_superuser",
        )

        lookup_field = 'slug'

    def validate(self, attrs):
        if not attrs.get('password'):
            attrs["password"] = User.objects.make_random_password()

        return attrs

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")

        return user

    def perform_create(self, validated_data):
        with transaction.atomic():
            is_superuser = validated_data.pop('is_superuser')
            if is_superuser:
                user = User.objects.create_superadmin(**validated_data)
            else:
                user = User.objects.create_user(**validated_data)
        return user


class TokenCreateSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=False, style={"input_type": "password"})

    default_error_messages = {
        "invalid_credentials": settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR,
        "inactive_account": settings.CONSTANTS.messages.INACTIVE_ACCOUNT_ERROR,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.fields[settings.LOGIN_FIELD] = serializers.CharField(
            required=False)

    def validate(self, attrs):
        password = attrs.get("password")
        params = {settings.LOGIN_FIELD: attrs.get(settings.LOGIN_FIELD)}
        self.user = authenticate(**params, password=password)
        if not self.user:
            self.user = User.objects.filter(**params).first()
            if self.user and not self.user.check_password(password):
                self.fail("invalid_credentials")
        if self.user and self.user.is_active:
            return attrs
        self.fail("invalid_credentials")


class UserFunctionsMixin:
    def get_user(self, is_active=True):
        try:
            user = User._default_manager.get(
                is_active=is_active,
                **{self.email_field: self.data.get(self.email_field, "")},
            )
            if user.has_usable_password():
                return user
        except User.DoesNotExist:
            pass
        if (
            settings.PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND
            or settings.USERNAME_RESET_SHOW_EMAIL_NOT_FOUND
        ):
            self.fail("email_not_found")


class SendEmailResetSerializer(serializers.Serializer, UserFunctionsMixin):
    default_error_messages = {
        "email_not_found": settings.CONSTANTS.messages.EMAIL_NOT_FOUND
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.email_field = get_user_email_field_name(User)
        self.fields[self.email_field] = serializers.EmailField()


class UidAndTokenSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    default_error_messages = {
        "invalid_token": settings.CONSTANTS.messages.INVALID_TOKEN_ERROR,
        "invalid_uid": settings.CONSTANTS.messages.INVALID_UID_ERROR,
    }

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        # uid validation have to be here, because validate_<field_name>
        # doesn't work with modelserializer
        try:
            uid = utils.decode_uid(self.initial_data.get("uid", ""))
            self.user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            key_error = "invalid_uid"
            raise ValidationError(
                {"uid": [self.error_messages[key_error]]}, code=key_error
            )

        is_token_valid = self.context["view"].token_generator.check_token(
            self.user, self.initial_data.get("token", "")
        )
        if is_token_valid:
            return validated_data
        else:
            key_error = "invalid_token"
            raise ValidationError(
                {"token": [self.error_messages[key_error]]}, code=key_error
            )


class ActivationSerializer(UidAndTokenSerializer):
    default_error_messages = {
        "stale_token": settings.CONSTANTS.messages.STALE_TOKEN_ERROR
    }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not self.user.is_active:
            return attrs
        raise exceptions.PermissionDenied(self.error_messages["stale_token"])


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        user = self.context["request"].user or self.user
        # why assert? There are ValidationError / fail everywhere
        assert user is not None

        try:
            validate_password(attrs["new_password"], user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)})
        return super().validate(attrs)


class PasswordRetypeSerializer(PasswordSerializer):
    re_new_password = serializers.CharField(style={"input_type": "password"})

    default_error_messages = {
        "password_mismatch": settings.CONSTANTS.messages.PASSWORD_MISMATCH_ERROR
    }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs["new_password"] == attrs["re_new_password"]:
            return attrs
        else:
            self.fail("password_mismatch")


class CurrentPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={"input_type": "password"})

    default_error_messages = {
        "invalid_password": settings.CONSTANTS.messages.INVALID_PASSWORD_ERROR
    }

    def validate_current_password(self, value):
        is_password_valid = self.context["request"].user.check_password(value)
        if is_password_valid:
            return value
        else:
            self.fail("invalid_password")


class UsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (settings.LOGIN_FIELD,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username_field = settings.LOGIN_FIELD
        self._default_username_field = User.USERNAME_FIELD
        self.fields["new_{}".format(self.username_field)] = self.fields.pop(
            self.username_field
        )

    def save(self, **kwargs):
        if self.username_field != self._default_username_field:
            kwargs[User.USERNAME_FIELD] = self.validated_data.get(
                "new_{}".format(self.username_field)
            )
        return super().save(**kwargs)


class UsernameRetypeSerializer(UsernameSerializer):
    default_error_messages = {
        "username_mismatch": settings.CONSTANTS.messages.USERNAME_MISMATCH_ERROR.format(
            settings.LOGIN_FIELD
        )
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["re_new_" + settings.LOGIN_FIELD] = serializers.CharField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        new_username = attrs[settings.LOGIN_FIELD]
        if new_username != attrs["re_new_{}".format(settings.LOGIN_FIELD)]:
            self.fail("username_mismatch")
        else:
            return attrs


class TokenSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source="key")

    class Meta:
        model = settings.TOKEN_MODEL
        fields = ("auth_token",)


class SetPasswordSerializer(PasswordSerializer, CurrentPasswordSerializer):
    pass


class SetPasswordRetypeSerializer(PasswordRetypeSerializer, CurrentPasswordSerializer):

    def validate(self, attrs):

        # Validate that this is not one of the old passwords
        new_password = attrs["new_password"]
        request = self.context.get('request')
        user = request.user
        previous_passwords = list(
            UserPreviousPassword.objects.filter(user=user).values_list('old_password', flat=True))
        for prev_pass in previous_passwords:
            if compare_password(new_password, prev_pass):
                raise serializers.ValidationError({"old_password": "New password cannot be the same as old password"})

        return super().validate(attrs)


class PasswordResetConfirmSerializer(UidAndTokenSerializer, PasswordSerializer):
    pass


class PasswordResetConfirmRetypeSerializer(
    UidAndTokenSerializer, PasswordRetypeSerializer
):
    pass


class UsernameResetConfirmSerializer(UidAndTokenSerializer, UsernameSerializer):
    pass


class UsernameResetConfirmRetypeSerializer(
    UidAndTokenSerializer, UsernameRetypeSerializer
):
    pass


class UserDeleteSerializer(serializers.Serializer):
    pass


class SetUsernameSerializer(UsernameSerializer, CurrentPasswordSerializer):
    class Meta:
        model = User
        fields = (settings.LOGIN_FIELD, 'current_password')


class SetUsernameRetypeSerializer(SetUsernameSerializer, UsernameRetypeSerializer):
    pass


class TimezoneLookupSerializer(serializers.Serializer):
    timezones = serializers.ReadOnlyField()


class LogoutSerializer(serializers.Serializer):
    pass


class UidOnlySerializer(serializers.Serializer):
    uid = serializers.CharField()

    default_error_messages = {
        "invalid_uid": settings.CONSTANTS.messages.INVALID_UID_ERROR,
    }

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        # uid validation have to be here, because validate_<field_name>
        # doesn't work with modelserializer
        try:
            uid = utils.decode_uid(self.initial_data.get("uid", ""))
            self.user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            key_error = "invalid_uid"
            raise ValidationError(
                {"uid": [self.error_messages[key_error]]}, code=key_error
            )
        return validated_data


class ResendActivationSetPassword(UidOnlySerializer):
    pass


class ResendActivationAuto(UidOnlySerializer):
    pass


class ParentUserSerializer(BaseSerializer):
    name = serializers.SerializerMethodField()
    is_system_contact = serializers.SerializerMethodField()

    @staticmethod
    def get_name(obj):
        return obj.first_name + ' ' + obj.last_name

    @staticmethod
    def get_is_system_contact(obj):
        return True

    date_of_birth = serializers.SerializerMethodField()

    @staticmethod
    def get_date_of_birth(obj):
        if obj.date_of_birth:
            date = datetime.strftime(obj.date_of_birth, "%d-%b-%Y")
            return date
        else:
            return None

    class Meta:
        model = User
        fields = (
            'slug', 'first_name', 'last_name', 'name', 'title', 'national_no', 'date_of_birth',
            'relationship_to_patient', 'address1', 'address2', 'address3', 'city', 'state', 'country',
            'zipcode', 'email', 'phone', 'phone2',  'language', 'timezone', 'is_system_contact')


class SimpleUserSerializer(BaseSerializer):
    class Meta:
        model = User
        fields = ('slug', 'name', 'email')


class UserMinifiedAuditLogSerializer(serializers.ModelSerializer):
    account = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return ((lambda: gettext("Inactive"), lambda: gettext("Active"))[obj.is_active]())

    def get_name(self, obj):
        return obj.first_name + ' ' + obj.last_name

    def get_account(self, obj):
        if obj.account:
            return obj.account.account_name
        else:
            return None

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'account',
            'name',
            'user_type',
            'id',
            'email',
            'status'
        )


class UserAuditLogSerializer(serializers.ModelSerializer):
    account = serializers.SerializerMethodField()
    # account = MinifiedAccountSerializer()
    user_type = serializers.CharField()
    groups = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    user_permission_list = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    #timezone_number = serializers.SerializerMethodField()

    class Meta:
        model = User
        # fields = '__all__'
        fields = [
            'first_name', 'last_name', 'name', 'title',
            'national_no', 'date_of_birth', 'is_active', 'title', 'account', 'user_type', 'groups', 'user_permission_list',
            'relationship_to_patient', 'address1', 'address2', 'address3', 'city', 'state', 'country', 'contact_associated_account',
            'zipcode', 'email', 'phone', 'phone2', 'language', 'timezone', 'credentials']
        # read_only_fields = ('user_type',)
        lookup_field = 'slug'

    def get_name(self, obj):
        return obj.first_name + ' ' + obj.last_name

    def get_timezone_number(self, obj):
        return datetime.now(pytz.timezone(obj.timezone)).strftime('%z')

    def get_account(self, obj):
        if hasattr(obj, 'account') and obj.account:
            return {
                "id": obj.account.id,
                "account_id": obj.account.account_id,
                "slug": obj.account.slug,
                "parent_account": obj.account.parent_account.account_name if obj.account.parent_account else None,
                "account_name": obj.account.account_name,
            }
        else:
            return None

    def get_user_permission_list(self, obj):
        user_permissions = []
        for group in obj.groups.all():
            user_permissions.extend(group.permissions.all().values_list('codename', flat=True))
        user_permissions = set(user_permissions)


class ParentUserAuditLogSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    @staticmethod
    def get_name(obj):
        return obj.first_name + ' ' + obj.last_name

    date_of_birth = serializers.SerializerMethodField()

    @staticmethod
    def get_date_of_birth(obj):
        if obj.date_of_birth:
            date = datetime.strftime(obj.date_of_birth, "%d-%m-%Y")
            return date
        else:
            return None

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'name', 'title', 'national_no', 'date_of_birth',
            'relationship_to_patient', 'address1', 'address2', 'address3', 'city', 'state', 'country',
            'zipcode', 'email', 'phone', 'phone2',  'language', 'timezone')


class GroupAuditLogSerializer(serializers.ModelSerializer):
    permissionsList = serializers.SerializerMethodField()

    def get_permissionsList(self, obj):
        return list(obj.permissions.values_list('name', flat=True))

    class Meta:
        model = Group
        fields = ('name', 'permissionsList')

class PermissionAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('name')

class UserChangeLogSerializer(BaseSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.first_name + ' ' + obj.last_name

    class Meta:
        model = User
        fields = (
            'slug',
            'name',
        )
