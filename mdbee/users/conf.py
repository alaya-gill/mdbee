from django.apps import apps
from django.conf import settings as django_settings
from django.test.signals import setting_changed
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string

DJOSER_SETTINGS_NAMESPACE = "DJOSER"

auth_module, user_model = django_settings.AUTH_USER_MODEL.rsplit(".", 1)

User = apps.get_model(auth_module, user_model)


class ObjDict(dict):
    def __getattribute__(self, item):
        try:
            val = self[item]
            if isinstance(val, str):
                val = import_string(val)
            elif isinstance(val, (list, tuple)):
                val = [import_string(v) if isinstance(
                    v, str) else v for v in val]
            self[item] = val
        except KeyError:
            val = super(ObjDict, self).__getattribute__(item)

        return val


default_settings = {
    "USER_ID_FIELD": 'slug',
    "LOGIN_FIELD": 'email',
    "SEND_ACTIVATION_EMAIL": True,
    "SEND_CONFIRMATION_EMAIL": False,
    "USER_CREATE_PASSWORD_RETYPE": False,
    "SET_PASSWORD_RETYPE": False,
    "PASSWORD_RESET_CONFIRM_RETYPE": False,
    "SET_USERNAME_RETYPE": False,
    "USERNAME_RESET_CONFIRM_RETYPE": False,
    "PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND": False,
    "USERNAME_RESET_SHOW_EMAIL_NOT_FOUND": False,
    "PASSWORD_CHANGED_EMAIL_CONFIRMATION": False,
    "USERNAME_CHANGED_EMAIL_CONFIRMATION": False,
    "TOKEN_MODEL": "rest_framework.authtoken.models.Token",
    "SERIALIZERS": ObjDict(
        {
            "activation": "mdbee.users.serializers.ActivationSerializer",
            "password_reset": "mdbee.users.serializers.SendEmailResetSerializer",
            "password_reset_confirm": "mdbee.users.serializers.PasswordResetConfirmSerializer",
            "password_reset_confirm_retype": "mdbee.users.serializers.PasswordResetConfirmRetypeSerializer",
            "set_password": "mdbee.users.serializers.SetPasswordSerializer",
            "set_password_retype": "mdbee.users.serializers.SetPasswordRetypeSerializer",
            "set_username": "mdbee.users.serializers.SetUsernameSerializer",
            "set_username_retype": "mdbee.users.serializers.SetUsernameRetypeSerializer",
            "username_reset": "mdbee.users.serializers.SendEmailResetSerializer",
            "username_reset_confirm": "mdbee.users.serializers.UsernameResetConfirmSerializer",
            "username_reset_confirm_retype": "mdbee.users.serializers.UsernameResetConfirmRetypeSerializer",
            "user_create": "mdbee.users.serializers.UserCreateSerializer",
            "user_create_password_retype": "mdbee.users.serializers.UserCreatePasswordRetypeSerializer",
            "user_delete": "mdbee.users.serializers.UserDeleteSerializer",
            "user": "mdbee.users.serializers.UserSerializer",
            "current_user": "mdbee.users.serializers.UserSerializer",
            "token": "mdbee.users.serializers.TokenSerializer",
            "token_create": "mdbee.users.serializers.TokenCreateSerializer",
        }
    ),
    "EMAIL": ObjDict(
        {
            "activation": "mdbee.users.email.ActivationEmail",
            "confirmation": "mdbee.users.email.ConfirmationEmail",
            "password_reset": "mdbee.users.email.PasswordResetEmail",
            "password_changed_confirmation": "mdbee.users.email.PasswordChangedConfirmationEmail",
            "activation_set_password": "mdbee.users.email.ActivationSetPasswordEmail",
            "username_changed_confirmation": "mdbee.users.email.UsernameChangedConfirmationEmail",
            "username_reset": "mdbee.users.email.UsernameResetEmail",
            "user_activate": "mdbee.users.email.UserActivateEmail",
            "user_deactivate": "mdbee.users.email.UserDeactivateEmail",
            "invite_contact": "mdbee.users.email.InviteContactEmail"
        }
    ),
    "CONSTANTS": ObjDict({"messages": "mdbee.users.constants.Messages"}),
    "LOGOUT_ON_PASSWORD_CHANGE": True,
    "CREATE_SESSION_ON_LOGIN": True,
    # "SOCIAL_AUTH_TOKEN_STRATEGY": "mdbee.users.social.token.jwt.TokenStrategy",
    "SOCIAL_AUTH_ALLOWED_REDIRECT_URIS": [],
    "HIDE_USERS": True,
    "PERMISSIONS": ObjDict(
        {
            "general": ["mdbee.utils.permissions.IsAuthenticatedOrDebugging", ],
            "activation": ["rest_framework.permissions.AllowAny"],
            "password_reset": ["mdbee.users.permissions.CanResetPassword"],
            "password_reset_confirm": ["rest_framework.permissions.AllowAny"],
            "set_password": ["mdbee.users.permissions.IsCurrentUserSuperAdminAccountAdmin"],
            "username_reset": ["rest_framework.permissions.AllowAny"],
            "username_reset_confirm": ["rest_framework.permissions.AllowAny"],
            "set_username": ["mdbee.users.permissions.CurrentUserOrAdmin"],
            "user_create": ["mdbee.users.permissions.CreateUserPermission"],
            "user_detail": ["mdbee.users.permissions.CanViewUserDetail"],
            "user_delete": ["mdbee.users.permissions.CanDeleteUser"],
            "user_edit": ["mdbee.users.permissions.CanEditUser"],
            "user": ["mdbee.users.permissions.CurrentUserOrAdmin"],
            "user_list": ["mdbee.users.permissions.CanViewUserList"],
            "token_create": ["rest_framework.permissions.AllowAny"],
            "token_destroy": ["rest_framework.permissions.IsAuthenticated"],
            'signup': ["rest_framework.permissions.AllowAny"],
            'logout': ["rest_framework.permissions.IsAuthenticated"],
            'create_system_user': ["mdbee.users.permissions.CreateUserPermission"],
            'case_role_permission': ["rest_framework.permissions.IsAuthenticated"],
        }
    ),
}

