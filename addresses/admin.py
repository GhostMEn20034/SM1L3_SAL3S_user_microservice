from django.contrib import admin
from .models import Address
from django.contrib.admin import ModelAdmin


@admin.register(Address)
class AddressAdmin(ModelAdmin):
    pass
