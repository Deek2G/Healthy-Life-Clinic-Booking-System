from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime, timedelta
from .models import *
from django.contrib import messages
from .forms import AppointmentForm, ContactForm, SubscriptionForm
from django.core.mail import send_mail

def index(request):
    return render(request, "index.html",{})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            user_name = form.cleaned_data['name']  # Assuming you have a 'name' field

            # Send a thank you email
            send_mail(
                'Thank you for contacting us',
                f'Dear {user_name},\n\nThank you for your message. We will get back to you shortly.\n\nBest regards,\nDr.Mhel Biol',
                'mhel@example.com',  # Replace with your "from" email address
                [user_email],
                fail_silently=False,
            )
            # Handle form submission, like sending an email
            messages.success(request, "Thank you for your message.")
            return redirect('index')
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})

def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']

            # Send a confirmation email
            send_mail(
                'Subscription Confirmation',
                'Thank you for subscribing to our newsletter!',
                'your_email@example.com',  # Replace with your "from" email address
                [user_email],
                fail_silently=False,
            )

            messages.success(request, "Thank you for subscribing to our newsletter.")
            return redirect('index')  # Redirect to a relevant page
    else:
        form = SubscriptionForm()

    return render(request, 'footer.html', {'form': form})

def about(request):
    return render(request, 'about.html')

def booking(request):
    # Calling 'validWeekday' Function to Loop days you want in the next 21 days:
    weekdays = validWeekday(22)

    # Only show the days that are not full:
    validateWeekdays = isWeekdayValid(weekdays)

    # # Doctors for each service
    # doctors = {
    #     "General Practioner": ["Dr. Mhel Biol"],
    #     "Family Medicine Doctor": ["Dr. Ervin Cantila"],
    #     "Pediatrician": ["Dr. Josh Nisperos"]
    # }

    if request.method == 'POST':
        service = request.POST.get('service')
        day = request.POST.get('day')
        doctor = request.POST.get('doctor')  # Capture the selected doctor

        if not service or not doctor:
            messages.success(request, "Please Select A Service and Doctor!")
            return redirect('booking')

        # Store day, service, and doctor in django session:
        request.session['day'] = day
        request.session['service'] = service
        request.session['doctor'] = doctor

        return redirect('bookingSubmit')

    return render(request, 'booking.html', {
        'weekdays': weekdays,
        'validateWeekdays': validateWeekdays,
    })


def bookingSubmit(request):
    user = request.user
    times = [
        "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "1:00 PM", "1:30 PM", "2:00 PM", "2:30 PM", "3:00 PM", "3:30 PM", "4:00 PM", "4:30 PM", "5:00 PM", "5:30 PM"
    ]
    today = datetime.now()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime

    # Get stored data from django session:
    day = request.session.get('day')
    service = request.session.get('service')
    doctor = request.session.get('doctor')  # Get the selected doctor

    # Only show the time of the day that has not been selected before:
    hour = checkTime(times, day)
    if request.method == 'POST':
        time = request.POST.get("time")
        date = dayToWeekday(day)

        if service and doctor:
            if minDate <= day <= maxDate:
                if date in ['Monday', 'Wednesday', 'Friday']:
                    if Appointment.objects.filter(day=day).count() < 11:
                        if Appointment.objects.filter(day=day, time=time).count() < 1:
                            Appointment.objects.get_or_create(
                                user=user,
                                service=service,
                                doctor=doctor,  # Save the selected doctor
                                day=day,
                                time=time,
                            )
                            messages.success(request, "Appointment Saved!")
                            return redirect('index')
                        else:
                            messages.success(request, "The Selected Time Has Been Reserved Before!")
                    else:
                        messages.success(request, "The Selected Day Is Full!")
                else:
                    messages.success(request, "The Selected Date Is Incorrect")
            else:
                messages.success(request, "The Selected Date Isn't In The Correct Time Period!")
        else:
            messages.success(request, "Please Select A Service and Doctor!")

    return render(request, 'bookingSubmit.html', {
        'times': hour,
    })



def userPanel(request):
    user = request.user
    appointments = Appointment.objects.filter(user=user).order_by('day', 'time')
    return render(request, 'userPanel.html', {
        'user':user,
        'appointments':appointments,
    })

