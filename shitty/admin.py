from django.contrib import admin
from shitty.models import *
# Register your models here.


class DriverAdmin(admin.ModelAdmin):
    list_display = ['user','name','postal_address','tel','vehicle']


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','name','municipality','house_no','phone']


admin.site.register(Profile,ProfileAdmin)
admin.site.register(Driver,DriverAdmin)
admin.site.register(Ct)
admin.site.register(Tt)
admin.site.register(Municipalities)
admin.site.register(Vehicle)
admin.site.register(TippingPoints)
admin.site.register(Request)
admin.site.register(License)
admin.site.register(DislodgeDates)
admin.site.register(BioRequest)
