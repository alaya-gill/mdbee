from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=255)
    phone_code = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)

    def __str__(self):
        return self.name + '-' + self.country.name


class City(models.Model):
    name = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.PROTECT)

    def __str__(self):
        return self.name + '-' + self.state.name + '-' + self.state.country.name
