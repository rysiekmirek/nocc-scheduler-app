import pytest
from django.test import Client

@pytest.fixture
def auth_user(Client, django_user_model):
    client = Client()
    login_data = dict (
        f_username = "test_user",
        f_password = "test_pass")
    user = django_user_model.objects.create_user(username=login_data['f_username'], password=login_data['f_password'])
    auth_user = client.post("/login/", login_data )
    return auth_user
