# Quick Tutor
### A service to you, from *Pseudocode*
Contributing software engineers: Nate Hunter, Alex Kim, Daniel Mizrahi, Ben Phillips, Shivaen Ramshetty

University of Virginia &emsp; | &emsp; CS 3240 &emsp; | &emsp; Spring 2020

## Overview
Quick Tutor is a web app for connecting students and tutors on Grounds.
It's like Uber for tutors: when a student needs help, they simply send out a request,
which tutors can instantly accept. Easy peasy lemon-squeezy!
No more waiting around, helplessly stuck on an integral that a tutor could walk you through in minutes.
And tutors, no more waiting around to make an extra buck!

## Organization
The website is organized into three main sections.
#### Login
Users start out at a sleek homepage, from which they can view info about the site,
sign up/log in, update account settings, and finally proceed to one of two modes: student or tutor.
Courses need to be entered in settings before a user can submit a request as a student.
#### Student
In student mode, a user can create a request for help under "Request A Tutor".
A user may only have one request at a time.
Upon submission, the request will pop up on tutors' pages, where they can accept it.
Under "My Request", students can check the status of their request, view their tutor's information,
time a session, cancel their request, or rate their tutor.
#### Tutor
In tutor mode, a user can view requests for help and accept one under "View Open Requests".
Under "My Request", tutors can check the status of their request, view their student's information,
complete a session, drop their request, or rate their student.

## Flow
The flow of a request from start to finish works like this:
### Normal request flow
#### 1. Student submits request
Everything starts when the student submits a request form under "Request A Tutor".
This makes the request open for all tutors to view.
Tutors for the course listed in the request will also be notified by email.
#### 2. Tutor accepts request
When a tutor clicks "Accept" on a request under "View Open Requests",
they are instantly paired with the student who requested help.
One of the two (typically the tutor) can reach out and arrange to meet the other via email or phone.
Contact info is shared both ways via email and the "My Request" page.
The student's location is also shared to make meeting up easier.
#### 3. Student starts timing
When the tutor arrives, the student can press a button under "My Request" to start a timer.
#### 4. Tutor completes request
When the tutoring session is done, the tutor can press a button under "My Request"
to stop the timer and complete the request.
The time elapsed can be used by the tutor to calculate pay (outside the app).
Students and tutors can also rate each other at this point. (Hopefully five stars!)
#### 5. Student ends request
After the student has paid the tutor (outside the app), they can press a button to end the request.
That deletes the request, so that the student and tutor can make/accept new requests.
That's all there is to it.
### Abort mission!
#### 1. Student cancels request
A student can cancel their request at any time. This gets rid of the request altogether.
#### 2. Tutor drops request
A tutor can drop their request after accepting it.
This reopens the request to be viewable to other tutors.

## Citations
- Snippets of code were borrowed from the project that our TA Sam McBroom did for this course,
  for implementing AJAX requests and testing HTTP requests and form submissions. Thanks Sam!
  His team's repo: https://github.com/Sammcb/TEMPS
- Code from Google was used for interfacing with their Maps API
  (https://developers.google.com/maps/documentation/javascript/examples/map-geolocation)
  and their login API (https://developers.google.com/identity/sign-in/web/sign-in)
- This project was built on Django and uses Bootstrap
- It runs on Heroku here: https://cs3240-pseudocode.herokuapp.com/
- Finally, thank you to Prof. Mark Sherriff for teaching this course
  and facilitating this project for us!

## We hope you enjoy!
Sincerely, *Team Pseudocode*
