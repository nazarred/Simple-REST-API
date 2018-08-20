from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
import clearbit

from accounts.utils import GetAuthTokenMixin

User = get_user_model()

UNDELIVERABLE_EMAIL = 'sdstsseli@close.io'
EMAIL_FOR_CLEARBIT = 'steli@close.io'



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

    def test_success_user_creation(self):
        self.user_data['password1'] = self.user_data['password']
        response = self.client.post(reverse('api_accounts:register'),
                                    data=self.user_data)
        self.assertEqual(response.status_code, 201)
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

    def test_getting_additional_data(self):
        self.user_data['password1'] = self.user_data['password']
        self.user_data['email'] = EMAIL_FOR_CLEARBIT
        response = self.client.post(reverse('api_accounts:register'),
                                    data=self.user_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
        clearbit.key = settings.CLEARBIT_KEY
        lookup = clearbit.Enrichment.find(email=EMAIL_FOR_CLEARBIT, stream=True)
        user = User.objects.get(email=EMAIL_FOR_CLEARBIT)
        data = lookup['person']
        self.assertTrue(data)
        self.assertEqual(data.get('location'), user.location)
        self.assertEqual(data.get('bio'), user.bio)
        self.assertEqual(data.get('site'), user.site)

    def test_undeliverable_email(self):
        """
        Test creation user with undeliverable email.
        Email checks with hunter.io API
        """
        self.user_data['password1'] = self.user_data['password']
        self.user_data['email'] = UNDELIVERABLE_EMAIL
        response = self.client.post(reverse('api_accounts:register'),
                                    data=self.user_data)
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
