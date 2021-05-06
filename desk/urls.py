from django.urls import path, include
from rest_framework import routers

from desk.API.resorces import LoginGetToken, ListDetailHelpStatement, RegistrationAPI, LogoutAPI, \
    CreateUpdateHelpStatement, CreateCommentAPIView, ListReturnHelpStatementAPIView, SuccessHelpStatementAPIView, \
    RejectedReturnHelpStatement
from desk.views import SelfLogin, SelfRegistration, SelfLogout, ListHelpStatement, DetailHelpStatement, CreateComment, \
    CreateHelpStatement, UpdateHelpStatement, ReturnedHelpStatement, DeleteReturnHelpStatement, \
    ListReturnHelpStatement, UpdateSuccessHelpStatement


router = routers.SimpleRouter()
router.register(r'list', ListDetailHelpStatement)
router.register(r'create', CreateUpdateHelpStatement)
router.register(r'comment', CreateCommentAPIView)
router.register(r'admin/list', ListReturnHelpStatementAPIView)
router.register(r'success', SuccessHelpStatementAPIView)
router.register(r'rejected/return', RejectedReturnHelpStatement)


urlpatterns = [
    path('login/', SelfLogin.as_view(), name='login'),
    path('registration/', SelfRegistration.as_view(), name='registration'),
    path('logout/', SelfLogout.as_view(), name='logout'),

    path('list/', ListHelpStatement.as_view(), name='list'),
    path('create/statement/', CreateHelpStatement.as_view(), name='create_statement'),
    path('update/statement/<int:pk>', UpdateHelpStatement.as_view(), name='update_statement'),
    path('returned/statement/<int:pk>', ReturnedHelpStatement.as_view(), name='return_statement'),
    path('detail/<int:pk>/', DetailHelpStatement.as_view(), name='detail'),
    path('create/comment/<int:pk>/', CreateComment.as_view(), name='create_comment'),

    path('success/<int:pk>', UpdateSuccessHelpStatement.as_view(), name='success_statement'),
    path('list/returned/', ListReturnHelpStatement.as_view(), name='list_returned'),
    path('delete/statement/<int:pk>', DeleteReturnHelpStatement.as_view(), name='delete_statement'),

    # API

    path('api/login/', LoginGetToken.as_view(), name='api_login'),
    path('api/registration/', RegistrationAPI.as_view(), name='api_registration'),
    path('api/logout/', LogoutAPI.as_view(), name='api_logout'),
    path('api/', include(router.urls)),
]
