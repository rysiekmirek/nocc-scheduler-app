import pytest
from django.urls import reverse
from datetime import datetime
from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib import messages
from django.contrib.messages import get_messages
from NoccSchedulerApp.models import Tour, Location
from NoccSchedulerApp.forms import TourFormDetails, TourFormFeedbackDetails
from NoccSchedulerApp.views import main, tour_details, view_calendar, archives, login_user, logout_user, ask_for_feedback

pytestmark = pytest.mark.django_db

# Helper function to add the middleware to a request
def add_middleware_to_request(request):
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

# Test main view
def test_main_view(rf):
    request = rf.get(reverse('main'))
    response = main(request)
    assert response.status_code == 200

# Test tour_details view
def test_tour_details(request, rf):
    
    # create test data
    location = Location.objects.create(location='Krakow')
    tour = Tour.objects.create(location=location, nocc_person_assigned='Test Person', tour_name='Test tour', date= datetime.now().date(), start_time="15:30", end_time='16:00',
    nocc_personnel_required='Yes', requestor_name='Thomas', requestor_email='thomas@mail.com', poc_name= 'John', poc_email= 'john@akamai.com', cc_this_request_to= 'john2@akamai.com',
    division= 'Compute', attendees_akamai= '2', attendees_guests= '2', customer_or_group_name= 'test', customers_website='website.com', type_of_customers= 'Manufacturing', 
    category= 'investors', opportunity_ID= '0', comment= 'aaaa', id='9b31ede7-36ba-44cb-b492-c493fd99daaa')

    form_data = {'location': location.id, 'tour_name': 'new tour name'}

    request = rf.get(reverse('tour_details', args=['9b31ede7-36ba-44cb-b492-c493fd99daaa']) )

    # test GET request
    request.method = 'GET'
    response = tour_details(request, tour.id)
    assert response.status_code == 200
    assert tour.location.location in str(response.content)
    # print (tour.location.location)
    # print (str(response.content))
    assert tour.tour_name in str(response.content)

    # test POST request with valid form data
    request.method = 'POST'
    request.POST = form_data
    response = tour_details(request, tour.id)
    assert response.status_code == 200
    # messages = list(get_messages(response.wsgi_request))
    # assert 'Tour details updated' in messages
    assert Tour.objects.get(id=tour.id).tour_name == 'new tour name'

    # test POST request with invalid form data
    request.POST = {'location': 'invalid'}
    response = tour_details(request, tour.id)
    assert response.status_code == 200
    assert 'This field is required.' in str(response.content)


# # Test view_calendar view
# def test_view_calendar_view(rf):
#     request = rf.get(reverse('view_calendar'))
#     response = view_calendar(request)
#     assert response.status_code == 200

#     request = rf.post(reverse('view_calendar'), {'month': '1', 'year': '2023'})
#     response = view_calendar(request)
#     assert response.status_code == 200

# # Test archives view
# def test_archives_view(rf):
#     request = rf.get(reverse('archives'))
#     request.user = User.objects.create_user(
#         username='testuser', password='testpassword')
#     add_middleware_to_request(request)

#     response = archives(request)
#     assert response.status_code == 200

# # Test login_user view
# def test_login_user_view(rf):
#     request = rf.get(reverse('login_user'))
#     request.user = AnonymousUser()
#     add_middleware_to_request(request)

#     response = login_user(request)
#     assert response.status_code == 200

#     request = rf.post(reverse('login_user'), {'f_username': 'testuser', 'f_password': 'testpassword'})
#     request.user = AnonymousUser()
#     add_middleware_to_request(request)

#     response = login_user(request)
#     assert response.status_code == 302

# # Test logout_user view
# def test_logout_user_view(rf):
#     request = rf.get(reverse('logout_user'))
#     request.user = User.objects.create_user(
#     username='testuser', password='testpassword')
#     add_middleware_to_request(request)
#     response = logout_user(request)
#     assert response.status_code == 302

# def test_ask_for_feedback_view(rf):
#     request = rf.get(reverse('ask_for_feedback', args=[1]))
#     request.user = User.objects.create_user(
#     username='testuser', password='testpassword')
#     add_middleware_to_request(request)
#     response = ask_for_feedback(request, 1)
#     assert response.status_code == 200

