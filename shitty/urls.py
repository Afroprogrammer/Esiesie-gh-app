"""shittrain URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import *


app_name="shitty"
urlpatterns = [
    path('',index,name="index"),
    path('user/',user_second,name="user_second"),
    path('driver/',driver_second,name="driver_second"),
    path('dashboard/',dashboard,name="dashboard"),
    path('driver_dashboard/',driver_dashboard,name="driver_dashboard"),
    path('driver_dashboard_two/',driver_dashboard_two,name="driver_dashboard_two"),
    path('paid/',paid,name="paid"),
    path('receipts/',receipts,name="receipts"),
    path('show_receipt/<int:id>/',show_receipt,name="show_receipt"),
    path('show_driver_receipt/<int:id>/',show_driver_receipt,name="show_driver_receipt"),
    path('driver_receipt/',driver_receipt,name="driver_receipt"),
    path('driver_tipping/<int:id>/',driver_tipping,name="driver_tipping"),
    path('biogas/',biogas,name="biogas"),
    path('bio_dashboard/',bio_dashboard,name="bio_dashboard"),
    path('code_of_conduct/',code_of_conduct,name="code_of_conduct"),
]
