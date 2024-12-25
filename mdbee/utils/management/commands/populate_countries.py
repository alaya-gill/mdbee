
import json

from django.core.management.base import BaseCommand

from mdbee.utils.models.country import *


class Command(BaseCommand):
    help = 'Populates Countries,Cities and States'

    def handle(self, *args, **kwargs):
        FILENAME = 'countries.json'
        file = open('./mdbee/'+FILENAME)
        parsed_json = json.loads(file.read())

        self.stdout.write("Cleaning old data.")
        City.objects.all().delete()
        State.objects.all().delete()
        Country.objects.all().delete()

        self.stdout.write("Populating New Data for Countries:")
        for x in parsed_json:
            if 'states' in x.keys():
                c = Country.objects.create(name=x['name'],phone_code=x['phone_code'])
                self.stdout.write(x['name'])
                for key,value in x['states'].items():
                    s = State.objects.create(name=key,country=c)
                    for z in value:
                        City.objects.create(name=z,state=s)

        file.close()

        self.stdout.write("Database has been populated")

