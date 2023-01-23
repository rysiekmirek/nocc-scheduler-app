import pytest
from django.test import Client

@pytest.fixture
def auth_user(django_user_model):
    client = Client()
    login_data = dict (
        f_username = "test_user",
        f_password = "test_pass")
    user = django_user_model.objects.create_user(username=login_data['f_username'], password=login_data['f_password'])
    client.post("/login/", login_data )
    #client.force_login(user)
    return client
