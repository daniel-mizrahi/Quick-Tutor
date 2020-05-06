from django.urls import path

from . import views

app_name = 'tutor'
urlpatterns = [
    path('tutor_home', views.tutor_home, name='tutor_home'),
    path('tutor_account', views.tutor_account, name='tutor_account'),
    path('tutor_open_requests/', views.TutorRequestsView.as_view(), name='tutor_open_requests'),
    path('tutor_request/', views.tutor_request, name='tutor_request'),
    path('<int:request_id>/take_request/', views.take_request, name='take_request'),
    path('drop_request/', views.drop_request, name="drop_request"),
    path('finish_request/', views.finish_request, name="finish_request")
]