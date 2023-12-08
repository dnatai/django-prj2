from django.shortcuts import render, redirect
from userauths.forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Profile, User
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from core.models import Post, FriendRequest, Group, Page, Block
from userauths.forms import UserRegisterForm, ProfileUpdateForm, UserUpdateForm
from django.http import JsonResponse
# Create your views here.

def RegisterView(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are registered")
        return redirect("core:feed")
    
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        form.save()

        full_name = form.cleaned_data.get("full_name")
        phone = form.cleaned_data.get("phone")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password1")

        user = authenticate(email=email, password=password)
        login(request, user)

        profile = Profile.objects.get(user=request.user)
        profile.full_name = full_name
        profile.phone = phone
        profile.save()

        messages.success(request,f"Hi {full_name}. your account was created successfully.")
        return redirect("core:feed")
    
    context = {
        "form":form
    }
    return render(request, "userauths/sign-up.html", context)

def loginView(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already login")
        return redirect("core:feed")
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You are logged in")
                return redirect("core:feed")
            else:
                messages.error(request, "Username or password does not exist")
                return redirect("userauths:sign-up")
        except:
            messages.error(request, "User does not exist")
            return redirect("userauths:sign-up")

    return HttpResponseRedirect("/")

def LogoutView(request):
    logout(request)
    messages.success(request, "You are logged out")
    return redirect("userauths:sign-up")


@login_required
def My_Profile(request):
    profile = request.user.profile
    all_profiles = Profile.objects.all()
    posts = Post.objects.filter(active=True, user=request.user).order_by("-id")
    groups = Group.objects.filter(member=request.user)
    pages = Page.objects.filter(user=request.user)
    user_block = Block.objects.filter(blocker=request.user).exists()
    is_blocked = Block.objects.filter(blocked_user=request.user).exists()
        # Kiểm tra xem người dùng hiện tại có bị chặn bởi profile_user không
    user_block_list = Block.objects.filter(blocker = request.user)
    context = {
        "profile": profile,
        "profiles": all_profiles,
        "posts": posts,
        "groups": groups,
        "pages": pages,
        "user_block":user_block,
        "is_blocked":is_blocked,
        "user_block_list":user_block_list,
    }

    return render(request, "userauths/my-profile.html", context)


@login_required
def Friend_Profile(request, username):
    profile = Profile.objects.get(user__username=username)
    if request.user.profile == profile:
        return redirect("userauths:my-profile")
    posts = Post.objects.filter(active=True, user=profile.user).order_by("-id")
    user_block = Block.objects.filter(blocker=request.user).exists()
    is_blocked = Block.objects.filter(blocked_user=request.user).exists()
        # Kiểm tra xem người dùng hiện tại có bị chặn bởi profile_user không
    user_block_list = Block.objects.filter(blocker = request.user)
    bool = False
    bool_friend = False

    sender = request.user
    receiver = profile.user

    try:
        friend_request = FriendRequest.objects.get(sender=sender, receiver=receiver)
        if friend_request:
            bool = True
        else:
            bool = False
    except:
        bool = False

    context = {
        "posts":posts,
        "bool_friend":bool_friend,
        "bool":bool,
        "profile":profile,
        "user_block":user_block,
        "is_blocked":is_blocked,
        "user_block_list":user_block_list,
    }

    return render(request, "userauths/friend-profile.html", context)


def profile_update(request):
    if request.method == "POST":
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
       

        if p_form.is_valid():
            p_form.save()
            
            messages.success(request, "Profile Updated Successfully.")
            return redirect('userauths:profile-update')
    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)
        

    context = {
        'p_form': p_form,
        
    }
    return render(request, 'userauths/profile-update.html', context)



