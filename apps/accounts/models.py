from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from .managers import AccountManager


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
