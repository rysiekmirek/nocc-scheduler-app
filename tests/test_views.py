import pytest
from django.test import Client

client=Client()

@pytest.mark.django_db
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
    #response = client.get('/archives')
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