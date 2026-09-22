import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestAuthenticationAPI:
    def test_user_registration(self, api_client):
        url = reverse('accounts:register')
        payload = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewUserPass123!',
            'password_confirm': 'NewUserPass123!',
            'first_name': 'New',
            'last_name': 'Developer',
            'role': 'MEMBER'
        }
        response = api_client.post(url, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert response.data['user']['username'] == 'newuser'
        assert response.data['user']['email'] == 'newuser@example.com'

    def test_user_login_token_obtain(self, api_client, member_user_1):
        url = reverse('accounts:login')
        payload = {
            'username': member_user_1.username,
            'password': 'MemberPassword123!',
        }
        response = api_client.post(url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['username'] == member_user_1.username
        assert response.data['user']['role'] == 'MEMBER'

    def test_login_invalid_credentials(self, api_client, member_user_1):
        url = reverse('accounts:login')
        payload = {
            'username': member_user_1.username,
            'password': 'WrongPassword!',
        }
        response = api_client.post(url, payload, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh(self, api_client, member_user_1):
        login_url = reverse('accounts:login')
        login_res = api_client.post(login_url, {
            'username': member_user_1.username,
            'password': 'MemberPassword123!',
        }, format='json')
        refresh_token = login_res.data['refresh']

        refresh_url = reverse('accounts:token_refresh')
        refresh_res = api_client.post(refresh_url, {'refresh': refresh_token}, format='json')
        assert refresh_res.status_code == status.HTTP_200_OK
        assert 'access' in refresh_res.data

    def test_me_endpoint_requires_auth(self, api_client):
        url = reverse('accounts:current_user_profile')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_endpoint_authenticated(self, api_client, auth_headers_member_1, member_user_1):
        url = reverse('accounts:current_user_profile')
        response = api_client.get(url, **auth_headers_member_1)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == member_user_1.username
        assert response.data['email'] == member_user_1.email

    def test_change_password(self, api_client, auth_headers_member_1, member_user_1):
        url = reverse('accounts:change_password')
        payload = {
            'old_password': 'MemberPassword123!',
            'new_password': 'UpdatedPassword456!',
        }
        response = api_client.post(url, payload, format='json', **auth_headers_member_1)
        assert response.status_code == status.HTTP_200_OK

        # Verify old password no longer works
        login_url = reverse('accounts:login')
        old_login = api_client.post(login_url, {
            'username': member_user_1.username,
            'password': 'MemberPassword123!',
        }, format='json')
        assert old_login.status_code == status.HTTP_401_UNAUTHORIZED

        # Verify new password works
        new_login = api_client.post(login_url, {
            'username': member_user_1.username,
            'password': 'UpdatedPassword456!',
        }, format='json')
        assert new_login.status_code == status.HTTP_200_OK
