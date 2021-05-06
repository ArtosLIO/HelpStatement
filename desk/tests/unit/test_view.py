from django.test import TestCase

from desk.models import MyUser, Statement


class TestViewUser(TestCase):

    def SetUp(self):
        self.user = MyUser(username='user1', password='123qwe456rty')
        self.statement = Statement(
            user=self.user,
            title='Test Title',
            description='Some text description'
        )

    def test_list_statement(self):
        pass
