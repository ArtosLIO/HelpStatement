from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import TestCase, RequestFactory, tag

from desk.form import CreationMyUserForm
from desk.models import MyUser, Statement, Comment
from desk.views import ListHelpStatement, SelfRegistration, CreateHelpStatement, UpdateHelpStatement, \
    ReturnedHelpStatement, CreateComment, UpdateSuccessHelpStatement, ListReturnHelpStatement, DeleteReturnHelpStatement


class TestLoginUser(TestCase):
    def setUp(self):
        MyUser.objects.create_user(username='test', password='1q2w3e')

    def test_login(self):
        user = self.client.login(username='test', password='1q2w3e')
        self.assertTrue(user)

    def test_failed_username(self):
        user = self.client.login(username='tes', password='1q2w3e')
        self.assertFalse(user)

    def test_failed_password(self):
        user = self.client.login(username='test', password='1q2w3')
        self.assertFalse(user)

    def test_failed_user_pass(self):
        user = self.client.login(username='tes', password='1q2w3')
        self.assertFalse(user)

    def test_registration(self):
        form = CreationMyUserForm({'username': 'usertest', 'password1': '123qwe456rty', 'password2': '123qwe456rty'})
        if form.is_valid():
            request = RequestFactory().post('/registration/')
            view = SelfRegistration()
            view.setup(request)
            view.form_valid(form)
        user = MyUser.objects.get(username='usertest')
        self.assertIn(user, MyUser.objects.all())

    def test_failed_registration(self):
        form = CreationMyUserForm({'username': 'usertest', 'password1': '123qwe456rty', 'password2': '123qwe'})
        valid = form.is_valid()
        self.assertFalse(valid)


@tag('view')
class TestViewUser(TestCase):

    def setUp(self):
        self.user = MyUser.objects.create_user(
            username='user1',
            password='123qwe456rty',
            is_staff=False
        )
        self.statement = Statement.objects.create(
            user=self.user,
            title='Test Title',
            description='Some text description'
        )
        self.statement_F = Statement.objects.create(
            user=self.user,
            title='Rejected title',
            description='Rejected text',
            success='F'
        )
        self.statement_R = Statement.objects.create(
            user=self.user,
            title='Returned title',
            description='Returned text',
            success='R'
        )

    def test_list_statement(self):
        request = RequestFactory().get('/list/')
        request.user = self.user
        view = ListHelpStatement()
        view.setup(request)
        queryset = view.get_queryset()
        self.assertIn(self.statement, queryset)

    def test_failed_list_statement(self):
        request = RequestFactory().get('/list/')
        request.user = AnonymousUser()
        view = ListHelpStatement()
        view.setup(request)
        answer = view.dispatch(request)
        self.assertNotIn('context_data', answer)

    def test_create_statement(self):
        data = {'title': 'Test title', 'description': 'Some text', 'level_important': 'L'}
        request = RequestFactory().post('/create/statement/', data)
        request.user = self.user
        view = CreateHelpStatement()
        view.setup(request)
        view.post(request)
        statement = Statement.objects.get(title='Test title')
        self.assertIn(statement, Statement.objects.all())

    def test_failed_create_statement(self):
        data = {'title': 'Test title', 'description': '', 'level_important': 'L'}
        request = RequestFactory().post('/create/statement/', data)
        request.user = self.user
        view = CreateHelpStatement()
        view.setup(request)
        answer = view.post(request)
        self.assertIn('description', answer.context_data['form'].errors)

    def test_update_statement(self):
        id = self.statement.id
        data = {'title': self.statement.title,
                'description': 'Text update',
                'level_important': self.statement.level_important
                }
        request = RequestFactory().post(f'/update/statement/{id}/', data)
        view = UpdateHelpStatement()
        view.setup(request, pk=id)
        view.post(request=request)
        update_statement = Statement.objects.get(id=id)
        self.assertNotEqual(self.statement.description, update_statement.description)

    def test_failed_update_statement(self):
        id = self.statement.id
        data = {'title': self.statement.title,
                'description': '',
                'level_important': self.statement.level_important
                }
        request = RequestFactory().post(f'/update/statement/{id}/', data)
        view = UpdateHelpStatement()
        view.setup(request, pk=id)
        view.post(request=request)
        update_statement = Statement.objects.get(id=id)
        self.assertEqual(self.statement.description, update_statement.description)

    def test_returned_statement(self):
        id = self.statement_F.id
        request = RequestFactory().post(f'/returned/statement/{id}')
        view = ReturnedHelpStatement()
        view.setup(request, pk=id)
        view.post(request=request)
        obj = Statement.objects.get(id=id)
        self.assertEqual(obj.success, 'R')

    def test_failed_returned_statement(self):
        id = self.statement.id
        request = RequestFactory().post(f'/returned/statement/{id}')
        view = ReturnedHelpStatement()
        view.setup(request, pk=id)
        view.post(request=request)
        obj = Statement.objects.get(id=id)
        self.assertNotEqual(obj.success, 'R')

    def test_create_comment(self):
        id = self.statement.id
        request = RequestFactory().post(f'/create/comment/{id}/', {'text': 'text comment'})
        request.user = self.user
        view = CreateComment()
        view.setup(request, pk=id)
        view.post(request, pk=id)
        comment = Comment.objects.first()
        self.assertEqual(comment.text, 'text comment')

    def test_failed_create_comment(self):
        id = self.statement.id
        request = RequestFactory().post(f'/create/comment/{id}/', {'text': ''})
        request.user = self.user
        view = CreateComment()
        view.setup(request, pk=id)
        view.post(request, pk=id)
        comment = Comment.objects.first()
        self.assertIsNone(comment)

