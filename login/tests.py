from django.test import TestCase, Client
from quick_tutor.models import Course, Length, Student, Tutor, Request, Profile
from django.contrib.auth.models import User
from django.urls import reverse

class SystemTestCase(TestCase):
    """Test Cases designed to ensure that all tests are working correctly."""
    # required fixtures for these test cases
    fixtures = ['course_data.json', 'app_data.json', 'times.json']

    def setUp(self):

        # The creation of Sherriff
        Sherriff = User.objects.create_user(username="mark", first_name="Mark",last_name="Sherriff", email="sherriff_fake@virginia.edu")
        Sherriff_profile = Profile.objects.get(user=Sherriff)
        Sherriff_profile.phone = "434-982-2688"
        Sherriff_profile.save()
        Sherriff_tutor = Tutor.objects.get(profile=Sherriff_profile)
        Sherriff_tutor.courses.add(Course.objects.get(name="CS 3240"))
        Sherriff_student = Student.objects.get(profile=Sherriff_profile)
        Sherriff_student.courses.add(Course.objects.get(name="CS 2150"))

        # The creation of Bloomfield
        Bloomfield = User.objects.create_user(username="aaron", first_name="Aaron", last_name = "Bloomfield", email="aaron_fake@virginia.edu")
        Bloomfield_profile = Profile.objects.get(user=Bloomfield)
        Bloomfield_profile.phone = "434-982-2215"
        Bloomfield_profile.save()
        Bloomfield_tutor = Tutor.objects.get(profile=Profile.objects.get(user=Bloomfield))
        Bloomfield_tutor.courses.add(Course.objects.get(name="CS 2150"))
        Bloomfield_student = Student.objects.get(profile=Profile.objects.get(user=Bloomfield))
        Bloomfield_student.courses.add(Course.objects.get(name="CS 3240"))

    def test_user_first_name_edit(self):
        user_object = User.objects.get(first_name="Mark", last_name="Sherriff")
        self.assertEqual("Mark", user_object.first_name)
        user_object.first_name = "Not Mark"
        user_object.save()
        self.assertEqual("Not Mark", user_object.first_name)
        user_object.first_name = "Mark"
        user_object.save()

    def test_user_last_name_edit(self):
        user_object = User.objects.get(first_name="Mark", last_name="Sherriff")
        self.assertEqual("Sherriff", user_object.last_name)
        user_object.last_name = "Sherf"
        user_object.save()
        self.assertEqual("Sherf", user_object.last_name)
        user_object.last_name = "Sherriff"
        user_object.save()
    
    def test_course_addition(self):
        user_object = User.objects.get(first_name="Mark", last_name="Sherriff")
        profile = Profile.objects.get(user=user_object)
        addedStudentCourse = Course.objects.get(name="CS 4774")
        addedTutorCourse = Course.objects.get(name="CS 1111")
        current_student = profile.student
        current_student.courses.add(addedStudentCourse)
        current_student.save()
        current_tutor = profile.tutor
        current_tutor.courses.add(addedTutorCourse)
        current_tutor.save()
        self.assertEqual("CS 4774", current_student.courses.all()[1].name)
        self.assertEqual("CS 1111", current_tutor.courses.all()[0].name)

    def test_profile_phone_edit(self):
        user_object = User.objects.get(first_name="Mark", last_name="Sherriff")
        profile = Profile.objects.get(user=user_object)
        self.assertEqual("434-982-2688", profile.phone)
        profile.phone = "1234567890"
        profile.save()
        self.assertNotEqual("123-456-7890", profile.phone)
        self.assertEqual("1234567890", profile.phone)
        profile.phone = "434-982-2688"
        profile.save()

    def test_get_email(self):
        user_object = User.objects.get(first_name="Mark", last_name="Sherriff")
        self.assertEqual("sherriff_fake@virginia.edu", user_object.email)


class LoginViewTests(TestCase):
    def test_profile(self):
        response = self.client.get(reverse('login:update'))
        self.assertEqual(302, response.status_code) #Redirects to a different url so expect 302
        c = Client()
        resp = c.post(reverse('login:update'))
        self.assertEqual(302, resp.status_code) #Redirects to a different url so expect 302
    
    def test_add_classes(self):
        response = self.client.get(reverse('login:classes'))
        self.assertEqual(302, response.status_code) #Redirects to a different url so expect 302
        c = Client()
        resp = c.post(reverse('login:classes'))
        self.assertEqual(302, resp.status_code) #Redirects to a different url so expect 302
    
    def test_not_logged_in(self):
        response = self.client.get(reverse('login:notloggedin'))
        self.assertEqual(302, response.status_code) #Redirects to a different url so expect 302

    def test_no_classes(self):
        response = self.client.get(reverse('login:no_classes'))
        self.assertEqual(302, response.status_code) #Redirects to a different url so expect 302

    def test_login(self):
        c = Client()
        response = c.get(reverse('login:login'))
        self.assertEqual(200, response.status_code) #Login page

    def test_logout(self):
        c = Client()
        response = c.post(reverse('login:logout'))
        self.assertEqual(302, response.status_code) #Logout redirects back to login page

        