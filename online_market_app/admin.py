from django.contrib import admin

from .models import Role, OnlineMarketUser

# Register your models here.
admin.site.register([Role, OnlineMarketUser])