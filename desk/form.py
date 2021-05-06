from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.forms import ModelForm

from desk.models import MyUser, Statement, Comment


class CreationMyUserForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ("username",)
        field_classes = {'username': UsernameField}


class CreateHelpStatementForm(ModelForm):
    class Meta:
        model = Statement
        fields = ('title', 'description', 'level_important')


class UpdateHelpStatementForm(ModelForm):
    class Meta:
        model = Statement
        fields = ('description', 'level_important')


class CreateCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )

# Superuser

class AdminUpdateHelpStatementForm(ModelForm):
    class Meta:
        model = Statement
        fields = ('success', )
