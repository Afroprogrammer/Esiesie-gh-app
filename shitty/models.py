from django.db import models
from django.contrib.auth.models import User


class Municipalities(models.Model):
    name = models.CharField(max_length=100,blank=True,null=True)
    tipping_point = models.ForeignKey('TippingPoints',on_delete=models.DO_NOTHING,blank=True,null=True)

    def __str__(self):
        return self.name


class Tt(models.Model):
    name = models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return self.name


class Ct(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class DislodgeDates(models.Model):
    date = models.DateField(blank=True,null=True)
    driver = models.ForeignKey('Driver',on_delete=models.DO_NOTHING,blank=True,null=True)
    done = models.BooleanField(default=False)

    def __str__(self):
        return str(self.date.isoformat())

class TippingPoints(models.Model):
    name = models.CharField(max_length=100,blank=True,null=True)
    lat_lng = models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING,blank=True,null=True)
    name = models.CharField(max_length=100,blank=True,null=True)
    municipality = models.ForeignKey(Municipalities,on_delete=models.DO_NOTHING,blank=True,null=True)
    house_no = models.CharField(max_length=100,blank=True,null=True)
    ghana_post = models.CharField(max_length=100,blank=True,null=True)
    number_of_adult_in_household = models.IntegerField(blank=True,null=True)
    number_of_children_in_household = models.IntegerField(blank=True,null=True)
    street_name = models.CharField(max_length=100,blank=True,null=True)
    toilet_type = models.ForeignKey(Tt,on_delete=models.DO_NOTHING,blank=True,null=True)
    gps_coord = models.CharField(max_length=100,blank=True,null=True)
    ct = models.ForeignKey(Ct,on_delete=models.DO_NOTHING,blank=True,null=True)
    lc = models.FloatField(blank=True,null=True)
    wc = models.FloatField(blank=True,null=True)
    ed = models.FloatField(blank=True,null=True)
    phone = models.CharField(max_length=100,blank=True,null=True)
    first_time = models.BooleanField(default=True)
    dis_dates = models.ManyToManyField(DislodgeDates,blank=True)
    initial_dislodge = models.DateField(blank=True,null=True)
    num_of_litres = models.FloatField(blank=True,null=True)

    def __str__(self):
        return self.name


class License(models.Model):
    type = models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return self.type


class Vehicle(models.Model):
    vehicle_number = models.CharField(max_length=100,blank=True,null=True)
    capacity = models.FloatField(blank=True,null=True)
    owner = models.CharField(max_length=100,blank=True,null=True)
    address_of_owner = models.CharField(max_length=100,blank=True,null=True)
    owner_tel = models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return self.vehicle_number


class Driver(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING,blank=True,null=True)
    name = models.CharField(max_length=100,blank=True,null=True)
    postal_address = models.CharField(max_length=100,blank=True,null=True)
    tel = models.CharField(max_length=100,blank=True,null=True)
    residential_address = models.CharField(max_length=100,blank=True,null=True)
    drivers_license = models.ForeignKey(License,on_delete=models.DO_NOTHING,blank=True,null=True)
    issue_date = models.DateField(blank=True,null=True)
    exp_date = models.DateField(blank=True,null=True)
    issuing_agency = models.CharField(max_length=100,blank=True,null=True)
    working = models.BooleanField(default=False)
    lat = models.CharField(max_length=100,blank=True,null=True)
    lng = models.CharField(max_length=100,blank=True,null=True)
    bpo = models.FileField(upload_to="bpo/",blank=True,null=True)
    vehicle = models.OneToOneField(Vehicle,blank=True,null=True,on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class Request(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.DO_NOTHING,blank=True,null=True)
    total_cost = models.FloatField(blank=True,null=True)
    volume_cost = models.FloatField(blank=True,null=True)

    def __str__(self):
        return self.profile.name
