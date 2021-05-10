from datetime import datetime, timedelta

from django.db.models import QuerySet
from django.utils.timezone import make_aware
from rest_framework import permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, \
    DestroyModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin, GenericViewSet

from HelpDesk.settings import AUTO_LOGOUT
from desk.API.serializers import CreateCommentSerializer, RegistrationSerializer, ListDetailHelpStatementSerializer, \
    CreateUpdateHelpStatementSerializer, SuccessHelpStatementSerializer
from desk.models import Statement, Comment, MyToken, MyUser


class LoginGetToken(ObtainAuthToken):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = MyToken.objects.get_or_create(user=user)
        if token.last_action and (make_aware(datetime.now()) - timedelta(seconds=AUTO_LOGOUT)) > token.last_action:
            token.delete()
            action = make_aware(datetime.now())
            token, created = MyToken.objects.get_or_create(user=user, last_action=action)
        if not token.last_action:
            token.last_action = make_aware(datetime.now())
            token.save()
        return Response({'token': token.key})


class RegistrationAPI(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = MyUser.objects.all()
    serializer_class = RegistrationSerializer


class LogoutAPI(DestroyAPIView):
    queryset = MyToken.objects.all()

    def get_object(self):
        obj = self.queryset.filter(user=self.request.user)
        return obj


class CreateCommentAPIView(CreateModelMixin, GenericViewSet, ViewSetMixin):
    queryset = Comment.objects.all()
    serializer_class = CreateCommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ListDetailHelpStatement(ListModelMixin, RetrieveModelMixin, GenericViewSet, ViewSetMixin):
    queryset = Statement.objects.all()
    serializer_class = ListDetailHelpStatementSerializer

    def get_queryset(self):
        assert self.queryset is not None, (
                "'%s' should either include a `queryset` attribute, "
                "or override the `get_queryset()` method."
                % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            if self.request.user.is_staff:
                return queryset.all().exclude(success='R')
            return queryset.filter(user=self.request.user).exclude(success='R')

    def filter_queryset(self, queryset):
        level_important = self.request.stream.GET.get('level_important', False)
        if level_important:
            if level_important in ('low', 'L', 'Low'):
                level_important = 'L'
            elif level_important in ('medium', 'M', 'Medium'):
                level_important = 'M'
            elif level_important in ('high', 'H', 'High'):
                level_important = 'H'
            return queryset.filter(level_important=level_important)
        else:
            return queryset

# User

class CreateUpdateHelpStatement(CreateModelMixin, UpdateModelMixin, GenericViewSet, ViewSetMixin):
    queryset = Statement.objects.all()
    serializer_class = CreateUpdateHelpStatementSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if self.queryset.get(user=self.request.user, pk=self.kwargs.get('pk', 0)):
            serializer.save()

# Superuser

class ListReturnHelpStatementAPIView(ListModelMixin, GenericViewSet, ViewSetMixin):
    permission_classes = [permissions.IsAdminUser]
    queryset = Statement.objects.all()
    serializer_class = ListDetailHelpStatementSerializer

    def filter_queryset(self, queryset):
        return queryset.filter(success='R')


class SuccessHelpStatementAPIView(UpdateModelMixin, GenericViewSet, ViewSetMixin):
    permission_classes = [permissions.IsAdminUser]
    queryset = Statement.objects.all()
    serializer_class = SuccessHelpStatementSerializer

    def perform_update(self, serializer):
        statement = serializer.instance
        statement.success = serializer.validated_data.get('success')
        statement.save()
        text = serializer.validated_data.get('state_comment', False)
        if text:
            comment = Comment(statement=serializer.instance, user=self.request.user, text=text)
            comment.save()


class RejectedReturnHelpStatement(DestroyModelMixin, GenericViewSet, ViewSetMixin):
    permission_classes = [permissions.IsAdminUser]
    queryset = Statement.objects.all()

    def perform_destroy(self, instance):
        if instance.success == 'R':
            instance.delete()
        raise Exception(None, "This statement not returned.")

