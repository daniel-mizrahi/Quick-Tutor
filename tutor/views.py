from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from quick_tutor.models import Request
from django.urls import reverse
import datetime
import random
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from student.views import print_request, send_email


# Create your views here.
@login_required
def tutor_home(request):
    template_name = 'tutor/tutor_home.html'
    name = request.user.first_name
    hour = datetime.datetime.now().hour
    salutation = "Hello, "
    if hour >= 17:
        salutation = "Good evening, "
    elif hour >= 12:
        salutation = "Good afternoon, "
    elif hour >= 4:
        salutation = "Good morning, "
    if random.random() < 0.1:
        salutation = "I can scarcely believe my peepers. Howdy, "
    greeting = salutation + name + "!"
    return render(request, template_name, {'greeting': greeting})


class TutorRequestsView(generic.ListView):
    template_name = 'tutor/tutor_open_requests.html'
    context_object_name = 'request_list'

    def get_queryset(self):
        return Request.objects.filter(state=Request.RequestStates.OPEN)


@login_required
def tutor_request(request):
    if(hasattr(request.user.profile.student, 'request')):
        messages.warning(request, "You already have a request as a student!")
        return HttpResponseRedirect(reverse('student:student_request'))
    template_name = 'tutor/tutor_request.html'
    try:
        this_tutors_request = Request.objects.get(tutor=request.user.profile.tutor)
        state = this_tutors_request.get_state_display()
        lat = this_tutors_request.student.latitute
        lng = this_tutors_request.student.longitude
        if this_tutors_request.state == 0 or this_tutors_request.state == 1:
            elapsed_time = None
        elif this_tutors_request.state == 2:
            elapsed_time = datetime.datetime.now(tz=datetime.timezone.utc) - this_tutors_request.time_start
        else:  # this_students_request.state == 3
            elapsed_time = this_tutors_request.time_stop - this_tutors_request.time_start
    except:
        this_tutors_request = None
        state = None
        elapsed_time = None
        lat = None
        lng = None
    time_to_print = "0:00:00"
    if elapsed_time is not None:
        time_to_print = str(elapsed_time)[:str(elapsed_time).rfind(".")]
    return render(request, template_name,
                  {'request': this_tutors_request, 'state': state, 'elapsed_time': time_to_print, 'lat': lat,
                   'lng': lng})


@login_required
def tutor_account(request):
    template_name = 'tutor/tutor_account.html'
    return render(request, template_name)


''' 
IMPORTANT NOTE: the parameter, request, refers to an http request. request_id refers to
the primary key of the Request object we specified in quick_tutor.models!
'''


@login_required
def take_request(request, request_id):
    tutor_to_be = request.user.profile.tutor
    taken_request = Request.objects.get(pk=request_id)
    if hasattr(tutor_to_be, 'request'):
        return render(request, 'tutor/tutor_open_requests.html', {
            'request_list': Request.objects.all(),
            'error_message': "You're already tutoring a student right now."
        })
    elif hasattr(request.user.profile.student, 'request'):
        return render(request, 'tutor/tutor_open_requests.html', {
            'request_list': Request.objects.all(),
            'error_message': "You're already looking for a tutor right now."
        })
    elif taken_request.tutor:
        return render(request, 'tutor/tutor_open_requests.html', {
            'request_list': Request.objects.all(),
            'error_message': "That request has already been taken!"
        })
    else:
        taken_request.tutor = tutor_to_be
        taken_request.state = Request.RequestStates.ACCEPTED
        tutor_to_be.save()
        taken_request.save()
        if taken_request.student.profile.notify_email:
            user = taken_request.student.profile.user
            message = "Hi, " + user.first_name + ",\n\nA tutor has accepted your request! See details below:\n\n" + \
                      print_request(taken_request, show_tutor=True)
            send_email("Request Accepted", message, email_to=[user.email])
        if taken_request.tutor.profile.notify_email:
            user = taken_request.tutor.profile.user
            message = "Hi, " + user.first_name + ",\n\nYou successfully accepted a request! " + \
                      "We know you will be a big help. See details below:\n\n" + \
                      print_request(taken_request, show_student=True)
            send_email("Request Accepted", message, email_to=[user.email])
        return HttpResponseRedirect(reverse('tutor:tutor_request'))


@login_required
def drop_request(request):
    to_drop = request.user.profile.tutor.request
    if (to_drop.state == Request.RequestStates.ACCEPTED or to_drop.state == Request.RequestStates.TIMING):
        if to_drop.student.profile.notify_email:
            user = to_drop.student.profile.user
            message = "Hello, " + user.first_name + ",\n\nYour tutor has dropped your request." + \
                      " It is currently open for other tutors to view and accept.\n\nDROPPED:\n" + \
                      print_request(to_drop, show_tutor=True)
            send_email("Request Dropped", message, email_to=[user.email])
        to_drop.tutor = None
        to_drop.state = Request.RequestStates.OPEN
        to_drop.save()
    return HttpResponseRedirect(reverse('tutor:tutor_request'))
    # else return an error message


@login_required
def finish_request(request):
    to_finish = request.user.profile.tutor.request
    if (to_finish.state == Request.RequestStates.TIMING):
        to_finish.state += 1
        to_finish.time_stop = datetime.datetime.now(tz=datetime.timezone.utc)
        to_finish.save()
    try:
        selected_rating = int(request.POST.get("rate"))
        current_rating = request.user.profile.tutor.request.student.rating
        num_ratings = request.user.profile.tutor.request.student.numberOfRatings
        current_rating *= num_ratings
        current_rating += selected_rating
        request.user.profile.tutor.request.student.numberOfRatings += 1
        request.user.profile.tutor.request.student.rating = current_rating / request.user.profile.tutor.request.student.numberOfRatings
        request.user.profile.tutor.request.student.save()
    finally:
        return HttpResponseRedirect(reverse('tutor:tutor_request'))
