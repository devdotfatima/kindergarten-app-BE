# auth/urls.py
from django.urls import path
from .views import LoginView,ParentRegistrationView, TeacherRegistrationView,AdminRegistrationView,SetPinView,PinLoginView,DeleteUserView,EditProfileView,UpdatePasswordView,LogoutView,UserProfileView

urlpatterns = [
    path('auth/login', LoginView.as_view(), name='login'),
    path("set-pin", SetPinView.as_view(), name="set-pin"),
    path("auth/login-with-pin", PinLoginView.as_view(), name="login-with-pin"),
    path("auth/register/parent", ParentRegistrationView.as_view(), name="register_parent"),
    path("auth/register/teacher", TeacherRegistrationView.as_view(), name="register_teacher"),
    path("auth/register/admin", AdminRegistrationView.as_view(), name="register_admin"),
    path("<int:id>", DeleteUserView.as_view(), name="delete_user"), 
    path("auth/profile", UserProfileView.as_view(), name="user_profile"),

    

    # New URLs
    path("auth/profile/edit", EditProfileView.as_view(), name="edit_profile"),
    path("auth/profile/update-password", UpdatePasswordView.as_view(), name="update_password"),
    path("auth/logout", LogoutView.as_view(), name="logout"),
]


