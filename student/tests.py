from quick_tutor.models import Course, Length, Student, Tutor, Request, Profile
from quick_tutor.forms import RequestForm
from .views import student_request_tutor, student_request_form, begin_timing, confirm_payment, cancel_request
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
from django.contrib.auth.models import User
# Create your tests here.

class StudentTestCase(TestCase):
    """Test Cases designed to ensure that the student app is working correctly."""
    # required fixtures for these test cases
    fixtures = ['course_data.json', 'app_data.json', 'times.json']

    def setUp(self):
        # The creation of Sherriff
        Sherriff = User.objects.create_user(username="mark", first_name="Mark", last_name="Sherriff",
                                            email="testsherriff@virginia.edu")
        Sherriff_profile = Profile.objects.get(user=Sherriff)
        Sherriff_profile.phone = "434-982-2688"
        Sherriff_profile.notify_email = False
        Sherriff_profile.save()
        Sherriff_tutor = Tutor.objects.get(profile=Sherriff_profile)
        Sherriff_tutor.courses.add(Course.objects.get(name="CS 3240"))
        Sherriff_student = Student.objects.get(profile=Sherriff_profile)
        Sherriff_student.courses.add(Course.objects.get(name="CS 2150"))

        # The creation of Bloomfield
        Bloomfield = User.objects.create_user(username="aaron", password="bloomboi", first_name="Aaron", last_name="Bloomfield",
                                              email="testaaron@virginia.edu")
        Bloomfield_profile = Profile.objects.get(user=Bloomfield)
        Bloomfield_profile.phone = "434-982-2215"
        Bloomfield_profile.notify_email = False
        Bloomfield_profile.save()
        Bloomfield_tutor = Tutor.objects.get(profile=Profile.objects.get(user=Bloomfield))
        Bloomfield_tutor.courses.add(Course.objects.get(name="CS 2150"))
        Bloomfield_student = Student.objects.get(profile=Profile.objects.get(user=Bloomfield))
        Bloomfield_student.courses.add(Course.objects.get(name="CS 3240"))

    def test_has_courses(self):
        Bloomfield_student = Student.objects.get(profile=Profile.objects.get(user=User.objects.get(username="aaron")))
        self.assertEqual(str(Bloomfield_student.courses.all()), '<QuerySet [<Course: CS 3240>]>')
        self.assertNotEqual(str(Bloomfield_student.courses.all()), '<QuerySet [<Course: CS 9999>]>')

    # Learned test format from this link: https://micropyramid.com/blog/django-unit-test-cases-with-forms-and-views/

    # Testing RequestForm validity
    def test_form_valid(self):
        form = RequestForm(user=User.objects.get(username="aaron"),
                           data={'title': "Help", 'course': Course.objects.get(name="CS 3240"),
                                 'length': Length.objects.get(name="5 minutes"), 'message': "Teach me Sherriff",
                                 'location': "Olsson 120"})
        self.assertTrue(form.is_valid())

    def test_form_invalid_course(self):
        form = RequestForm(user=User.objects.get(username="aaron"),
                           data={'title': "Help", 'course': Course.objects.get(name="CS 2150"),
                                 'length': Length.objects.get(name="5 minutes"), 'message': "Teach me Sherriff",
                                 'location': "Olsson 120"})
        self.assertFalse(form.is_valid())

    def test_form_valid_message_blank(self):
        form = RequestForm(user=User.objects.get(username="aaron"),
                           data={'title': "Help", 'course': Course.objects.get(name="CS 3240"),
                                 'length': Length.objects.get(name="5 minutes"), 'message': "",
                                 'location': "Olsson 120"})
        self.assertTrue(form.is_valid())

    def test_form_invalid_title_blank(self):
        form = RequestForm(user=User.objects.get(username="aaron"),
                           data={'title': "", 'course': Course.objects.get(name="CS 3240"),
                                 'length': Length.objects.get(name="5 minutes"), 'message': "Teach me Sherriff",
                                 'location': "Olsson 120"})
        self.assertFalse(form.is_valid())

    # Testing various pages when logged in (or not logged in) as a student
    def test_home_view(self):
        user_login = self.client.login(email="testaaron@virginia.edu", password="bloomboi")
        self.assertTrue(user_login)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/index.html")

    def test_bad_login(self):
        user_login = self.client.login(email="testaaron@virginia.edu", password="bloombad")
        self.assertFalse(user_login)

    def test_home_view_logged_out(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/index.html")

    def test_student_home_view(self):
        user_login = self.client.login(email="testaaron@virginia.edu", password="bloomboi")
        self.assertTrue(user_login)
        response = self.client.get("/student/student_home/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student/student_home.html")

    def test_student_home_view_logged_out(self):
        response = self.client.get("/student/student_home/")
        self.assertEqual(response.status_code, 302)

    def test_student_request_tutor_view(self):
        user_login = self.client.login(email="testaaron@virginia.edu", password="bloomboi")
        self.assertTrue(user_login)
        response = self.client.get("/student/student_request_tutor/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student/student_request_tutor.html")

    def test_student_request_tutor_view_logged_out(self):
        response = self.client.get("/student/student_home/")
        self.assertEqual(response.status_code, 302)

    def test_no_request_before_submission(self):
        bloomy = User.objects.get(username="aaron")
        self.assertFalse(hasattr(bloomy.profile.student, 'request'))

    def test_submit_bad_request_no_location(self):
        self.assertEqual(Request.objects.count(), 0)
        user_login = self.client.login(email="testaaron@virginia.edu", password="bloomboi")
        self.assertTrue(user_login)
        response = self.client.post("/student/student_request_form/",
                                    {'title': "Help", 'course': Course.objects.get(name="CS 3240").pk,
                                     'length': Length.objects.get(name="5 minutes").pk,
                                     'message': "Teach me Sherriff",
                                     'location': ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Request.objects.count(), 0)

    def test_submit_bad_request_logged_out(self):
        self.assertEqual(Request.objects.count(), 0)
        bloomy = User.objects.get(username="aaron")
        response = self.client.post("/student/student_request_form/",
                                    {'title': "Help", 'course': Course.objects.get(name="CS 3240").pk,
                                     'length': Length.objects.get(name="5 minutes").pk,
                                     'message': "Teach me Sherriff",
                                     'location': "Olsson 120"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Request.objects.count(), 0)

    def test_submit_good_request(self):
        self.assertEqual(Request.objects.count(), 0)
        user_login = self.client.login(email="testaaron@virginia.edu", password="bloomboi")
        self.assertTrue(user_login)
        bloomy = User.objects.get(username="aaron")
        response = self.client.post("/student/student_request_form/",
                                    {'title': "Help", 'course': Course.objects.get(name="CS 3240").pk,
                                     'length': Length.objects.get(name="5 minutes").pk,
                                     'message': "Teach me Sherriff",
                                     'location': "Olsson 120"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Request.objects.count(), 1)



class StudentRequests(TestCase):
    fixtures = ['course_data.json', 'app_data.json', 'times.json']

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=True)
    def setUp(self):

        # Thanks to https://github.com/Sammcb/TEMPS/tree/master/pages for helping me test http requests
        # As well as helping with signing in with google
        User = get_user_model()
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

    def test_view_request_form(self):
        req = RequestFactory().get(reverse("student:student_request_tutor"))
        setattr(req, 'session', 'session')
        messages = FallbackStorage(req)
        setattr(req, '_messages', messages)
        req.user = self.request.user
        resp = student_request_tutor(req)
        self.assertTrue(self.request.user.is_authenticated)
        self.assertEquals(resp.status_code, 200)

    def test_create_request(self):
        student_request = Request.objects.create(title="Help with Django",
                                                 course=Course.objects.get(name="CS 3240"),
                                                 length=Length.objects.get(name="30 minutes"),
                                                 message="I'm really struggling with Django right now.",
                                                 location="Thornton Hall",
                                                 student=Student.objects.get(profile=Profile.objects.get(
                                                     user=User.objects.get(username="aaron"))))
        self.assertEqual(student_request, Request.objects.get(
            student=Student.objects.get(profile=Profile.objects.get(user=User.objects.get(username="aaron")))))

    def test_create_request_view(self):
        self.assertEquals(self.request.user, User.objects.get(username="aaron"))
        form_data = {'title': 'Help with Django',
                     'course': Course.objects.get(name="CS 3240").pk,
                     'length': Length.objects.get(name="30 minutes").pk,
                     'message': "I'm really struggling with Django right now.",
                     'location': 'Thornton Hall', }
        form = RequestForm(self.request.user, form_data)
        self.assertTrue(form.is_valid())
        self.assertTrue(self.request.user.is_authenticated)
        req = RequestFactory().post(reverse('student:student_request_form'), data=form_data)
        setattr(req, 'session', 'session')
        messages = FallbackStorage(req)
        setattr(req, '_messages', messages)
        req.user = self.request.user
        resp = student_request_form(req)
        self.assertTrue(Request.objects.get(
            student=Student.objects.get(profile=Profile.objects.get(user=User.objects.get(username="aaron")))))

    def test_begin_timing_view(self):
        student_request = Request.objects.create(title="Help with Django",
                                                 course=Course.objects.get(name="CS 3240"),
                                                 length=Length.objects.get(name="30 minutes"),
                                                 message="I'm really struggling with Django right now.",
                                                 location="Thornton Hall",
                                                 student=Student.objects.get(profile=Profile.objects.get(
                                                     user=User.objects.get(username="aaron"))),
                                                 tutor=Tutor.objects.get(profile=Profile.objects.get(
                                                     user=User.objects.get(username="mark"))),
                                                 state=Request.RequestStates.ACCEPTED)
        self.assertTrue(Request.objects.get(title="Help with Django"))
        req = RequestFactory().post(reverse('student:begin_timing'))
        setattr(req, 'session', 'session')
        messages = FallbackStorage(req)
        setattr(req, '_messages', messages)
        req.user = self.request.user
        resp = begin_timing(req)
        self.assertEqual(Request.objects.get(title="Help with Django").state, Request.RequestStates.TIMING)

    def test_confirm_payment_view(self):
        student_request = Request.objects.create(title="Help with Django",
                                                 course=Course.objects.get(name="CS 3240"),
                                                 length=Length.objects.get(name="30 minutes"),
                                                 message="I'm really struggling with Django right now.",
                                                 location="Thornton Hall",
                                                 student=Student.objects.get(profile=Profile.objects.get(
                                                     user=User.objects.get(username="aaron"))),
                                                 tutor=Tutor.objects.get(profile=Profile.objects.get(
                                                     user=User.objects.get(username="mark"))),
                                                 state=Request.RequestStates.COMPLETE)
        self.assertTrue(Request.objects.get(title="Help with Django"))
        req = RequestFactory().post(reverse('student:confirm_payment'))
        setattr(req, 'session', 'session')
        messages = FallbackStorage(req)
        setattr(req, '_messages', messages)
        req.user = self.request.user
        resp = confirm_payment(req)
        with self.assertRaises(Request.DoesNotExist):
            Request.objects.get(title="Help with Django")
        with self.assertRaises(Request.DoesNotExist):
            Request.objects.get(student=Student.objects.get(profile=Profile.objects.get(user=User.objects.get(username="aaron"))))
        with self.assertRaises(Request.DoesNotExist):
            Request.objects.get(tutor=Tutor.objects.get(profile=Profile.objects.get(user=User.objects.get(username="mark"))))

    def test_cancel_unaccepted_request_view(self):
        student_request = Request.objects.create(title="Help with Django",
                                                 course=Course.objects.get(name="CS 3240"),
                                                 length=Length.objects.get(name="30 minutes"),
                                                 message="I'm really struggling with Django right now.",
                                                 location="Thornton Hall",
                                                 student=Student.objects.get(profile=Profile.objects.get(
                                                     user=User.objects.get(username="aaron"))))
        self.assertTrue(Request.objects.get(title="Help with Django"))
        req = RequestFactory().post(reverse('student:cancel_request'))
        setattr(req, 'session', 'session')
        messages = FallbackStorage(req)
        setattr(req, '_messages', messages)
        req.user = self.request.user
        resp = cancel_request(req)
        with self.assertRaises(Request.DoesNotExist):
            Request.objects.get(title="Help with Django")
        with self.assertRaises(Request.DoesNotExist):
            Request.objects.get(
                student=Student.objects.get(profile=Profile.objects.get(user=User.objects.get(username="aaron"))))
        with self.assertRaises(Request.DoesNotExist):
            Request.objects.get(
                tutor=Tutor.objects.get(profile=Profile.objects.get(user=User.objects.get(username="mark"))))

    def test_cancel_accepted_request_view(self):
        student_request = Request.objects.create(title="Help with Django",
                                                 course=Course.objects.get(name="CS 3240"),
                                                 length=Length.objects.get(name="30 minutes"),
                                                 message="I'm really struggling with Django right now.",
                                                 location="Thornton Hall",
                                                 student=Student.objects.get(profile=Profile.objects.get(
                                                     user=User.objects.get(username="aaron"))),
                                                 tutor=Tutor.objects.get(profile=Profile.objects.get(
                                                     user=User.objects.get(username="mark"))),
                                                 state=Request.RequestStates.ACCEPTED)
        self.assertTrue(Request.objects.get(title="Help with Django"))
        req = RequestFactory().post(reverse('student:cancel_request'))
        setattr(req, 'session', 'session')
        messages = FallbackStorage(req)
        setattr(req, '_messages', messages)
        req.user = self.request.user
        resp = cancel_request(req)
        with self.assertRaises(Request.DoesNotExist):
            Request.objects.get(title="Help with Django")
        with self.assertRaises(Request.DoesNotExist):
            Request.objects.get(
                student=Student.objects.get(profile=Profile.objects.get(user=User.objects.get(username="aaron"))))
        with self.assertRaises(Request.DoesNotExist):
            Request.objects.get(
                tutor=Tutor.objects.get(profile=Profile.objects.get(user=User.objects.get(username="mark"))))

    # Attempting to cancel a completed request instead of confirming payment should do nothing.
    def test_cannot_cancel_completed_request_view(self):
        student_request = Request.objects.create(title="Help with Django",
                                                 course=Course.objects.get(name="CS 3240"),
                                                 length=Length.objects.get(name="30 minutes"),
                                                 message="I'm really struggling with Django right now.",
                                                 location="Thornton Hall",
                                                 student=Student.objects.get(profile=Profile.objects.get(
                                                     user=User.objects.get(username="aaron"))),
                                                 tutor=Tutor.objects.get(profile=Profile.objects.get(
                                                     user=User.objects.get(username="mark"))),
                                                 state=Request.RequestStates.COMPLETE)
        self.assertTrue(Request.objects.get(title="Help with Django"))
        req = RequestFactory().post(reverse('student:cancel_request'))
        setattr(req, 'session', 'session')
        messages = FallbackStorage(req)
        setattr(req, '_messages', messages)
        req.user = self.request.user
        resp = cancel_request(req)
        self.assertTrue(Request.objects.get(title="Help with Django"))


