from django_countries.fields import CountryField
from django_countries import Countries
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model


Account = get_user_model()

class EuropeCountries(Countries):
    only = [
        "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR",
        "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
        "SI", "ES", "SE", "UA", "GB"
    ]


class Address(models.Model):
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    country = CountryField(countries=EuropeCountries)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = PhoneNumberField()
    city = models.CharField(max_length=50)
    region = models.CharField(blank=True, max_length=50)
    street = models.CharField(max_length=75)
    house_number = models.CharField(max_length=75)
    apartment_number = models.CharField(blank=True, max_length=75)
    postal_code = models.CharField(max_length=75)

    class Meta:
        verbose_name_plural = "Addresses"

    def format_address(self):
        name = self.first_name + " " + self.last_name
        street = self.house_number + " " + self.street
        if self.apartment_number:
            street += ", " + self.apartment_number

        city = self.city
        region = self.region
        postal_code = self.postal_code
        country = self.country.name

        address = name + " " + street
        address += " " + city + " " + region + " " + postal_code if region else " " + city + " " + postal_code
        address += " " + country.upper()

        return address

    def __str__(self):
        return self.format_address()
