from django.contrib import admin

from desk.models import Statement, Comment, MyUser, MyToken

admin.site.register(Statement)
admin.site.register(Comment)
admin.site.register(MyUser)
admin.site.register(MyToken)
