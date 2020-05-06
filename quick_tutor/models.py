from django.db import models
from django.db.models import Model
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

# Course is just a string; i.e. 'CS 3240'. Load list from csv
class Course(Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# Question length; i.e. '15 minutes'
class Length(Model):
    name = models.CharField(max_length=20)
    minutes = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['minutes']


# Profile Model that extends Default User
class Profile(Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    notify_email = models.BooleanField(default=True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile1 = Profile.objects.create(user=instance)
        Student.objects.create(profile=profile1)
        Tutor.objects.create(profile=profile1)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Student(Model):
    # Many students to many courses
    courses = models.ManyToManyField(Course)
    # One student to one Profile
    rating = models.FloatField(default=5.0)
    numberOfRatings = models.IntegerField(default=1)

    #Location of Student
    latitute = models.CharField(max_length=100, null=True)
    longitude = models.CharField(max_length=100, null=True)

    # One student to one Profile
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    def __str__(self):
        return "%s - Student" % str(self.profile)


class Tutor(Model):
    # Many tutors to many courses
    courses = models.ManyToManyField(Course)
    rating = models.FloatField(default=5.0)
    numberOfRatings = models.IntegerField(default=1)
    # One tutor to one Profile
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    def __str__(self):
        return "%s - Tutor" % str(self.profile)


# Complete request; associated with student and tutor
class Request(Model):
    title = models.CharField(max_length=100)
    # One course to many requests
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    # Dropdown for question length
    length = models.ForeignKey(Length, on_delete=models.SET_NULL, null=True)
    message = models.TextField(max_length=1000, blank=True)
    location = models.CharField(max_length=50)

    # there should only be 4 valid states: "open", "accepted", "timing", and "complete"
    # This is an IntegerChoice in order to allow state advancement by incrementing.
    class RequestStates(models.IntegerChoices):
        OPEN = 0, 'Open'
        ACCEPTED = 1, 'Accepted'
        TIMING = 2, 'Timing'
        COMPLETE = 3, 'Complete'
    state = models.IntegerField(
        choices=RequestStates.choices,
        default=RequestStates.OPEN,
    )

    time_start = models.DateTimeField(null=True, blank=True)
    time_stop = models.DateTimeField(null=True, blank=True)
    cost = models.FloatField(default=0, null=True, blank=True)
    # One tutor to one request
    tutor = models.OneToOneField(
        Tutor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    # One student to one request
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.title