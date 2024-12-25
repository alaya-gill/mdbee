from django.contrib.auth import get_user_model

from config import celery_app

User = get_user_model()


@celery_app.task()
def update_user_t_and_c_policy_flag():
    """A pointless Celery task to demonstrate usage."""
    all_users = User.objects.all().update(tandc_policy_agreed=False)


@celery_app.task()
def update_subscription_policy_flag():
    """A pointless Celery task to demonstrate usage."""
    all_users = User.objects.all().update(subscription_policy_agreed=False)
