# auth/urls.py
from django.urls import path
from .views import (
    LoginView, ParentRegistrationView, TeacherRegistrationView, AdminRegistrationView,
    SetPinView, PinLoginView, DeleteUserView, EditProfileView, UpdatePasswordView,
    LogoutView, UserProfileView,
    # Superadmin user management
    UserListView, UserDetailView, UserDeactivateView, UserChangeRoleView,
    # Admin-created users with credential emails
    AdminCreateParentView, AdminCreateTeacherView, AdminCreateAdminView,
    AdminResetCredentialsView,
)

urlpatterns = [
    path('auth/login', LoginView.as_view(), name='login'),
    path("set-pin", SetPinView.as_view(), name="set-pin"),
    path("auth/login-with-pin", PinLoginView.as_view(), name="login-with-pin"),
    path("auth/register/parent", ParentRegistrationView.as_view(), name="register_parent"),
    path("auth/register/teacher", TeacherRegistrationView.as_view(), name="register_teacher"),
    path("auth/register/admin", AdminRegistrationView.as_view(), name="register_admin"),
    path("<int:id>", DeleteUserView.as_view(), name="delete_user"),
    path("auth/profile", UserProfileView.as_view(), name="user_profile"),
    path("auth/profile/<int:id>/", UserProfileView.as_view(), name="user_profile_by_id"),
    path("auth/profile/edit", EditProfileView.as_view(), name="edit_profile"),
    path("auth/profile/update-password", UpdatePasswordView.as_view(), name="update_password"),
    path("auth/logout", LogoutView.as_view(), name="logout"),

    # Superadmin: user management (specific paths before generic <str:action>)
    path("list/", UserListView.as_view(), name="user_list"),
    path("manage/<int:id>/", UserDetailView.as_view(), name="user_detail"),
    path("manage/<int:id>/change-role/", UserChangeRoleView.as_view(), name="user_change_role"),
    path("manage/<int:id>/<str:action>/", UserDeactivateView.as_view(), name="user_deactivate"),

    # Admin/Superadmin: create users with auto credential email
    path("admin/create-parent/", AdminCreateParentView.as_view(), name="admin_create_parent"),
    path("admin/create-teacher/", AdminCreateTeacherView.as_view(), name="admin_create_teacher"),
    path("admin/create-admin/", AdminCreateAdminView.as_view(), name="admin_create_admin"),
    path("admin/reset-credentials/<int:id>/", AdminResetCredentialsView.as_view(), name="admin_reset_credentials"),
]
