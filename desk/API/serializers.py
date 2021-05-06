from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from desk.models import Statement, MyUser, Comment


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = MyUser
        fields = ['username', 'password']

    def save(self, **kwargs):
        self.validated_data["password"] = make_password(self.validated_data["password"])
        return super().save()


# All

class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text', 'statement']


class ListDetailHelpStatementSerializer(serializers.ModelSerializer):
    success = serializers.CharField(read_only=True, required=False)
    level_important = serializers.CharField(required=False)
    user = RegistrationSerializer(read_only=True, required=False)
    comment = serializers.StringRelatedField(source='state_comment', many=True, read_only=True)

    class Meta:
        model = Statement
        fields = ['id', 'user', 'title', 'description', 'level_important', 'success', 'comment']


class CreateUpdateHelpStatementSerializer(serializers.ModelSerializer):
    level_important = serializers.StringRelatedField(required=False)

    class Meta:
        model = Statement
        fields = ['title', 'description', 'level_important']


# Superuser

class SuccessHelpStatementSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(source='state_comment', required=False)
    success = serializers.CharField(required=True)

    class Meta:
        model = Statement
        fields = ['success', 'comment']

    def validate_comment(self, attrs):
        success = self.initial_data.get('success')
        if attrs:
            if success == 'F':
                if len(attrs) > 2:
                    return attrs
            elif success == 'C':
                return attrs
        raise serializers.ValidationError("Don't have success or don't valid success")

    def validate_success(self, attrs):
        if attrs == 'F':
            comment = self.initial_data.get('comment')
            self.validate_comment(attrs=comment)
        if attrs in ('F', 'C'):
            return attrs
        raise serializers.ValidationError("Don't valid success")
