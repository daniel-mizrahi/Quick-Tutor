from django.contrib import admin
from .models import Course, Length, Request, Student, Tutor, Profile

# Register your models here.

admin.site.register(Course)
admin.site.register(Length)
admin.site.register(Request)
admin.site.register(Profile)
admin.site.register(Student)
admin.site.register(Tutor)
