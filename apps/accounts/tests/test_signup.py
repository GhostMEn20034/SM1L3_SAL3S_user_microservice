from rest_framework.test import APITestCase
from unittest import mock
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status

Account = get_user_model()

class TestSignup(APITestCase):
    def setUp(self):

        self.user = Account.objects.create_user(
            email="TakenEmail44@gmail.com",
            password="test1234",
            first_name="Hello"
        )

    @mock.patch('apps.verification.tasks.send_code_signup_confirmation.send')
    def test_sign_up_with_correct_data(self, mocked_send_email):
        """User that enter correct data is successfully registered"""
        data = {
            "email": "testsunit44@gmail.com",
            "first_name": "Unit",
            "last_name": "Test",
            "password1": "test1234",
            "password2": "test1234"
        }

        url = reverse("user_signup")

        response = self.client.post(url, data=data, format='json')

        # get created user
        user = Account.objects.get(email=data["email"])

        # Check that the response status is 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the response data contains a token
        self.assertIn('token', response.data)

        # Ensure that user is inactive after registration
        self.assertEqual(user.is_active, False)

        # Check that send_code_signup_confirmation.delay was called once with the user email
        mocked_send_email.assert_called_once_with(data["email"])

    def test_sign_up_with_shorter_password(self):
        """User that enter too short password fails registration"""
        data = {
            "email": "testsunit44@gmail.com",
            "first_name": "Unit",
            "last_name": "Test",
            "password1": "test12",
            "password2": "test12"
        }

        url = reverse("user_signup")

        response = self.client.post(url, data=data, format="json")

        expected_error = {
            "error": "Password must have at least 8 characters"
        }

        # Check that the response status is 400 Bad Request
        self.assertEqual(response.status_code, 400)

        self.assertEqual(response.data, expected_error)

    def test_sign_up_with_different_passwords(self):
        """User that enter different passwords fails registration"""
        data = {
            "email": "testsunit44@gmail.com",
            "first_name": "Unit",
            "last_name": "Test",
            "password1": "test1234",
            "password2": "test12345"
        }

        url = reverse("user_signup")

        response = self.client.post(url, data=data, format="json")

        expected_error = {
            "error": "Passwords do not match"
        }

        # Check that the response status is 400 Bad Request
        self.assertEqual(response.status_code, 400)

        self.assertEqual(response.data, expected_error)

    def test_sign_up_with_missing_first_name(self):
        """User that miss first name fails registration"""
        data = {
            "email": "testsunit44@gmail.com",
            "first_name": "",
            "last_name": "Test",
            "password1": "test1234",
            "password2": "test12345"
        }

        url = reverse("user_signup")

        response = self.client.post(url, data=data, format="json")

        # Check that the response status is 400 Bad Request
        self.assertEqual(response.status_code, 400)

    def test_sign_up_with_invalid_email(self):
        """User that enter invalid email fails registration"""
        data = {
            "email": "wrong_email",
            "first_name": "Unit",
            "last_name": "Test",
            "password1": "test1234",
            "password2": "test12345"
        }

        url = reverse("user_signup")

        response = self.client.post(url, data=data, format="json")

        # Check that the response status is 400 Bad Request
        self.assertEqual(response.status_code, 400)

    def test_signup_with_existing_email(self):
        """If user enter email which already taken, then user fails registration"""
        data = {
            "email": "TakenEmail44@gmail.com",
            "first_name": "Unit",
            "last_name": "Test",
            "password1": "test1234",
            "password2": "test12345"
        }

        url = reverse("user_signup")

        response = self.client.post(url, data=data, format="json")

        # Check that the response status is 400 Bad Request
        self.assertEqual(response.status_code, 400)
