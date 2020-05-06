from .views import TutorRequestsView, take_request, drop_request, finish_request
from quick_tutor.models import Course, Length, Student, Tutor, Request, Profile
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.urls import reverse
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.socialaccount.helpers import complete_social_login
# Create your tests here.

class TutorTestCase(TestCase):
    """Test Cases designed to ensure that the tutor app is working correctly."""
    # required fixtures for these test cases
    fixtures = ['course_data.json', 'app_data.json', 'times.json']

    def setUp(self):

        # The creation of Sherriff
        Sherriff = User.objects.create_user(username="mark", first_name="Mark",last_name="Sherriff", email="testsherriff@virginia.edu")
        Sherriff_profile = Profile.objects.get(user=Sherriff)
        Sherriff_profile.phone = "434-982-2688"
        Sherriff_profile.save()
        Sherriff_tutor = Tutor.objects.get(profile=Sherriff_profile)
        Sherriff_tutor.courses.add(Course.objects.get(name="CS 3240"))
        Sherriff_student = Student.objects.get(profile=Sherriff_profile)
        Sherriff_student.courses.add(Course.objects.get(name="CS 2150"))

        # The creation of Bloomfield
        Bloomfield = User.objects.create_user(username="aaron", first_name="Aaron", last_name = "Bloomfield", email="testaaron@virginia.edu")
        Bloomfield_profile = Profile.objects.get(user=Bloomfield)
        Bloomfield_profile.phone = "434-982-2215"
        Bloomfield_profile.save()
        Bloomfield_tutor = Tutor.objects.get(profile=Profile.objects.get(user=Bloomfield))
        Bloomfield_tutor.courses.add(Course.objects.get(name="CS 2150"))
        Bloomfield_student = Student.objects.get(profile=Profile.objects.get(user=Bloomfield))
        Bloomfield_student.courses.add(Course.objects.get(name="CS 3240"))

    def test_has_courses(self):
        Bloomfield_tutor = Tutor.objects.get(profile=Profile.objects.get(user=User.objects.get(username="aaron")))
        self.assertEqual(str(Bloomfield_tutor.courses.all()), '<QuerySet [<Course: CS 2150>]>')
        self.assertNotEqual(str(Bloomfield_tutor.courses.all()),'<QuerySet [<Course: CS 9999>]>')

