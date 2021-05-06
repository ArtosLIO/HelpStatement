from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

from desk.form import CreationMyUserForm, CreateCommentForm, CreateHelpStatementForm, UpdateHelpStatementForm, \
    AdminUpdateHelpStatementForm
from desk.models import Statement, Comment


class SelfLogin(LoginView):
    template_name = 'login.html'


class SelfRegistration(CreateView):
    template_name = 'registration.html'
    form_class = CreationMyUserForm
    success_url = '/login/'


class SelfLogout(LoginRequiredMixin, LogoutView):
    next_page = '/login/'

# User

class ListHelpStatement(LoginRequiredMixin, ListView):
    model = Statement
    template_name = 'user_list_statement.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset.exclude(success='R')
        else:
            return queryset.filter(user=self.request.user).exclude(success='R')


class DetailHelpStatement(UserPassesTestMixin, DetailView):
    template_name = 'user_detail_statement.html'
    model = Statement

    def test_func(self):
        obj = self.get_object()
        if obj.user == self.request.user or self.request.user.is_staff:
            return True
        else:
            return False


class CreateHelpStatement(LoginRequiredMixin, CreateView):
    template_name = 'user_create_statement.html'
    form_class = CreateHelpStatementForm
    success_url = '/list/'

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            statement = form.save(commit=False)
            statement.user = request.user
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class UpdateHelpStatement(LoginRequiredMixin, UpdateView):
    template_name = 'user_update_statement.html'
    model = Statement
    form_class = UpdateHelpStatementForm
    success_url = '/list/'

    def get_success_url(self):
        self.success_url = f"/detail/{self.kwargs['pk']}/"
        return super().get_success_url()


class ReturnedHelpStatement(LoginRequiredMixin, UpdateView):
    success_url = '/list/'
    model = Statement

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.success = 'R'
        return self.form_valid(self.object)

    def get_success_url(self):
        return self.success_url


class CreateComment(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CreateCommentForm

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.statement_id = kwargs['pk']
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        self.success_url = f"/detail/{self.kwargs['pk']}/"
        return super().get_success_url()

# Superuser

class ConfirmedHelpStatement(UserPassesTestMixin, UpdateView):
    success_url = '/list/'
    model = Statement
    form_class = AdminUpdateHelpStatementForm

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.success = 'C'
        return self.form_valid(self.object)

    def get_success_url(self):
        return self.success_url

    def test_func(self):
        return self.request.user.is_staff


class RejectedHelpStatement(UserPassesTestMixin, UpdateView):
    success_url = '/list/'
    model = Statement
    form_class = AdminUpdateHelpStatementForm

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.POST['comment'] not in ('', ' '):
            self.object.success = 'F'
            comment = Comment(text=request.POST['comment'])
            comment.user = request.user
            comment.statement = self.object
            comment.save()
            return self.form_valid(self.object)
        else:
            return self.form_invalid(self.object)

    def get_success_url(self):
        return self.success_url

    def test_func(self):
        return self.request.user.is_staff


class UpdateSuccessHelpStatement(UserPassesTestMixin, UpdateView):
    success_url = '/list/'
    model = Statement
    form_class = AdminUpdateHelpStatementForm
    template_name = 'admin_error_success.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success = request.POST.get('success', False)
        if success == 'confirmed':
            self.object.success = 'C'
            return self.form_valid(self.object)
        elif success == 'rejected':
            if request.POST['comment'] not in ('', ' '):
                self.object.success = 'F'
                comment = Comment(text=request.POST['comment'])
                comment.user = request.user
                comment.statement = self.object
                comment.save()
                return self.form_valid(self.object)
            else:
                return self.form_invalid(self.object)
        else:
            self.form_invalid(self.object)

    def get_success_url(self):
        return self.success_url

    def test_func(self):
        return self.request.user.is_staff


class ListReturnHelpStatement(UserPassesTestMixin, ListView):
    template_name = 'admin_return_statement.html'
    model = Statement

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(success='R')
        return queryset

    def test_func(self):
        return self.request.user.is_staff


class DeleteReturnHelpStatement(UserPassesTestMixin, DeleteView):
    success_url = '/list/returned/'
    model = Statement

    def test_func(self):
        return self.request.user.is_staff