# admin

    def test_confirmed_success_statement(self):
        id = self.statement.id
        request = RequestFactory().post(f'/success/{id}/', {'success': 'confirmed'})
        request.user = self.user
        view = UpdateSuccessHelpStatement()
        view.setup(request, pk=id)
        view.post(request)
        statement = Statement.objects.get(pk=id)
        self.assertEqual(statement.success, 'C')

    def test_rejected_success_statement(self):
        id = self.statement.id
        request = RequestFactory().post(f'/success/{id}/', {'success': 'rejected', 'comment': 'rejected comment'})
        request.user = self.user
        view = UpdateSuccessHelpStatement()
        view.setup(request, pk=id)
        view.post(request)
        statement = Statement.objects.get(pk=id)
        comment = Comment.objects.first()
        self.assertEqual(comment.text, 'rejected comment')
        self.assertEqual(statement.success, 'F')

    def test_failed_success_statement(self):
        id = self.statement.id
        request = RequestFactory().post(f'/success/{id}/', {'success': 'rejected', 'comment': ''})
        request.user = self.user
        view = UpdateSuccessHelpStatement()
        view.setup(request, pk=id)
        view.post(request)
        statement = Statement.objects.get(pk=id)
        comment = Comment.objects.first()
        self.assertIsNone(comment)
        self.assertEqual(statement.success, 'P')

    def test_return_list(self):
        request = RequestFactory().get('/list/returned/')
        request.user = self.user
        view = ListReturnHelpStatement()
        view.setup(request)
        queryset = view.get_queryset()
        self.assertIn(self.statement_R, queryset)

    def test_failed_return_list(self):
        request = RequestFactory().get('/list/returned/')
        request.user = AnonymousUser()
        view = ListReturnHelpStatement()
        view.setup(request)
        answer = view.dispatch(request)
        self.assertNotIn('context_data', answer)

    def test_delete_return_statement(self):
        id = self.statement_R.id
        request = RequestFactory().post(f'/delete/statement/{id}/')
        view = DeleteReturnHelpStatement()
        view.setup(request, pk=id)
        view.post(request, pk=id)
        statement = Statement.objects.filter(success='R')
        self.assertNotIn(self.statement_R, statement)

    def test_failed_delete_return_statement(self):
        id = self.statement_R.id
        request = RequestFactory().post(f'/delete/statement/{id}/')
        request.user = self.user
        view = DeleteReturnHelpStatement()
        view.setup(request, pk=id)
        permission = True
        try:
            view.dispatch(request)
        except PermissionDenied:
            permission = False
        statement = Statement.objects.filter(success='R')
        self.assertIn(self.statement_R, statement)
        self.assertFalse(permission)
