import random
from configparser import ConfigParser
import requests
from faker import Faker

CONFIG_PATH = 'bot_config.ini'

config = ConfigParser()
config.read(CONFIG_PATH)

NMB_OF_USER = int(config.get('settings', 'number_of_users'))
MAX_POSTS = int(config.get('settings', 'max_posts_per_user'))
MAX_LIKES = int(config.get('settings', 'max_likes_per_user'))
MAX_TRY = int(config.get('settings', 'max_try'))
HOSTNAME = config.get('settings', 'hostname')


class APIClient:
    register_url = 'http://%s/api/accounts/register/'
    likes_url = 'http://%s/api/posts/likes/'
    post_create_url = 'http://%s/api/posts/create/'
    activate_url = 'http://%s/activate/{key}/{user_id}/'
    jwt_token_url = 'http://%s/api-token-auth/'

    def __init__(self, hostname):
        self.register_url = self.register_url % hostname
        self.likes_url = self.likes_url % hostname
        self.post_create_url = self.post_create_url % hostname
        self.activate_url = self.activate_url % hostname
        self.jwt_token_url = self.jwt_token_url % hostname

    def post_data(self, url, data, jwt_token=None):
        try:
            if jwt_token:
                headers = {'Authorization': 'JWT ' + jwt_token}
                response = requests.post(url, data, headers=headers)
            else:
                response = requests.post(url, data)
        except requests.exceptions.ConnectionError as error:
            return None
        return response

    def get_jwt_token(self, email, password):
        response = self.post_data(self.jwt_token_url, data={'email': email,
                                                            'password': password})
        return response.json().get('token')

    def create_user(self, data):
        response = self.post_data(self.register_url, data)
        if response.status_code == 201:
            activation_key = response.json().get('activation_key')
            user_id = response.json().get('id')
            if activation_key:
                activated = self.user_activate(activation_key, user_id)
                if activated:
                    return response.json().get('email'), user_id
        return None, None

    def get_activation_url(self, activation_key, user_id):
        return self.activate_url.format(key=activation_key, user_id=user_id)

    def user_activate(self, activation_key, user_id):
        url = self.get_activation_url(activation_key, user_id)
        response = requests.get(url)
        if response.status_code == 200:
            return 'Account is active' in response.text

    def create_post_by_user(self, email, password, post_data):
        jwt_token = self.get_jwt_token(email, password)
        response = self.post_data(self.post_create_url, post_data, jwt_token=jwt_token)
        return response.json().get('id')

    def like_post(self, user_id, post_id, email, password):
        jwt_token = self.get_jwt_token(email, password)
        post_data = {
            'user_id': user_id,
            'post_id': post_id
        }
        response = self.post_data(self.likes_url, post_data, jwt_token=jwt_token)
        return response.json().get('liked')


def run(number_of_users, max_posts_per_user, max_likes_per_user, max_try, hostname):
    faker = Faker()
    client = APIClient(hostname)
    users = []
    post_ids = []
    count, i = 0, 0
    while i < number_of_users:
        user_email = faker.slug() + faker.free_email()
        email, user_id = client.create_user({
            'email': user_email[-40:],
            'password': '1q2w3e',
            'password1': '1q2w3e',
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
        })
        print(email)
        if not email and count < max_try:
            count += 1
            continue
        count = 0
        i += 1
        if email:
            number_of_posts = random.randint(1, max_posts_per_user)
            for _ in range(number_of_posts):
                post_id = client.create_post_by_user(email, '1q2w3e', {'title': faker.text(15),
                                                                       'content': faker.text(),
                                                                       'is_published': True})
                post_ids.append(post_id)
            users.append((email, user_id))
    for email, user_id in users:
        number_of_likes = random.randint(1, max_likes_per_user)
        random.shuffle(post_ids)
        for post_id in post_ids[:number_of_likes]:
            client.like_post(user_id=user_id, post_id=post_id, email=email, password='1q2w3e')


run(NMB_OF_USER, MAX_POSTS, MAX_LIKES, MAX_TRY, HOSTNAME)
