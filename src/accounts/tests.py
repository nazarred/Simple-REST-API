from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from mock import Mock, patch

from accounts.utils import GetAuthTokenMixin, HunterAPIClient

User = get_user_model()

UNDELIVERABLE_EMAIL = 'sdstsseli@close.io'
CLEARBIT_MOCK_DATA = {'person': {
    'bio': 'some bio',
    'location': 'some location',
    'site': 'https://google.com'
}}


class UserModelTests(TestCase):
    """
    Test the User model and manager.

    """
    user_data = {'email': 'test@mail.com',
                 'password': 'somepassword',
                 'first_name': 'John',
                 'last_name': 'Dou'}

    def test_active_user_creation(self):
        new_user = User.objects.create_user(**self.user_data)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(new_user.is_active)
        self.assertFalse(new_user.is_superuser)

    def test_inactive_user_creation(self):
        new_user = User.objects.create_inactive_user(**self.user_data)
        self.assertEqual(User.objects.count(), 1)
        self.assertFalse(new_user.is_active)
        self.assertFalse(new_user.is_superuser)

    def test_send_activation_email(self):
        new_user = User.objects.create_inactive_user(**self.user_data)
        new_user.send_activation_email()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user_data['email']])

    def test_user_activate(self):
        new_user = User.objects.create_inactive_user(**self.user_data)
        new_user.activate()
        self.assertTrue(new_user.is_active)

    def test_generation_activation_key(self):
        new_user = User.objects.create_inactive_user(**self.user_data)
        new_user.send_activation_email()
        email_inst = mail.outbox[0]
        token_generator = PasswordResetTokenGenerator()
        activation_key = token_generator.make_token(new_user)
        self.assertIn(activation_key, email_inst.body)


