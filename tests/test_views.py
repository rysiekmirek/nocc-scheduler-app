import pytest
from django.test import TestCase
from django.urls import reverse
from django.test import RequestFactory as rf
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from NoccSchedulerApp.models import Tour, Location
from NoccSchedulerApp.forms import TourFormDetails, TourFormFeedbackDetails
from NoccSchedulerApp.views import main, tour_details, view_calendar, archives, login_user, logout_user, ask_for_feedback



@pytest.mark.django_db
class TestExample:
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

# # Test tour_details view
# def test_tour_details_view(rf):
#     request = rf.get(reverse('tour_details', args=[1]))
#     request.user = User.objects.create_user(
#         username='testuser', password='testpassword')
#     add_middleware_to_request(request)

#     response = tour_details(request, 1)
#     assert response.status_code == 200

#     request = rf.post(reverse('tour_details', args=[1]), {'field1': 'value1'})
#     request.user = User.objects.create_user(
#         username='testuser', password='testpassword')
#     add_middleware_to_request(request)

#     response = tour_details(request, 1)
#     assert response.status_code == 302

# # Test view_calendar view
# def test_view_calendar_view(rf):
#     request = rf.get(reverse('view_calendar'))
#     response = view_calendar(request)
#     assert response.status_code == 200

#     request = rf.post(reverse('view_calendar'), {'month': '1', 'year': '2022'})
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

