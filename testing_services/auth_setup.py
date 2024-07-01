from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test.client import Client

Account = get_user_model()


class AuthSetupService:
    def __init__(self, client: Client):
        self.client = client

    def get_auth_token(self, account: Account, password: str) -> str:
        # Get the login url
        login_url = reverse("token_obtain_pair")

        # Send the email and password to the login url and get the token
        response = self.client.post(
            login_url,
            data={
                'email': account.email,
                'password': password
            },
            format='json'
        )

        # Get access token from response
        return response.data["access"]

