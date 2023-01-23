import pytest
from django.test import Client
from datetime import datetime
from NoccSchedulerApp.models import Tour, Location
from NoccSchedulerApp.forms import TourFormDetails, TourFormFeedbackDetails
from NoccSchedulerApp.views import main, tour_details, view_calendar, archives, login_user, logout_user, ask_for_feedback

client=Client()

def test_user_login(client, django_user_model):
    login_data = dict (
        f_username = "test_user",
        f_password = "test_pass")
    user = django_user_model.objects.create_user(username=login_data['f_username'], password=login_data['f_password'])
    response = client.post("/login/", login_data )
    # Use this:
    #client.force_login(user)
    # Or this:
    #client.login(username=login_data['username'], password=login_data['password'])
    assert response.status_code == 302


def test_user_login_fail(client, django_user_model):
    login_data = dict (
        f_username = "test_user",
        f_password = "test_pass")
    user = django_user_model.objects.create_user(username=login_data['f_username'], password='wrong_pass')
    response = client.post("/login/", login_data )
    # Use this:
    #client.force_login(user)
    # Or this:
    #client.login(username=login_data['username'], password=login_data['password'])
    #response = client.get('/archives')
    assert response.status_code == 200

def test_check_admin_access(auth_user):
    response = auth_user.get('/archives/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_add_new_tour(client):
    #create test data
    location = Location.objects.create(location='Krakow')
    print(location)
    form_data = dict(location=location.id, nocc_person_assigned='Test Person', tour_name='Test tour', date= "2024-01-13", start_time="15:30", end_time='16:00',
    nocc_personnel_required='Yes', requestor_name='Thomas', requestor_email='thomas@mail.com', poc_name= 'John', poc_email= 'john@akamai.com', cc_this_request_to= 'john2@akamai.com',
    division= 'Compute', attendees_akamai= '2', attendees_guests= '2', customer_or_group_name= 'test', customers_website='website.com', type_of_customers= 'Manufacturing', 
    category= 'investors', opportunity_ID= '0', comment= 'aaaa', id='9b31ede7-36ba-44cb-b492-c493fd99daaa')

    response = client.post('/new-tour/', form_data)
    #data = response.data
    data_in_db = Tour.objects.all().first()
    print(data_in_db)

    assert data_in_db.poc_name == form_data['poc_name']