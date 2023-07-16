from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField
from django_countries import Countries
from .managers import AccountManager

class EuropeCountries(Countries):
    only = [
        "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR",
        "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
        "SI", "ES", "SE", "UA", "GB"
    ]


class Account(AbstractUser):
    MALE = 'MALE'
    FEMALE = 'FEMALE'

    SEX_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    ]

    username = None
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, blank=True)
    phone_number = PhoneNumberField(blank=True)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ['first_name', 'last_name', ]

    objects = AccountManager()

    def __str__(self):
        return self.email


class Address(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
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
        street = self.street + " " + self.house_number
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
