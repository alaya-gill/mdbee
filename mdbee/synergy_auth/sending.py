from django.utils.translation import ugettext as _
from templated_mail.mail import BaseEmailMessage


class OTPEmail(BaseEmailMessage):
    template_name = "email/otp.html"

    def get_context_data(self):
        # PasswordResetEmail can be deleted
        context = super().get_context_data()

        user = context.get("user")
        return context


class CodeSendingFailed(Exception):
    pass


def send_verification_code_via_email(user, code, class_context):
    user_email_address = getattr(user, 'email', None)
    if not user_email_address:
        raise CodeSendingFailed(_("No e-mail address known"))

    # subject_template = _(
    #     api_settings.EMAIL_SENDER_SUBJECT_OVERRIDE or
    #     _("{code}: Your verification code"))
    # body_template = (
    #     api_settings.EMAIL_SENDER_BODY_OVERRIDE or
    #     _("{code} is the verification code needed for the login."))

    # context = BaseEmailMessage().get_context_data()
    context = {}
    context['user'] = user
    context['code'] = code
    to = [user_email_address]
    OTPEmail(context=context, request=class_context).send(to=to)



    # messages_sent = send_mail(
    #     subject=subject_template.format(code=code),
    #     message=body_template.format(code=code),
    #     from_email=settings.DEFAULT_FROM_EMAIL,
    #     recipient_list=[user_email_address],
    #     fail_silently=True)
    #
    # if not messages_sent:
    #     raise CodeSendingFailed(_("Unable to send e-mail"))


def send_verification_code(user, code, class_context):
    sender = send_verification_code_via_email
    return sender(user, code, class_context)



class FeedbackEmail(BaseEmailMessage):
    template_name = "email/feedback.html"

    def get_context_data(self):
        # PasswordResetEmail can be deleted
        context = super().get_context_data()

        user = context.get("user")
        return context