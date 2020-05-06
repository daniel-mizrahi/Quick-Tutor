from django.forms import ModelForm, ModelChoiceField
from django.contrib.auth.models import User
from .models import Request, Course

class RequestForm(ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'course', 'length', 'message', 'location']
    
    # Remaining code subsets the course query set to only the student's courses
    # Source: https://stackoverflow.com/questions/34270099/django-modelform-overriding-init
    student_courses = Course.objects.all()
    course = ModelChoiceField(queryset = student_courses)

    def __init__(self, user, *args, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.student_courses = user.profile.student.courses.all()
            self.fields['course'].queryset = self.student_courses
