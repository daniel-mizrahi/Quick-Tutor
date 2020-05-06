from django.urls import path
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

app_name = 'login'
urlpatterns = [
    path('', TemplateView.as_view(template_name="login/index.html"), name='login'),
    path('info/', TemplateView.as_view(template_name="login/info.html"), name='info'),
    path('mode/', TemplateView.as_view(template_name="login/mode.html"), name='mode'),
    path('accounts/', include('allauth.urls')),
    path('profile/', TemplateView.as_view(template_name="login/profile.html"), name='profile'),
    path('update/', views.profile, name='update'),
    path('classes/', views.add_classes, name='classes'),
    path('logout/', views.logout_view, name='logout'),
    path('accessdenied/', views.not_logged_in, name='notloggedin'),
    path('missing/', views.no_classes, name='no_classes'),
    path('notifications/', views.notify, name='notifications'),
    path('privacy/', TemplateView.as_view(template_name="login/privacy.html"), name="privacy"),
]