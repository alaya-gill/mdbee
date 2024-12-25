from django.dispatch import Signal

# New user has registered.
user_registered = Signal(providing_args=["user", "request"])

# User Updated
user_updated = Signal(providing_args=["user", "request"])

# User Deleted
user_deleted = Signal(providing_args=["user", "request"])

# invite contact
user_invite_contact = Signal(providing_args=["user", "request"])

# User has activated his or her account.
user_activated = Signal(providing_args=["user", "request"])

# User has activated his or her account.
otp_generated = Signal(providing_args=["user", "request"])

# User has activated his or her account.
otp_resend_success = Signal(providing_args=["user", "request"])

# User has activated his or her account.
otp_resend_failure = Signal(providing_args=["user", "request"])

# User has activated his or her account.
session_expiry = Signal(providing_args=["user", "request"])


# User has activated his or her account.
user_deactivated = Signal(providing_args=["user", "request"])


# User has activated his or her account.
user_resend_activation = Signal(providing_args=["user", "request"])


# User has activated his or her account.
set_password = Signal(providing_args=["user", "request"])


# User has activated his or her account.
reset_password = Signal(providing_args=["user", "request"])


# User has activated his or her account.
reset_password_confirm = Signal(providing_args=["user", "request"])

# Contact Register
contact_registered = Signal(providing_args=["user", "request"])

save_group_permissions = Signal(providing_args=["user", "request"])

users_signal = Signal(providing_args=["user", "request"])

user_feed_signal = Signal(providing_args=["user", "request"])