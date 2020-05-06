from django.urls import path

from . import views

app_name = 'student'
urlpatterns = [
    path('student_home/', views.student_home, name='student_home'),
    path('student_request/', views.student_request, name='student_request'),
    path('student_request_tutor/', views.student_request_tutor, name='student_request_tutor'),
    path('student_account/', views.student_account, name='student_account'),
    path('student_request_form/', views.student_request_form, name='student_request_form'),
    path('cancel_request/', views.cancel_request, name="cancel_request"),
    path('begin_timing/', views.begin_timing, name="begin_timing"),
    path('confirm_payment/', views.confirm_payment, name="confirm_payment"),
]