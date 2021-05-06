from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import make_aware
from rest_framework.authtoken.models import Token

CHOICE_LEVEL = [
    ('L', 'Low'),
    ('M', 'Medium'),
    ('H', 'High')
]
CHOICE_SUCCESS = [
    ('P', 'Process'),
    ('C', 'Confirmed'),
    ('F', 'Rejected'),
    ('R', 'Returned')
]


class MyUser(AbstractUser):
    pass


class Statement(models.Model):
    user = models.ForeignKey(MyUser, related_name='master_statement', on_delete=models.CASCADE)
    title = models.CharField(max_length=150, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    level_important = models.CharField(choices=CHOICE_LEVEL, blank=False, null=False, default='L', max_length=10)
    success = models.CharField(choices=CHOICE_SUCCESS, blank=False, null=False, default='P', max_length=10)
    create_at = models.DateTimeField()

    class Meta:
        ordering = ['-create_at', 'title']
        unique_together = ['user', 'title']

    def save(self, *args, **kwargs):
        if not self.id:
            self.create_at = make_aware(datetime.now())
        return super().save(*args, **kwargs)


class Comment(models.Model):
    user = models.ForeignKey(MyUser, related_name='master_comment', on_delete=models.CASCADE)
    statement = models.ForeignKey(Statement, related_name='state_comment', on_delete=models.CASCADE)
    text = models.TextField(blank=False, null=False)
    create_at = models.DateTimeField()

    class Meta:
        ordering = ['create_at']

    def save(self, *args, **kwargs):
        if not self.id:
            self.create_at = make_aware(datetime.now())
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.text


class MyToken(Token):
    last_action = models.DateTimeField(null=True)