SETTINGS_TO_IMPORT = ["TOKEN_MODEL", ]


class Settings:
    def __init__(self, default_settings, explicit_overriden_settings: dict = None):
        if explicit_overriden_settings is None:
            explicit_overriden_settings = {}

        overriden_settings = (
            getattr(django_settings, DJOSER_SETTINGS_NAMESPACE, {})
            or explicit_overriden_settings
        )

        self._load_default_settings()
        self._override_settings(overriden_settings)
        self._init_settings_to_import()

    def _load_default_settings(self):
        for setting_name, setting_value in default_settings.items():
            if setting_name.isupper():
                setattr(self, setting_name, setting_value)

    def _override_settings(self, overriden_settings: dict):
        for setting_name, setting_value in overriden_settings.items():
            value = setting_value
            if isinstance(setting_value, dict):
                value = getattr(self, setting_name, {})
                value.update(ObjDict(setting_value))
            setattr(self, setting_name, value)

    def _init_settings_to_import(self):
        for setting_name in SETTINGS_TO_IMPORT:
            value = getattr(self, setting_name)
            if isinstance(value, str):
                setattr(self, setting_name, import_string(value))


class LazySettings(LazyObject):
    def _setup(self, explicit_overriden_settings=None):
        self._wrapped = Settings(default_settings, explicit_overriden_settings)


settings = LazySettings()


def reload_djoser_settings(*args, **kwargs):
    global settings
    setting, value = kwargs["setting"], kwargs["value"]
    if setting == DJOSER_SETTINGS_NAMESPACE:
        settings._setup(explicit_overriden_settings=value)


setting_changed.connect(reload_djoser_settings)
