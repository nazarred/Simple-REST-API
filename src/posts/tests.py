import json

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from mixer.backend.django import mixer

from .models import Post, Like
from accounts.utils import GetAuthTokenMixin

User = get_user_model()


class LikeModelTest(TestCase):
    """
    Test the Like model

    """

    def test_post_save_signal(self):
        post = mixer.blend(Post)
        self.assertEqual(post.number_of_likes, 0)
        likes = mixer.cycle(5).blend(Like, post=post)
        post.refresh_from_db()
        self.assertEqual(post.number_of_likes, 5)

    def test_post_delete_signal(self):
        post = mixer.blend(Post)
        likes = mixer.cycle(5).blend(Like, post=post)
        like_inst = Like.objects.filter(post=post).last()
        like_inst.delete()
        post.refresh_from_db()
        self.assertEqual(post.number_of_likes, 4)


class PostModelTests(TestCase):
    """
    Test the Post model and manager.

    """

    def test_increment_and_decrement(self):
        post = mixer.blend(Post)
        self.assertEqual(post.number_of_likes, 0)
        post.increment_likes()
        post.refresh_from_db()
        self.assertEqual(post.number_of_likes, 1)
        post.decrement_likes()
        post.refresh_from_db()
        self.assertEqual(post.number_of_likes, 0)

    def test_get_users_who_liked(self):
        post = mixer.blend(Post)
        # create 5 likes for 'post'
        likes = mixer.cycle(5).blend(Like, post=post)
        # create another likes for some other Post instance
        another_likes = mixer.cycle(5).blend(Like)
        self.assertEqual(post.get_users_who_liked().count(), 5)
        user_ids = post.get_users_who_liked().order_by('id').values_list('id', flat=True)
        # get users ids from Like objects
        user_ids_like = [like.user_id for like in likes]
        self.assertEqual(list(user_ids), sorted(user_ids_like))

    def test_get_active_posts(self):
        nmb_of_active_post = 7
        nmb_of_inactive_post = 5
        active_post = mixer.cycle(nmb_of_active_post).blend(Post)
        inactive_post = mixer.cycle(nmb_of_inactive_post).blend(Post, is_published=False)
        self.assertEqual(Post.objects.get_active_posts().count(), nmb_of_active_post)
        self.assertEqual(Post.objects.all().count(), nmb_of_active_post+nmb_of_inactive_post)


class ViewsTests(GetAuthTokenMixin, TestCase):
    user_data = {'email': 'test@mail.com',
                 'password': 'somepassword',
                 'first_name': 'John',
                 'last_name': 'Dou'}

    def setUp(self):
        user = User.objects.create_user(**self.user_data)
        self.post = mixer.blend(Post, user=user)
        # client with JWT in headers
        self.auth_client = self.get_authorized_client(self.user_data['email'], self.user_data['password'])

    def test_like_or_unlike_view(self):
        # Unauthorized user
        response = self.client.post(reverse('api_posts:likes'),
                                    data={
                                        'user_id': self.post.user_id,
                                        'post_id': self.post.id
                                    })
        self.assertEqual(response.status_code, 401)
        # Authorized user
        response = self.auth_client.post(reverse('api_posts:likes'),
                                         data={
                                             'user_id': self.post.user_id,
                                             'post_id': self.post.id
                                         })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('liked'))
        response = self.auth_client.post(reverse('api_posts:likes'),
                                         data={
                                             'user_id': self.post.user_id,
                                             'post_id': self.post.id
                                         })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data.get('liked'))

    def test_like_view_bad_data(self):
        # post with not existing user
        response = self.auth_client.post(reverse('api_posts:likes'),
                                         data={
                                             'user_id': 10,
                                             'post_id': self.post.id
                                         })
        self.assertEqual(response.status_code, 404)

        # post with not existing post
        response = self.auth_client.post(reverse('api_posts:likes'),
                                         data={
                                             'user_id': self.post.user_id,
                                             'post_id': 10
                                         })
        self.assertEqual(response.status_code, 404)

        # post with wrong id type
        response = self.auth_client.post(reverse('api_posts:likes'),
                                         data={
                                             'user_id': self.post.user_id,
                                             'post_id': 'string'
                                         })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('error'))

    def test_like_list_view(self):
        post_likes = mixer.cycle(4).blend(Like, post=self.post)
        another_likes = mixer.cycle(10).blend(Like)
        response = self.client.get(reverse('api_posts:likes_list', kwargs={'pk': self.post.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 4)

    def test_post_list_view(self):
        posts = mixer.cycle(4).blend(Post)
        response = self.client.get(reverse('api_posts:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 5)

    def test_post_detail_view(self):
        response = self.client.get(reverse('api_posts:post_detail', kwargs={'pk': self.post.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('id'), self.post.id)
        self.assertEqual(response.data['user'].get('id'), self.post.user_id)
        self.assertFalse(response.data.get('likes'))

    def test_post_detail_view_with_get_param(self):
        likes = mixer.cycle(5).blend(Like, post=self.post)
        url = reverse('api_posts:post_detail', kwargs={'pk': self.post.id}) + '?likes=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get('likes'))
        self.assertEqual(len(response.data.get('likes')), 5)

    def test_post_create_view(self):
        # Unauthorized user
        response = self.client.post(reverse('api_posts:post_create'),
                                    data={
                                        'title': 'Test post',
                                        'content': 'test post content',
                                        'is_published': True
                                    })
        self.assertEqual(response.status_code, 401)
        # Authorized user
        response = self.auth_client.post(reverse('api_posts:post_create'),
                                         data={
                                             'title': 'Test post',
                                             'content': 'test post content',
                                             'is_published': True
                                         })
        self.assertEqual(response.status_code, 201)
        post = Post.objects.get(title='Test post')
        self.assertEqual(post.user_id, self.post.user_id)
        self.assertEqual(Post.objects.all().count(), 2)

    def test_post_update_view(self):
        title = 'New title'
        data = json.dumps({'title': title})
        # Unauthorized user
        response = self.client.put(reverse('api_posts:post_update', kwargs={'pk': self.post.id}),
                                   data=data, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        # Authorized but not owner
        new_post = mixer.blend(Post)
        response = self.auth_client.put(reverse('api_posts:post_update', kwargs={'pk': new_post.id}),
                                        data=data, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        # Authorized and owner
        response = self.auth_client.put(reverse('api_posts:post_update', kwargs={'pk': self.post.id}),
                                        data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.get(id=self.post.id).title, title)

    def test_post_delete_view(self):
        # Unauthorized user
        response = self.client.delete(reverse('api_posts:post_delete', kwargs={'pk': self.post.id}))
        self.assertEqual(response.status_code, 401)
        # Authorized but not owner
        new_post = mixer.blend(Post)
        response = self.auth_client.delete(reverse('api_posts:post_delete', kwargs={'pk': new_post.id}))
        self.assertEqual(response.status_code, 403)
        # Authorized and owner
        response = self.auth_client.delete(reverse('api_posts:post_delete', kwargs={'pk': self.post.id}))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Post.objects.count(), 1)
