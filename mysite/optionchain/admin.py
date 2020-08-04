from django.contrib import admin
from .models import Option, OptionPrice

# Register your models here.
# Source: https://stackoverflow.com/questions/26312219/operationalerror-no-such-column-django
admin.site.register(Option)
admin.site.register(OptionPrice)