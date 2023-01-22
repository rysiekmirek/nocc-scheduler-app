import pytest
from django.test import Client

client=Client()

@pytest.mark.django_db
def test_user_login(client, django_user_model):
    login_data = dict (
        username = "test_user",
        password = "test_pass")
    user = django_user_model.objects.create_user(username=login_data['username'], password=login_data['password'])
    response = client.post("/login/", login_data )
    # Use this:
    #client.force_login(user)
    # Or this:
    #client.login(username=login_data['username'], password=login_data['password'])
    #response = client.get('/archives')
    assert response.status_code == 200