class ViewTests(GetAuthTokenMixin, TestCase):

    def setUp(self):
        self.user_data = {'email': 'test@mail.com',
                          'password': 'somepassword',
                          'first_name': 'John',
                          'last_name': 'Dou'}

    @patch('clearbit.Enrichment')
    @patch('accounts.utils.HunterAPIClient.email_verifier')
    def test_success_user_creation(self, mock_email_verifier, clearbit_mock):
        clearbit_mock.find.return_value = None
        mock_email_verifier.return_value = 'deliverable'
        self.user_data['password1'] = self.user_data['password']
        response = self.client.post(reverse('api_accounts:register'),
                                    data=self.user_data)
        self.assertEqual(response.status_code, 201)
        mock_email_verifier.assert_called_with(self.user_data['email'])
        clearbit_mock.find.assert_called_with(email=self.user_data['email'], stream=True)
        self.assertEqual(User.objects.count(), 1)
        for key in self.user_data:
            if key in ['password', 'password1']:
                self.assertNotEqual(response.data.get(key), self.user_data.get(key))
            else:
                self.assertEqual(response.data.get(key), self.user_data.get(key))
                self.assertEqual(response.data.get(key), self.user_data.get(key))

        new_user = User.objects.get(email=self.user_data['email'])
        self.assertFalse(new_user.is_active)
        self.assertFalse(new_user.is_superuser)

    @patch('clearbit.Enrichment')
    @patch('accounts.utils.HunterAPIClient.email_verifier')
    def test_getting_additional_data(self, mock_email_verifier, clearbit_mock):
        clearbit_mock.find.return_value = CLEARBIT_MOCK_DATA
        mock_email_verifier.return_value = 'deliverable'
        self.user_data['password1'] = self.user_data['password']
        response = self.client.post(reverse('api_accounts:register'),
                                    data=self.user_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
        mock_email_verifier.assert_called_with(self.user_data['email'])
        clearbit_mock.find.assert_called_with(email=self.user_data['email'], stream=True)

        user = User.objects.get(email=self.user_data['email'])
        data = CLEARBIT_MOCK_DATA['person']
        self.assertTrue(data)
        self.assertEqual(data.get('location'), user.location)
        self.assertEqual(data.get('bio'), user.bio)
        self.assertEqual(data.get('site'), user.site)

    @patch('accounts.utils.HunterAPIClient.email_verifier')
    def test_undeliverable_email(self, mock_email_verifier):
        """
        Test creation user with undeliverable email.
        Email checks with hunter.io API
        """
        mock_email_verifier.return_value = 'undeliverable'
        self.user_data['password1'] = self.user_data['password']
        response = self.client.post(reverse('api_accounts:register'),
                                    data=self.user_data)
        mock_email_verifier.assert_called_with(self.user_data['email'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 0)
        error_msg = "This email is undeliverable"
        self.assertIn(error_msg, response.data.get('email')[0])

    def test_email_exist(self):
        """
        Test creation user with already exists email
        """
        new_user = User.objects.create_user(**self.user_data)
        self.user_data['password1'] = self.user_data['password']
        response = self.client.post(reverse('api_accounts:register'),
                                    data=self.user_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 1)
        error_msg = 'user with this email already exists.'
        self.assertIn(error_msg, response.data.get('email')[0])

    def test_passwords_not_match(self):
        """
        Test creation user with not matching passwords
        """
        new_user = User.objects.create_user(**self.user_data)
        self.user_data['password1'] = 'badpassword'
        response = self.client.post(reverse('api_accounts:register'),
                                    data=self.user_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 1)
        error_msg = 'Passwords must match'
        self.assertIn(error_msg, response.data.get('password1')[0])

    def test_success_user_activation_view(self):
        new_user = User.objects.create_inactive_user(**self.user_data)
        token_generator = PasswordResetTokenGenerator()
        activation_key = token_generator.make_token(new_user)
        response = self.client.get(reverse('activation_link',
                                           kwargs={
                                               'token': activation_key,
                                               'pk': new_user.pk
                                           }))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/activate.html')
        new_user.refresh_from_db()
        self.assertTrue(new_user.is_active)
        self.assertContains(response, "Your email verified. Account is active")

    def test_bad_user_activation(self):
        """
        Test activation not existing user
        """

        new_user = User.objects.create_inactive_user(**self.user_data)
        token_generator = PasswordResetTokenGenerator()
        activation_key = token_generator.make_token(new_user)
        response = self.client.get(reverse('activation_link',
                                           kwargs={
                                               'token': activation_key,
                                               'pk': 10
                                           }))
        self.assertEqual(response.status_code, 404)
        new_user.refresh_from_db()
        self.assertFalse(new_user.is_active)

    def test_wrong_token_activation(self):
        """
        Test activation with incorrect token
        """
        new_user = User.objects.create_inactive_user(**self.user_data)
        activation_key = 'wrong_string'
        response = self.client.get(reverse('activation_link',
                                           kwargs={
                                               'token': activation_key,
                                               'pk': new_user.pk
                                           }))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/activate.html')
        new_user.refresh_from_db()
        self.assertFalse(new_user.is_active)
        self.assertContains(response, "Can't verified your email. Account not activated")

    def test_user_detail_view(self):
        new_user = User.objects.create_user(**self.user_data)
        # Unauthorized user
        response = self.client.get(reverse('api_accounts:detail', kwargs={'pk': new_user.pk}))
        self.assertEqual(response.status_code, 401)
        # Authorized user
        client = self.get_authorized_client(self.user_data['email'], self.user_data['password'])
        response = client.get(reverse('api_accounts:detail', kwargs={'pk': new_user.pk}))
        self.assertEqual(response.status_code, 200)
        for key in self.user_data:
            if key in ['password']:
                self.assertNotEqual(response.data.get(key), self.user_data.get(key))
            else:
                self.assertEqual(response.data.get(key), self.user_data.get(key))
                self.assertEqual(response.data.get(key), self.user_data.get(key))


class HunterAPIClientTests(TestCase):
    api_key = settings.HUNTER_API_KEY
    email = 'email@com.ua'
    resp_data = {'data': {'result': 'ok'}}

    def setUp(self):
        self.hunter_client = HunterAPIClient(self.api_key)
        self.url = HunterAPIClient.email_verif_url.format(email=self.email, key=self.api_key)
        mock_resp = Mock()
        mock_resp.json = Mock(return_value=self.resp_data)
        mock_resp.status_code = 200
        self.mock_resp = mock_resp

    def test_get_url(self):
        self.assertEqual(self.url, self.hunter_client.get_url(self.email))

    @patch('requests.get')
    def test_get_response_200(self, mock_get):
        mock_get.return_value = self.mock_resp
        response = self.hunter_client.get_response(self.url)
        self.assertEqual(response.json(), self.resp_data)

    @patch('requests.get')
    def test_email_verifier(self, mock_get):
        mock_get.return_value = self.mock_resp
        self.assertEqual(self.hunter_client.email_verifier(self.url), self.resp_data['data']['result'])
