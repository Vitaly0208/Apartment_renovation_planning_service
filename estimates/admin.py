from django.contrib import admin

from .models import Estimate, Material, User

admin.site.register([Estimate, Material, User])
