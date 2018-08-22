from django.urls import reverse
from django.conf import settings

import requests
import clearbit
from requests import HTTPError
from rest_framework.test import APIClient


class GetAuthTokenMixin(object):
    """
    Used in test for JWT authentication.
    Get JWT token for user and add this token in headers
    """
    def get_authorized_client(self, email, password):
        response = self.client.post(reverse('jwt_auth'),
                                    data={
                                        'email': email,
                                        'password': password
                                    })
        token = response.data.get('token')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        return client


def get_additional_info(email):
    """
    get additional info by email for user
    """
    clearbit.key = settings.CLEARBIT_KEY
    try:
        lookup = clearbit.Enrichment.find(email=email, stream=True)
    except HTTPError:
        return None
    if lookup:
        person_data = lookup['person']
        if person_data:
            bio = person_data.get('bio')
            location = person_data.get('location')
            site = person_data.get('site')
            data = {
                'bio': bio,
                'location': location,
                'site': site
            }
            return data


class HunterAPIClient(object):
    """
    Client for working with hunter.io API
    """
    # endpoint
    email_verif_url = 'https://api.hunter.io/v2/email-verifier?email={email}&api_key={key}'

    def __init__(self, api_key):
        self.api_key = api_key

    def get_url(self, email):
        return self.email_verif_url.format(email=email, key=self.api_key)

    def email_verifier(self, email):
        url = self.get_url(email)
        response = self.get_response(url)
        if response:
            data = response.json().get('data')
            return data.get('result') if data else None

    def get_response(self, url):
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError as error:
            return None
        if response.status_code == 200:
            return response


def get_hunter_client():
    return HunterAPIClient(settings.HUNTER_API_KEY)





