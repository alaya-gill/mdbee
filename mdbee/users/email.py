from django.contrib.auth.tokens import default_token_generator
from templated_mail.mail import BaseEmailMessage

from mdbee.users import utils
from mdbee.users.conf import settings


class ActivationEmail(BaseEmailMessage):
    template_name = "email/activation.html"

    def get_context_data(self):
        # ActivationEmail can be deleted
        context = super().get_context_data()

        user = context.get("user")
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = settings.ACTIVATION_URL.format(**context)
        return context


class ConfirmationEmail(BaseEmailMessage):
    template_name = "email/confirmation.html"


class PasswordResetEmail(BaseEmailMessage):
    template_name = "email/password_reset.html"

    def get_context_data(self):
        # PasswordResetEmail can be deleted
        context = super().get_context_data()

        user = context.get("user")
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = settings.PASSWORD_RESET_CONFIRM_URL.format(**context)
        return context


class PasswordChangedConfirmationEmail(BaseEmailMessage):
    template_name = "email/password_changed_confirmation.html"


class UsernameChangedConfirmationEmail(BaseEmailMessage):
    template_name = "email/username_changed_confirmation.html"


class UsernameResetEmail(BaseEmailMessage):
    template_name = "email/username_reset.html"

    def get_context_data(self):
        context = super().get_context_data()

        user = context.get("user")
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = settings.USERNAME_RESET_CONFIRM_URL.format(**context)
        return context

class ActivationSetPasswordEmail(BaseEmailMessage):
    template_name = "email/activation_set_password.html"

    def get_context_data(self):
         # PasswordResetEmail can be deleted
        context = super().get_context_data()

        user = context.get("user")
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = settings.PASSWORD_RESET_CONFIRM_URL.format(**context)
        return context


class UserActivateEmail(BaseEmailMessage):
    template_name = "email/user_activation.html"

    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        return context

class UserDeactivateEmail(BaseEmailMessage):
    template_name = "email/user_deactivation.html"

    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        return context

class InviteContactEmail(BaseEmailMessage):
    template_name = "email/invitation.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["url"] = settings.SIGNUP_URL.format(**context)
        return context