class TutorRequest(TestCase):
    fixtures = ['course_data.json', 'app_data.json', 'times.json']

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=True)
    def setUp(self):
        User = get_user_model()

        # Thanks to https://github.com/Sammcb/TEMPS/tree/master/pages for helping me test http requests
        # As well as helping with signing in with google
        factory = RequestFactory()
        self.request = factory.get('/google/login/callback/')
        self.request.user = AnonymousUser()
        SessionMiddleware().process_request(self.request)
        MessageMiddleware().process_request(self.request)
        user = User(username='aaron', email='testaaron@virginia.edu')
        account = SocialAccount(user=user, provider='Gmail', uid='123')
        sociallogin = SocialLogin(user=user, account=account)
        complete_social_login(self.request, sociallogin)
        self.assertTrue(self.request.user.is_authenticated)

        # The creation of Sherriff
        Sherriff = User.objects.create_user(username="mark", first_name="Mark",
                                            last_name="Sherriff", email="testsherriff@virginia.edu")
        Sherriff.set_password("sherriff's password")
        Sherriff_profile = Profile.objects.get(user=Sherriff)
        Sherriff_profile.phone = "434-982-2688"
        Sherriff_profile.save()
        Sherriff_tutor = Tutor.objects.get(profile=Sherriff_profile)
        Sherriff_tutor.courses.add(Course.objects.get(name="CS 3240"))
        Sherriff_student = Student.objects.get(profile=Sherriff_profile)
        Sherriff_student.courses.add(Course.objects.get(name="CS 2150"))

        # The creation of Bloomfield

        Bloomfield = User.objects.get(username="aaron")
        Bloomfield_profile = Profile.objects.get(user=Bloomfield)
        Bloomfield_profile.phone = "434-982-2215"
        Bloomfield_profile.save()
        Bloomfield_tutor = Tutor.objects.get(profile=Profile.objects.get(user=Bloomfield))
        Bloomfield_tutor.courses.add(Course.objects.get(name="CS 2150"))
        Bloomfield_student = Student.objects.get(profile=Profile.objects.get(user=Bloomfield))
        Bloomfield_student.courses.add(Course.objects.get(name="CS 3240"))

    def test_view_request_list(self):
        req = RequestFactory().get(reverse("tutor:tutor_open_requests"))
        setattr(req, 'session', 'session')
        messages = FallbackStorage(req)
        setattr(req, '_messages', messages)
        req.user = self.request.user
        resp = TutorRequestsView.as_view()(req)
        self.assertTrue(self.request.user.is_authenticated)
        self.assertEquals(resp.status_code, 200)

    def test_accept_request_view(self):
        student_request = Request.objects.create(title="Help with Linux",
                                                 course=Course.objects.get(name="CS 2150"),
                                                 length=Length.objects.get(name="30 minutes"),
                                                 message="What is a 'C++'?",
                                                 location="Olsson Hall",
                                                 student=Student.objects.get(profile=Profile.objects.get(
                                                     user=User.objects.get(username="mark"))))
        self.assertTrue(Request.objects.get(title="Help with Linux"))
        req = RequestFactory().post(reverse('tutor:take_request', args=[student_request.pk]))
        setattr(req, 'session', 'session')
        messages = FallbackStorage(req)
        setattr(req, '_messages', messages)
        req.user = self.request.user
        resp = take_request(req, student_request.pk)
        self.assertEqual(Request.objects.get(title="Help with Linux").state, Request.RequestStates.ACCEPTED)

    def test_drop_request_view(self):
        student_request = Request.objects.create(title="Help with Linux",
                                                 course=Course.objects.get(name="CS 2150"),
                                                 length=Length.objects.get(name="30 minutes"),
                                                 message="What is a 'C++'?",
                                                 location="Olsson Hall",
                                                 student=Student.objects.get(profile=Profile.objects.get(
                                                     user=User.objects.get(username="mark"))),
                                                 tutor=Tutor.objects.get(profile=Profile.objects.get(
                                                     user=User.objects.get(username="aaron"))),
                                                 state=Request.RequestStates.ACCEPTED
                                                 )
        self.assertTrue(Request.objects.get(title="Help with Linux"))
        req = RequestFactory().post(reverse('tutor:drop_request'))
        setattr(req, 'session', 'session')
        messages = FallbackStorage(req)
        setattr(req, '_messages', messages)
        req.user = self.request.user
        resp = drop_request(req)
        student_request = Request.objects.get(title="Help with Linux")
        self.assertEqual(student_request, Request.objects.get(student=Student.objects.get(profile=Profile.objects.get(user=User.objects.get(username="mark")))))
        with self.assertRaises(Request.DoesNotExist):
            Request.objects.get(tutor=Tutor.objects.get(profile=Profile.objects.get(user=User.objects.get(username="aaron"))))

    def test_finish_request_view(self):
        student_request = Request.objects.create(title="Help with Linux",
                                                 course=Course.objects.get(name="CS 2150"),
                                                 length=Length.objects.get(name="30 minutes"),
                                                 message="What is a 'C++'?",
                                                 location="Olsson Hall",
                                                 student=Student.objects.get(profile=Profile.objects.get(
                                                     user=User.objects.get(username="mark"))),
                                                 tutor=Tutor.objects.get(profile=Profile.objects.get(
                                                     user=User.objects.get(username="aaron"))),
                                                 state=Request.RequestStates.TIMING
                                                 )
        self.assertTrue(Request.objects.get(title="Help with Linux"))
        req = RequestFactory().post(reverse('tutor:finish_request'))
        setattr(req, 'session', 'session')
        messages = FallbackStorage(req)
        setattr(req, '_messages', messages)
        req.user = self.request.user
        resp = finish_request(req)
        self.assertEqual(Request.objects.get(title="Help with Linux").state, Request.RequestStates.COMPLETE)