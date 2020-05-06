from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from quick_tutor.models import Student, Profile, Request
from quick_tutor.forms import RequestForm
from django.urls import reverse
import datetime
import random
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages


# Request form. Note that request parameter refers to HTTP request, not tutor request object
# Thought: when a student sees the Request Form, they can only make a request for a class they already have.
# It's not _really_ a problem if they aren't taking the class that they make a request for,
# so if they force a request for a class they're not taking, such as by creating a fake post request, that's fine.
@login_required
@csrf_exempt
def student_request_form(request):
    # Pressing submit
    if request.method == 'POST':
        form = RequestForm(None, request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.student = Student.objects.get(profile=Profile.objects.get(user=request.user))
            req.save()
            # Send a confirmation email, notify tutors, and show confirmation page
            if req.student.profile.notify_email:
                message =   "Hello, " + request.user.first_name + ",\n\n" +\
                            "Your request was successfully submitted! " +\
                            "Tutors are now able to view your request and accept it. " +\
                            "Happy studying!\n\n" + print_request(req)
                send_email("Request Submitted", message, email_to=[request.user.email])
            notify_tutors(req)
            messages.success(request, "Request successfully submitted!")
            return HttpResponseRedirect(reverse('student:student_request'))
    # Initial form loading; only works if student doesn't have a request
    else:
        if hasattr(request.user.profile.student, 'request'):
            messages.warning(request, "You already have a request!")
            return HttpResponseRedirect(reverse('student:student_request'))
        elif hasattr(request.user.profile.tutor, 'request'):
            messages.warning(request, "You have already accepted a request as a tutor!")
            return HttpResponseRedirect(reverse('tutor:tutor_request'))
        else:
            form = RequestForm(user=request.user)

    #Get position data from AJAX
    current_student = request.user.profile.student
    current_student.latitute = request.POST.get("lat")
    current_student.longitude = request.POST.get("lng")
    current_student.save()

    print(request.POST.get("lat"))
    print(request.POST.get("lng"))
    
    return render(request, 'student/student_request_tutor.html', {'form': form})

@login_required
def student_request_tutor(request):
    template_name = 'student/student_request_tutor.html'
    return render(request, template_name)


@login_required
def student_home(request):
    template_name = 'student/student_home.html'
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
        salutation = "Well, hold my biscuit, if it isn't "
    greeting = salutation + name + "!"
    return render(request, template_name, {'greeting': greeting})

@login_required
def student_request(request):
    if hasattr(request.user.profile.tutor, 'request'):
        messages.warning(request, "You already have a request as a tutor!")
        return HttpResponseRedirect(reverse('tutor:tutor_request'))
    template_name = 'student/student_request.html'
    try:
        this_students_request = Request.objects.get(student=request.user.profile.student)
        state = this_students_request.get_state_display()
        if this_students_request.state == 0 or this_students_request.state == 1:
            elapsed_time = None
        elif this_students_request.state == 2:
            elapsed_time = datetime.datetime.now(tz = datetime.timezone.utc) - this_students_request.time_start
        else:  # this_students_request.state == 3
            elapsed_time = this_students_request.time_stop - this_students_request.time_start
    except Request.DoesNotExist:
        this_students_request = None
        state = None
        elapsed_time = None
    time_to_print = "0:00:00"
    if elapsed_time is not None:
        time_to_print = str(elapsed_time)[:str(elapsed_time).rfind(".")]
    return render(request, template_name,
                  {'request': this_students_request,
                   'state': state,
                   'elapsed_time': time_to_print,})


@login_required
def student_account(request):
    template_name = 'student/student_account.html'
    return render(request, template_name)

@login_required
def cancel_request(request):
    # added: we notify any current tutors if the request is deleted while its taken
    # thought: we probably want to ask for confirmation before deleting a request
    req = request.user.profile.student.request
    # A student should not be able to cancel a request if the request is complete.
    if req.state != Request.RequestStates.COMPLETE:
        if hasattr(req, 'tutor') and req.tutor is not None:
            user = req.tutor.profile.user
            if user.profile.notify_email:
                message = "Hello, " + user.first_name + ",\n\nThe student who requested your help has canceled their request.\n" +\
                            "\nCANCELED:\n" + print_request(req, show_student=True)
                send_email("Request Canceled", message, email_to=[user.email])
        req.delete()
    return HttpResponseRedirect(reverse('student:student_request'))

@login_required
def begin_timing(request):
    to_begin = request.user.profile.student.request
    if to_begin.state == Request.RequestStates.ACCEPTED:
        to_begin.state += 1
        to_begin.time_start = datetime.datetime.now(tz = datetime.timezone.utc)
        to_begin.save()
    return HttpResponseRedirect(reverse('student:student_request'))

@login_required
def confirm_payment(request):
    request.user.profile.student.request.delete()
    # if the user has made a valid rating choice
    try:
        selected_rating = int(request.POST.get("rate"))
        current_rating = request.user.profile.student.request.tutor.rating
        num_ratings = request.user.profile.student.request.tutor.numberOfRatings
        current_rating *= num_ratings
        current_rating += selected_rating
        request.user.profile.student.request.tutor.numberOfRatings += 1
        request.user.profile.student.request.tutor.rating = current_rating / request.user.profile.student.request.tutor.numberOfRatings
        request.user.profile.student.request.tutor.save()
    finally:
        return HttpResponseRedirect(reverse('student:student_request'))


# Sends an email automatically
def send_email(subject, message, email_to = [], email_bcc = []):
    email = EmailMessage(
        subject,
        message + "\n\nYours,\nTeam Pseudocode\n\nSent on " + 
                datetime.datetime.now().strftime("%A, %B %d, %Y at %I:%M:%S %p.\n") +
                "Site: https://cs3240-pseudocode.herokuapp.com/ \n",
        'quicktutorbypseudocode@gmail.com',
        email_to, email_bcc,    # Lists of email strings
    )
    email.send()

# Turns a request into a multiline string
def print_request(req, show_student = False, show_tutor = False):
    message = ("Message: \t" + req.message + "\n") if req.message else ""
    student = ""
    if show_student:
        user = req.student.profile.user
        phone = ("Student phone: \t" + user.profile.phone + "\n") if user.profile.phone else ""
        student = "Student: \t" + str(user.profile) + "\n" +\
                    "Student email: \t" + user.email + "\n" + phone
    tutor = ""
    if show_tutor:
        user = req.tutor.profile.user
        phone = ("Tutor phone: \t" + user.profile.phone + "\n") if user.profile.phone else ""
        tutor = "Tutor: \t\t" + str(user.profile) + "\n" +\
                    "Tutor email: \t" + user.email + "\n" + phone
    return  "------------ Request ------------\n" +\
            student + tutor +\
            "Title: \t\t" + str(req) + "\n" +\
            "Course: \t" + str(req.course) + "\n" +\
            "Length: \t" + str(req.length) + "\n" +\
            message +\
            "Location: \t" + req.location + "\n" +\
            "---------------------------------\n"

# Notify appropriate tutors by email when a request is submitted
def notify_tutors(req):
    tutors = req.course.tutor_set.filter(profile__notify_email=True)
    email_list = []
    for tutor in tutors:
        email_list.append(tutor.profile.user.email)
    message = "Hey there,\n\nA new request just popped up! We think you'd be good for the job. " +\
                "Check it out! \n\nhttps://cs3240-pseudocode.herokuapp.com/ \n\n" + print_request(req)
    send_email("New Request", message, email_bcc=email_list)
    
