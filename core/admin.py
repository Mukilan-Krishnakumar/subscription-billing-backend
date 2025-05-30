from django.contrib import admin

from core import models

# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Plan)
admin.site.register(models.Subscription)
admin.site.register(models.Invoice)