def userUpdate(request, id):
    appointment = Appointment.objects.get(pk=id)
    userdatepicked = appointment.day
    #Copy  booking:
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')

    #24h if statement in template:
    delta24 = (userdatepicked).strftime('%Y-%m-%d') >= (today + timedelta(days=1)).strftime('%Y-%m-%d')
    #Calling 'validWeekday' Function to Loop days you want in the next 21 days:
    weekdays = validWeekday(22)

    #Only show the days that are not full:
    validateWeekdays = isWeekdayValid(weekdays)
    

    if request.method == 'POST':
        service = request.POST.get('service')
        day = request.POST.get('day')

        #Store day and service in django session:
        request.session['day'] = day
        request.session['service'] = service

        return redirect('userUpdateSubmit', id=id)


    return render(request, 'userUpdate.html', {
            'weekdays':weekdays,
            'validateWeekdays':validateWeekdays,
            'delta24': delta24,
            'id': id,
        })

def userUpdateSubmit(request, id):
    user = request.user
    times = [
        "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "1:00 PM", "1:30 PM", "2:00 PM", "2:30 PM", "3:00 PM", "3:30 PM", "4:00 PM", "4:30 PM", "5:00 PM", "5:30 PM"
    ]
    today = datetime.now()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime

    day = request.session.get('day')
    service = request.session.get('service')
    
    #Only show the time of the day that has not been selected before and the time he is editing:
    hour = checkEditTime(times, day, id)
    appointment = Appointment.objects.get(pk=id)
    userSelectedTime = appointment.time
    if request.method == 'POST':
        time = request.POST.get("time")
        date = dayToWeekday(day)

        if service != None:
            if day <= maxDate and day >= minDate:
                if date == 'Monday' or date == 'Wednesday' or date == 'Friday':
                    if Appointment.objects.filter(day=day).count() < 11:
                        if Appointment.objects.filter(day=day, time=time).count() < 1 or userSelectedTime == time:
                            AppointmentForm = Appointment.objects.filter(pk=id).update(
                                user = user,
                                service = service,
                                day = day,
                                time = time,
                            ) 
                            messages.success(request, "Appointment Edited!")
                            return redirect('index')
                        else:
                            messages.success(request, "The Selected Time Has Been Reserved Before!")
                    else:
                        messages.success(request, "The Selected Day Is Full!")
                else:
                    messages.success(request, "The Selected Date Is Incorrect")
            else:
                    messages.success(request, "The Selected Date Isn't In The Correct Time Period!")
        else:
            messages.success(request, "Please Select A Service!")
        return redirect('userPanel')


    return render(request, 'userUpdateSubmit.html', {
        'times':hour,
        'id': id,
    })

def staffPanel(request):
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=31)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime
    # Only show the Appointments 21 days from today
    items = Appointment.objects.filter(day__range=[minDate, maxDate]).order_by('day', 'time')

    return render(request, 'staffPanel.html', {
        'items': items,
    })

def delete_appointment(request, appointment_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to delete this appointment.")
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.delete()
    return redirect('staffPanel')

def edit_appointment(request, appointment_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to edit this appointment.")

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('staffPanel')
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'edit_appointment.html', {'form': form})


def dayToWeekday(x):
    z = datetime.strptime(x, "%Y-%m-%d")
    y = z.strftime('%A')
    return y

def validWeekday(days):
    #Loop days you want in the next 21 days:
    today = datetime.now()
    weekdays = []
    for i in range (0, days):
        x = today + timedelta(days=i)
        y = x.strftime('%A')
        if y == 'Monday' or y == 'Wednesday' or y == 'Friday':
            weekdays.append(x.strftime('%Y-%m-%d'))
    return weekdays
    
def isWeekdayValid(x):
    validateWeekdays = []
    for j in x:
        if Appointment.objects.filter(day=j).count() < 10:
            validateWeekdays.append(j)
    return validateWeekdays

def checkTime(times, day):
    #Only show the time of the day that has not been selected before:
    x = []
    for k in times:
        if Appointment.objects.filter(day=day, time=k).count() < 1:
            x.append(k)
    return x

def checkEditTime(times, day, id):
    #Only show the time of the day that has not been selected before:
    x = []
    appointment = Appointment.objects.get(pk=id)
    time = appointment.time
    for k in times:
        if Appointment.objects.filter(day=day, time=k).count() < 1 or time == k:
            x.append(k)
    return x

def cancelAppointment(request, appointment_id):
    # Get the appointment or return 404 if it doesn't exist
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if the user owns the appointment
    if appointment.user != request.user:
        return HttpResponseForbidden("You cannot cancel this appointment.")
    
    # Delete the appointment
    appointment.delete()
    messages.success(request, "Appointment cancelled successfully.")
    return redirect('userPanel')