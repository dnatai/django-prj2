from django.urls import path
from userauths import views

app_name = "userauths"

urlpatterns = [
    path("sign-up/", views.RegisterView, name="sign-up"),
    path("sign-in/", views.loginView, name="sign-in"),
    path("sign-out/", views.LogoutView, name="sign-out"),

    path("my-profile/", views.My_Profile, name="my-profile"),
    path("profile/<username>", views.Friend_Profile, name="profile"),
    path("profile-update/", views.profile_update, name="profile-update"),
    
]
