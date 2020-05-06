from django.test import TestCase
from .models import Course, Length, Student, Tutor, Request, Profile
from django.contrib.auth.models import User


class SystemTestCase(TestCase):
    """Test Cases designed to ensure that all tests are working correctly."""
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

        #Request with student Sherriff and tutor Bloomfield
        student_request = Request.objects.create(title="Help with Django",
                                                 course=Course.objects.get(name="CS 3240"),
                                                 length=Length.objects.get(name="30 minutes"),
                                                 message="I'm really struggling with Django right now.",
                                                 location="Thornton Hall",
                                                 student=Student.objects.get(profile=Profile.objects.get(
                                                     user=User.objects.get(username="mark"))),
                                                 tutor=Tutor.objects.get(profile=Profile.objects.get(
                                                     user=User.objects.get(username="aaron"))))

    def test_user_and_profile_instantiation(self):
        user_object = User.objects.get(first_name="Mark", last_name="Sherriff")
        profile_object = Profile.objects.get(user=user_object)
        self.assertEqual("testsherriff@virginia.edu", user_object.email)
        self.assertEqual("434-982-2688", profile_object.phone)

    def test_did_course_list_load(self):
        '''
        Note about this test: This test assumes that you are using the data from the UVA Spring 2020 Semester with all
        courses with the same course mnemonic (e.g. APMA, CS) and course number (e.g. 3100, 3240) as one course.
        This data was taken from Lou's List.
        '''
        self.assertEqual(len(Course.objects.all()), 3072)

    def test_create_request_through_django(self):
        '''
        This tests the creation of a request, but directly through django, instead of through our website
        '''
        test_student = Student.objects.get(profile=Profile.objects.get(user=User.objects.get(first_name="Aaron", last_name="Bloomfield")))
        test_request = Request.objects.create(
            title="Help with Django!",
            course=Course.objects.get(name="CS 3240"),
            length=Length.objects.get(name="15 minutes"),
            message="Django is way too hard for me to understand! (i'm sorry bloomfield i don't mean anything bad)",
            location="Olsson 109",
            student=test_student,
        )
        self.assertEqual(test_request.state,0)
        self.assertEqual(test_request, Request.objects.get(title="Help with Django!"))

    #Test if user is initialized with default latitude and longitude of None
    def test_initial_location(self):
        user_object = User.objects.get(first_name="Mark", last_name="Sherriff")
        profile = Profile.objects.get(user=user_object)
        current_student = profile.student
        current_student.save()
        self.assertEqual(None, current_student.latitute)
        self.assertEqual(None, current_student.longitude)

    #Test whether student geolocation values can be updated
    def test_geolocate_student(self):
        user_object = User.objects.get(first_name="Mark", last_name="Sherriff")
        profile = Profile.objects.get(user=user_object)
        current_student = profile.student
        student_latitude = "38.033554"
        student_longitude = "-78.507980"
        current_student.latitute = student_latitude
        current_student.longitude = student_longitude
        current_student.save()
        self.assertEqual("38.033554", current_student.latitute)
        self.assertEqual("-78.507980", current_student.longitude) 

    #Test whether tutor can access student position when not geolocated
    def test_get_student_location_null(self):
        student_object = User.objects.get(first_name="Mark", last_name="Sherriff")
        tutor_object = User.objects.get(first_name="Aaron", last_name="Bloomfield")
        tutor_profile = Profile.objects.get(user=tutor_object)
        latitude_access = tutor_profile.tutor.request.student.latitute
        longitude_access = tutor_profile.tutor.request.student.longitude
        self.assertEqual(None, latitude_access)
        self.assertEqual(None, longitude_access)
    
    #Test whether tutor can access student position when geolocated
    def test_get_student_location_1(self):
        student_object = User.objects.get(first_name="Mark", last_name="Sherriff")
        tutor_object = User.objects.get(first_name="Aaron", last_name="Bloomfield")
        student_profile = Profile.objects.get(user=student_object)
        student_profile_student = student_profile.student
        student_profile_student.latitute = "38.033554"
        student_profile_student.longitude = "-78.507980"
        student_profile_student.save()
        tutor_profile = Profile.objects.get(user=tutor_object)
        self.assertEqual("38.033554", tutor_profile.tutor.request.student.latitute)
        self.assertEqual("-78.507980", tutor_profile.tutor.request.student.longitude)

    #Test whther tutor can access student postionn when not geolocated
    def test_get_student_location_2(self):
        student_object = User.objects.get(first_name="Mark", last_name="Sherriff")
        tutor_object = User.objects.get(first_name="Aaron", last_name="Bloomfield")
        student_profile = Profile.objects.get(user=student_object)
        student_profile_student = student_profile.student
        student_profile_student.latitute = "0"
        student_profile_student.longitude = "0"
        student_profile_student.save()
        tutor_profile = Profile.objects.get(user=tutor_object)
        self.assertEqual("0", tutor_profile.tutor.request.student.latitute)
        self.assertEqual("0", tutor_profile.tutor.request.student.longitude)

    
    



    