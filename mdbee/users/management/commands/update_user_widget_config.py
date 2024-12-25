from django.core.management.base import BaseCommand

from mdbee.users.models import User


class Command(BaseCommand):
    help = 'Repopulates user widgets'

    def handle(self, *args, **kwargs):
        all_users = User.objects.all()

        for user in all_users:
            user.widgets.all().delete()
            
