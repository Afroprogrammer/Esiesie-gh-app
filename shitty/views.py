from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from shitty.models import *
from shitty.forms import ProFileForm,DriverForm
# from django.views.decorators import
from django.views.decorators.csrf import csrf_exempt
import arrow
today = arrow.now().date()


def index(request):
    context = {

    }
    return render(request, "shitty/reg_screen.html",context)


@csrf_exempt
def driver_second(request):
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

        form = DriverForm(data=request.POST)
        password = request.POST.get("pass1")
        print(password)
        if form.is_valid():
            print("form is valid")
            profile = form.save(commit=False)
            user = User(username=str(request.POST.get("username")).lower())
            user.set_password(password)
            user.save()
            profile.user = user
            profile.tel = request.POST.get("phone")
            profile.postal_address = request.POST.get("ghana_post_address")
            profile.first_time = True
            profile.save()
            user = authenticate(request, username=request.POST.get("username"), password=password)
            login(request, user)
            print("profile saved")
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
            profile.gps_coord = gps_location
            profile.save()
            gps_location_gps = (gps_location[0],gps_location[1])
            distance = geodesic(tip_off_gps, gps_location_gps).miles * 1.60934
            kilo_cost = distance * unit_rate
            volumetric_cost= profile.num_of_litres * unit_vol_rate
            services_charges = 0.05 * (kilo_cost+volumetric_cost)
            total_cost = services_charges + volumetric_cost + kilo_cost
            request.session['distance_calculated'] = distance
            data = {
                "message": "success",
                "total_cost": "{:.2f}".format(total_cost),
                "name": profile.name,
                "volume": profile.num_of_litres,
                "community":profile.street_name
            }
            return JsonResponse(data)

        if request.POST.get("type") == "final_request":
            print(request.session['distance_calculated'])
            final = Request(profile=Profile.objects.get(user=request.user),
                            total_cost=float(request.POST.get("total_cost")[2:]),
                            volume_cost=request.POST.get("volume_cost"),
                            distance="{:.2f}".format(request.session['distance_calculated'])
                            )
            final.save()
            data = {
                "message": "success"
            }

            return JsonResponse(data)

        if request.POST.get("type") == "biogas_request":
            print("biogas request")
            print(request.POST.get("type_of_toilet"))
            print(request.POST.get("request_comment"))
            BioRequest.objects.create(
                comment=request.POST.get("request_comment"),
                type_of_toilet=request.POST.get("type_of_toilet"),
                user = Profile.objects.get(user=request.user),
                date=today
            )
            print("saved request")
            data = {
                "message":"success"
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
    accepted_requests = Request.objects.filter(profile=user,paid=False)
    if accepted_requests.exists():
        accepted_requests = accepted_requests[0]
    else:
        accepted_requests = None
    print(accepted_requests)
    dislodged_dates = DislodgeDates.objects.filter(requested_user=user)
    print(dislodged_dates)
    context = {
        'user': user,
        "tt":tt,
        "ct":ct,
        "municipals":municipals,
        "dislodged_dates":dislodged_dates,
        "accepted_requests":accepted_requests
    }
    return render(request, "shitty/dashboard.html",context)


@csrf_exempt
def driver_dashboard(request):
    driver = Driver.objects.get(user=request.user)
    requests = Request.objects.filter(disludged=False)
    if request.method == "POST":

        if request.POST.get("type") == "accept_request":
            print("accepting request")
            # print(request.POST.get("id"))
            service_request = Request.objects.get(id=int(request.POST.get("id")))
            service_request.accepted_driver = Driver.objects.get(user=request.user)
            service_request.save()
            tip_off = service_request.profile.municipality.tipping_point.lat_lng.split(",")
            house_location = ast.literal_eval(service_request.profile.gps_coord)

            request.session['house_location1'] = float(house_location[0])
            request.session['house_location2'] = float(house_location[1])
            request.session['tip_off'] = tip_off
            print(request.session['house_location1'],"house location 1")
            print(request.session['house_location2'],"house location 2")
            data = {
                "message": "success",
            }
            return JsonResponse(data)

        if request.POST.get("type") == "submit_forms":
            print("submitting forms")
            vehicle = Vehicle.objects.create(
                vehicle_number=request.POST.get("vehicle_number"),
                capacity=request.POST.get("vehicle_capacity"),
                owner_tel=request.POST.get("owner_tel"),
                owner=request.POST.get("name_of_owner")
            )
            driver.drivers_license = License.objects.get(type=request.POST.get("license_category"))
            driver.issue_date = request.POST.get("issue_date")
            driver.exp_date = request.POST.get("issue_expiry")
            driver.vehicle = vehicle
            driver.first_time = False
            driver.save()
            print("Saved forms")
            data = {
                'message': "success"
            }
            return JsonResponse(data)
    context = {
        "requests":requests,
        "driver":driver
    }
    return render(request, "shitty/driver_dashboard.html",context)

from mapbox import Directions
import ast
@csrf_exempt
def driver_dashboard_two(request):
    driver = Driver.objects.get(user=request.user)
    # print(request.session['house_location'])
    # house_location=ast.literal_eval(request.session['house_location'])
    tip_off=request.session['tip_off'][0]
    # print(tip_off)
    # print(request.session['house_location'])
    # print(request.session['tip_off'])
    if request.method == "POST":
        if request.POST.get("type") == "accept_request":
            print("accepting request")
            # print(request.POST.get("id"))
            service_request = Request.objects.get(id=int(request.POST.get("id")))
            service_request.accepted_driver = Driver.objects.get(user=request.user)
            service_request.save()
            tip_off = service_request.profile.municipality.tipping_point.lat_lng
            print(tip_off,"this is the tip off point")
            request.session['request_object'] = tip_off
            request.session['request_object'] = service_request.profile.gps_coord

            # origin = service_request.profile.gps_coord
            # print(origin)
            # response = service.directions([origin, destination])
            data = {
                "message": "success"
            }
            return JsonResponse(data)

        if request.POST.get("type") == "submit_forms":
            print("submitting forms")
            vehicle = Vehicle.objects.create(
                vehicle_number=request.POST.get("vehicle_number"),
                capacity=request.POST.get("vehicle_capacity"),
                owner_tel=request.POST.get("owner_tel"),
                owner=request.POST.get("name_of_owner")
            )
            driver.drivers_license = License.objects.get(type=request.POST.get("license_category"))
            driver.issue_date = request.POST.get("issue_date")
            driver.exp_date = request.POST.get("issue_expiry")
            driver.vehicle = vehicle
            driver.first_time = False
            driver.save()
            print("Saved forms")
            data = {
                'message': "success"
            }
            return JsonResponse(data)
    context = {
        "driver":driver,
        "tip_off_f": tip_off[0],
        "tip_off_l": tip_off[1],
        # "house_f": house_location[0],
        # "house_l": house_location[1],

    }
    return render(request, "shitty/driver_dashboard_two.html",context)


@csrf_exempt
def paid(request):
    if request.method == "POST":
        _request = Request.objects.get(id=request.POST.get("ref_code"))
        print(_request)
        _request.paid = True
        _request.save()
        DislodgeDates.objects.create(
            requested_user=Profile.objects.get(user=request.user),
            date=today,
            driver=Driver.objects.get(id=_request.accepted_driver.id)
        )
        data = {
                "message": True
        }
        print("saved transactions")
        return JsonResponse(data)
        # todo generate receipt payment


def receipts(request):
    requests = Request.objects.filter(profile=Profile.objects.get(user=request.user),paid=True)
    print(requests)
    context = {
        "requests":requests
    }
    return render(request, "shitty/user_receipts.html",context)


def show_receipt(request,id):
    receipt = Request.objects.get(id=id)
    context = {
        "receipt":receipt,
        "today":today
    }
    return render(request, "shitty/receipt.html",context)


def show_driver_receipt(request,id):
    receipt = Request.objects.get(id=id)
    context = {
        "receipt":receipt,
        "today":today
    }
    return render(request, "shitty/driver_receipt.html",context)


def driver_receipt(request):
    requests = Request.objects.filter(accepted_driver=Driver.objects.get(user=request.user),paid=True)
    context = {
        "requests":requests,
        "today":today
    }
    return render(request, "shitty/driver_receipt.html",context)


def driver_tipping(request,id):
    requests = Request.objects.get(id=id)
    tipping_off = requests.profile.municipality.tipping_point.lat_lng
    print(tipping_off)
    context = {
        "requests":requests,
        "today":today
    }
    return render(request, "shitty/tipping.html",context)


def biogas(request):
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
    return render(request, "shitty/biogas_register.html",context)


def bio_dashboard(request):
    driver = Driver.objects.get(user=request.user)
    requests = Request.objects.filter(disludged=False)
    if request.method == "POST":

        if request.POST.get("type") == "accept_request":
            print("accepting request")
            # print(request.POST.get("id"))
            service_request = Request.objects.get(id=int(request.POST.get("id")))
            service_request.accepted_driver = Driver.objects.get(user=request.user)
            service_request.save()
            tip_off = service_request.profile.municipality.tipping_point.lat_lng.split(",")
            house_location = ast.literal_eval(service_request.profile.gps_coord)

            request.session['house_location1'] = float(house_location[0])
            request.session['house_location2'] = float(house_location[1])
            request.session['tip_off'] = tip_off
            print(request.session['house_location1'],"house location 1")
            print(request.session['house_location2'],"house location 2")
            data = {
                "message": "success",
            }
            return JsonResponse(data)

        if request.POST.get("type") == "submit_forms":
            print("submitting forms")
            vehicle = Vehicle.objects.create(
                vehicle_number=request.POST.get("vehicle_number"),
                capacity=request.POST.get("vehicle_capacity"),
                owner_tel=request.POST.get("owner_tel"),
                owner=request.POST.get("name_of_owner")
            )
            driver.drivers_license = License.objects.get(type=request.POST.get("license_category"))
            driver.issue_date = request.POST.get("issue_date")
            driver.exp_date = request.POST.get("issue_expiry")
            driver.vehicle = vehicle
            driver.first_time = False
            driver.save()
            print("Saved forms")
            data = {
                'message': "success"
            }
            return JsonResponse(data)
    context = {
        "requests":requests,
        "driver":driver
    }
    return render(request, "shitty/biogas_dashboard.html",context)
