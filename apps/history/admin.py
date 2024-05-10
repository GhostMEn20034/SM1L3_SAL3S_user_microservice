from django.contrib import admin

from .models import RecentlyViewedItem

@admin.register(RecentlyViewedItem)
class RecentlyViewedItemAdmin(admin.ModelAdmin):
    pass
