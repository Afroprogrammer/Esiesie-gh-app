from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from shitty.models import *
from shitty.forms import ProFileForm
# from django.views.decorators import
from django.views.decorators.csrf import csrf_exempt
def index(request):
    context = {

    }
    return render(request, "shitty/reg_screen.html",context)


def driver_second(request):
    context = {

    }
    return render(request, "shitty/driver_second.html",context)

@csrf_exempt
def user_second(request):
    if request.method == "POST":
        print("post request")
        if request.POST.get("type") == "register":
            username = str(request.POST.get("username")).strip().lower()
            _email = User.objects.filter(email=request.POST.get("email")).exists()
            _username = User.objects.filter(username=username).exists()
            _phone = Profile.objects.filter(phone=request.POST.get("phone")).exists()
            if _email:
                data = {
                    "message": "failure",
                    "info": "A user with this email already exists, please use a different email",
                    "type": "email"
                }
                return JsonResponse(data)

            if _username:
                data = {
                    "message": "failure",
                    "info": "A user with this username already exists,please use a different username",
                    "type": "username"
                }
                return JsonResponse(data)

            if _phone:
                data = {
                    "message": "failure",
                    "info": "A user with this phone number already exists,please use a different phone number",
                    "type": "phone"
                }
                return JsonResponse(data)

            # email = User.objects.filter(email=request.POST.get("email"),profile__phone=request.POST.get("phone"),
            #                             username=username).exists()
            # print(email)
            # if email:
            #     print("hmm email or phone exits in the system")
            #     data = {
            #         "message": "failure",
            #         "info": "A user with either email or phone already exists"
            #     }
            #     return JsonResponse(data)
            form = ProFileForm(data=request.POST)
            password = request.POST.get("pass1")
            print(password)
            if form.is_valid():
                print("form is valid")
                profile = form.save()
                user = User(username=str(request.POST.get("username")).lower(), email=request.POST.get("email"))
                user.set_password(password)
                user.save()
                profile.user = user
                profile.save()
                user = authenticate(request, username=request.POST.get("username"), password=password)
                login(request, user)
                print("profile saved")
                # thread = EmailThread(request.POST.get("email"),profile.name,profile.user.username,profile.phone)
                # thread.start()
                data = {
                    "message": "success"
                }
                return JsonResponse(data)

            else:
                error_list = [form.errors.get(i) for i in form.errors]
                print(error_list)
                data = {
                    "message": "failure",
                    "info": error_list
                }
                return JsonResponse(data)

        if request.POST.get("type") == "login":
            print("a login")
            username = str(request.POST.get("username")).lower()
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            try:
                login(request, user)
                if user is not None:
                    print("hello world i am authenticated")
                    data = {
                        "message": "success"
                    }
                    return JsonResponse(data)
            except Exception as e:
                print("fake cred")
                data = {
                    "message": "failure"
                }

                return JsonResponse(data)

        # if request.POST.get("type") == "forgot":
        #     print("forgot password in session")
        #     checker = User.objects.filter(email=request.POST.get("email"))
        #     if checker.exists():
        #         print("checker exists")
        #         data = str(uuid.uuid4())
        #         reset = EmailRest(uuid=data,username=checker[0].username)
        #         reset.save()
        #         thread = ForgotThread(request.POST.get("email"),checker[0].username,data)
        #         thread.start()
        #         data = {"message": "success"}
        #         return JsonResponse(data)
        #     else:
        #         data = {"message": "failure"}
        #         return JsonResponse(data)

    context = {

    }
    return render(request, "shitty/second.html",context)

import datetime
from geopy.distance import geodesic
@csrf_exempt
def dashboard(request):
    if request.method == "POST":
        if request.POST.get("type") == "request_dislodge":
            print("this is a dislodge request")
            unit_rate = 70.00
            unit_vol_rate = 0.3
            gps_location = request.POST.get("gps_location").split(",")
            profile = Profile.objects.get(user=request.user)
            tip_off = str(profile.municipality.tipping_point.lat_lng).split(",")
            comm = profile.street_name
            tip_off_gps = (tip_off[0],tip_off[1])
            gps_location_gps = (gps_location[0],gps_location[1])
            distance = geodesic(tip_off_gps, gps_location_gps).miles * 1.60934
            print(distance,"distance")
            kilo_cost = distance * unit_rate
            volumetric_cost= profile.num_of_litres * unit_vol_rate
            services_charges = 0.05 * (kilo_cost+volumetric_cost)
            total_cost = services_charges + volumetric_cost + kilo_cost
            # print(kilo_cost,"kilo cost")
            # print(volumetric_cost,"volume cost")
            # print(services_charges,"service charge")
            # print(total_cost,"total cost")
            # print(distance)
            # cost_a = miles
            print(profile.name)
            print(profile.street_name)
            data = {
                "message": "success",
                "total_cost": "{:.2f}".format(total_cost),
                "name": profile.name,
                "volume": profile.num_of_litres,
                "community":profile.street_name
            }
            return JsonResponse(data)







        date = None
        if len(str(request.POST.get("last_date"))) > 2:
            print("somethind dey")
            date = request.POST.get("last_date")
        profile = Profile.objects.get(user=request.user)
        profile.municipality_id = request.POST.get("municipality")
        profile.house_no = request.POST.get("house_no")
        profile.ghana_post = request.POST.get("ghana_post")
        profile.number_of_adult_in_household = request.POST.get("num_adults")
        profile.number_of_children_in_household = request.POST.get("num_children")
        profile.toilet_type_id = request.POST.get("tt")
        profile.ct_id = request.POST.get("ct")
        profile.lc = request.POST.get("len_con")
        profile.wc = request.POST.get("wid_con")
        profile.ed = request.POST.get("eff")
        profile.first_time = False
        profile.num_of_litres = request.POST.get("num_of_litres")
        profile.initial_dislodge = date
        profile.save()
        print(request)
        data = {
            "message": "success"
        }

        return JsonResponse(data)
    user = Profile.objects.get(user=request.user)
    municipals = Municipalities.objects.all()
    tt = Tt.objects.all()
    ct = Ct.objects.all()
    context = {
        'user': user,
        "tt":tt,
        "ct":ct,
        "municipals":municipals
    }
    return render(request, "shitty/dashboard.html",context)


