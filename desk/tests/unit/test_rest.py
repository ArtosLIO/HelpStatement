from unittest.mock import Mock

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory, tag
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.test import APIRequestFactory, APIClient

from desk.API.resorces import LoginGetToken, CreateCommentAPIView
from desk.API.serializers import CreateCommentSerializer
from desk.models import MyUser, MyToken, Statement, Comment


class TestLoginRest(TestCase):

    def setUp(self):
        self.user = MyUser.objects.create(
            username="user",
            password="123qwe456rty",
            is_staff=False
        )
        self.token = MyToken.objects.create(
            user=self.user
        )
        self.client = APIClient()

    def test_login_api(self):
        data = {'username': 'user', 'password': '123qwe456rty'}
        response = self.client.post('/api/login/', data)
        token = MyToken.objects.first()
        self.assertEqual(token.pk, response.token)


class TestResorcesREST(TestCase):

    def setUp(self):
        self.user = MyUser.objects.create(
            username="user",
            password="123qwe456rty",
            is_staff=False
        )
        self.statement = Statement.objects.create(
            user=self.user,
            title='REST Title',
            description='Some REST description'
        )

    def test_create_comment_API(self):
        data = {"text": "create comment", "statement": "1"}
        request = APIRequestFactory().post('/api/comment/', data)
        request.user = self.user
        view = CreateCommentAPIView()
        view.setup(request)
        serializer = CreateCommentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        view.perform_create(serializer)
        comment = Comment.objects.first()
        self.assertEqual(comment.text, 'create comment')

    def test_failed_create_comment_API(self):
        data = {"text": "", "statement": "1"}
        request = APIRequestFactory().post('/api/comment/', data=data)
        request.data = data
        request.user = self.user
        view = CreateCommentAPIView()
        view.setup(request)
        view.create(request)
        comment = Comment.objects.first()
        self.assertIsNone(comment)
