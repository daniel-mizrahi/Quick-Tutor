from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from quick_tutor.models import Request, Student, Profile, Course
from quick_tutor.forms import RequestForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib import messages
from django.test import Client

@login_required
def profile(request):
    #First Name
    if request.POST.get('first_name'):
        current_profile = request.user
        current_profile.first_name = request.POST.get('first_name')
        current_profile.save()

    #Last Name
    if request.POST.get('last_name'):
        current_profile = request.user
        current_profile.last_name = request.POST.get('last_name')
        current_profile.save()

    #Phone number
    if request.POST.get('phone'):
        current_profile = request.user.profile
        current_profile.phone = request.POST.get('phone')
        current_profile.save()
        
    if request.method == "POST":
        messages.success(request, "Information Saved")

    return render(request, 'login/update.html')

@login_required
def add_classes(request):
    #CoursesTaking
    error = False 

    classes = Course.objects.all()
    if request.POST.get('CoursesTaking'):
        addedCourseName = request.POST.get('CoursesTaking')
        if Course.objects.filter(name=addedCourseName).count() == 1:
            addedCourse = Course.objects.get(name=addedCourseName)
            current_student = request.user.profile.student
            current_student.courses.add(addedCourse)
            current_student.save()
        else:
            error = True
            messages.error(request, "Class Not Found")

    #RemoveCoursesTaking
    if request.POST.get('CoursesTaking') and request.POST.get('StudentRemove'):
        deletedCourseName = request.POST.get('CoursesTaking')
        if Course.objects.filter(name=addedCourseName).count() == 1:
            deletedCourse = Course.objects.get(name=deletedCourseName)
            current_student = request.user.profile.student
            current_student.courses.remove(deletedCourse)
            current_student.save()

    #CoursesHelping
    if request.POST.get('CoursesHelping'):
        addedCourseName = request.POST.get('CoursesHelping')
        if Course.objects.filter(name=addedCourseName).count() == 1:
            addedCourse = Course.objects.get(name=addedCourseName)
            current_tutor = request.user.profile.tutor
            current_tutor.courses.add(addedCourse)
            current_tutor.save()
        else:
            error = True
            messages.error(request, "Class Not Found")

    #RemoveClassTutor
    if request.POST.get('CoursesHelping') and request.POST.get('TutorRemove'):
        deletedCourseName = request.POST.get('CoursesHelping')
        if Course.objects.filter(name=addedCourseName).count() == 1:
            deletedCourse = Course.objects.get(name=deletedCourseName)
            current_tutor = request.user.profile.tutor
            current_tutor.courses.remove(deletedCourse)
            current_tutor.save()

    if request.method == "POST" and not error:
        messages.success(request, "Information Saved")

    return render(request, 'login/classes.html', {'classes': classes})


#Need to be logged in
def not_logged_in(request):
    messages.warning(request, "Must be logged in to visit")
    return redirect('login:login')

#Classes could not be found
@login_required
def no_classes(request):
    messages.error(request, "Must have student classes to request a Tutor")
    return redirect('login:classes')

#Notification Changes
@login_required
def notify(request):
    if request.user.profile.notify_email:
        profile = request.user.profile
        profile.notify_email = False
        profile.save()
        messages.warning(request, 'You will not receive notifications')
    else:
        profile = request.user.profile
        profile.notify_email = True
        profile.save()
        messages.success(request, 'You will receive notifications')
    return redirect('login:profile')

#log user out
@login_required
def logout_view(request):
    messages.success(request, "Successfully logged out")
    if request.method == 'POST':
        logout(request)
        return redirect('login:login')
    
