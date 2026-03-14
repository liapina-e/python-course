from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import Post, Comment, PostLike, CommentLike
from datetime import datetime, timedelta


class AuthTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.me_url = '/api/auth/me/'

        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_register_user(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')

        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_password_mismatch(self):
        data = self.user_data.copy()
        data['password2'] = 'wrongpass'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_login_user(self):
        User.objects.create_user(username='testuser', password='testpass123')

        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password(self):
        User.objects.create_user(username='testuser', password='testpass123')

        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_endpoint(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=user)

        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')


class PostTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass123')
        self.post_url = '/api/posts/'

        self.post_data = {
            'title': 'Test Post',
            'content': 'Test content for post'
        }

    def test_create_post_unauthenticated(self):
        response = self.client.post(self.post_url, self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.post_url, self.post_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Post')
        self.assertEqual(response.data['author']['username'], 'testuser')

    def test_list_posts(self):
        Post.objects.create(title='Post 1', content='Content 1', author=self.user)
        Post.objects.create(title='Post 2', content='Content 2', author=self.other_user)

        response = self.client.get(self.post_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_update_post_as_author(self):
        post = Post.objects.create(title='Original', content='Content', author=self.user)
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(f'{self.post_url}{post.id}/', {
            'title': 'Updated Title'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_update_post_as_other_user(self):
        post = Post.objects.create(title='Original', content='Content', author=self.user)
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(f'{self.post_url}{post.id}/', {
            'title': 'Updated Title'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_as_author(self):
        post = Post.objects.create(title='To Delete', content='Content', author=self.user)
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(f'{self.post_url}{post.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=post.id).exists())

    def test_delete_post_as_admin(self):
        admin = User.objects.create_superuser(username='admin', password='admin123', email='admin@test.com')
        post = Post.objects.create(title='To Delete', content='Content', author=self.user)

        self.client.force_authenticate(user=admin)
        response = self.client.delete(f'{self.post_url}{post.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_like_post(self):
        post = Post.objects.create(title='Liked Post', content='Content', author=self.other_user)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(f'{self.post_url}{post.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'like added')
        self.assertTrue(PostLike.objects.filter(post=post, user=self.user).exists())

        response = self.client.post(f'{self.post_url}{post.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'like removed')
        self.assertFalse(PostLike.objects.filter(post=post, user=self.user).exists())

    def test_popular_posts(self):
        post1 = Post.objects.create(title='Popular', content='Content', author=self.user)
        post2 = Post.objects.create(title='Not Popular', content='Content', author=self.user)

        user2 = User.objects.create_user(username='user2', password='pass')
        user3 = User.objects.create_user(username='user3', password='pass')

        PostLike.objects.create(post=post1, user=self.user)
        PostLike.objects.create(post=post1, user=user2)
        PostLike.objects.create(post=post1, user=user3)

        response = self.client.get('/api/posts/popular/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], 'Popular')


class CommentTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass123')
        self.post = Post.objects.create(title='Test Post', content='Content', author=self.user)
        self.comment_url = '/api/comments/'

        self.comment_data = {
            'post': self.post.id,
            'content': 'Test comment'
        }

    def test_create_comment_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.comment_url, self.comment_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Test comment')
        self.assertEqual(response.data['author']['username'], 'testuser')

    def test_create_comment_unauthenticated(self):
        response = self.client.post(self.comment_url, self.comment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_comment_as_author(self):
        comment = Comment.objects.create(post=self.post, content='Original', author=self.user)
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(f'{self.comment_url}{comment.id}/', {
            'content': 'Updated comment'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Updated comment')

    def test_update_comment_as_other_user(self):
        comment = Comment.objects.create(post=self.post, content='Original', author=self.user)
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(f'{self.comment_url}{comment.id}/', {
            'content': 'Updated comment'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comments_by_post(self):
        Comment.objects.create(post=self.post, content='Comment 1', author=self.user)
        Comment.objects.create(post=self.post, content='Comment 2', author=self.other_user)

        response = self.client.get(f'/api/comments/by_post/?post_id={self.post.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_comments_stats(self):
        comment1 = Comment.objects.create(post=self.post, content='Top level', author=self.user)
        Comment.objects.create(post=self.post, content='Reply', author=self.other_user, parent=comment1)

        response = self.client.get('/api/comments/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_comments'], 2)
        self.assertEqual(response.data['reply_comments'], 1)
        self.assertEqual(response.data['top_level_comments'], 1)


class LikeTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass123')
        self.post = Post.objects.create(title='Test Post', content='Content', author=self.user)
        self.comment = Comment.objects.create(post=self.post, content='Test comment', author=self.user)

    def test_create_post_like(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/posts/{self.post.id}/like/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(PostLike.objects.filter(post=self.post, user=self.user).exists())

    def test_create_comment_like(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/comments/{self.comment.id}/like/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(CommentLike.objects.filter(comment=self.comment, user=self.user).exists())

    def test_post_like_count(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(f'/api/posts/{self.post.id}/like/')

        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(f'/api/posts/{self.post.id}/like/')

        self.assertEqual(response.data['likes_count'], 2)

    def test_like_own_post(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/posts/{self.post.id}/like/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'like added')