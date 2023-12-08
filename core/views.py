from django.shortcuts import render, redirect, get_object_or_404
from core.models import Post, Comment, ReplyComment, FriendRequest, ChatMessage,  GroupChatMessage, GroupChat, Notification, Group, GroupPost,GroupMembership,MessageGroup, Page, PagePost, Gallery, Block, OTP 
from django.utils.text import slugify
import shortuuid
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.timesince import timesince
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from userauths.models import User, Profile
from django.core.paginator import Paginator
from django.db.models import OuterRef, Subquery
from django.db.models import Q
from .forms import GroupForm, GroupPostForm, PageForm, PagePostForm, CreateGroupChatForm, PostForm, ForgotPasswordForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views import View
import random
import string
from mysite.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
# Create your views here.


def create_group_inbox(request):
    if request.method == 'POST':
        form = CreateGroupChatForm(request.POST, request.FILES)
        if form.is_valid():
            groupchat = form.save(commit=False)
            groupchat.host = request.user
            groupchat.save()
            groupchat.members.add(request.user)  # Add the host as a member

            return redirect("core:group_inbox_detail", slug=groupchat.slug)
    else:
        form = CreateGroupChatForm()

    context = {'form': form}
    return render(request, 'chat/create_group_inbox.html', context)



def group_index(request):
    notifyCounter=len(  Notification.objects.filter(reciever=request.user).filter(read=False) )

    query = request.GET.get('q', '')
    if(query):
        groups = Group.objects.filter(name__icontains=str(query)).union(
            Group.objects.filter(name__in=[query]))
    else:
        groups = Group.objects.all()

    return render(request, "groups/index.html", {

        "groups": groups,
        "notifyCounter":notifyCounter


    })

@login_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # Check if the logged-in user has permission to delete the group
    if request.user != group.user:
        return HttpResponseForbidden("You don't have permission to delete this group.")

    # Delete the group and return a JSON response
    if request.method == 'POST':
        group.delete()
        return redirect('core:feed')

    # Render the confirmation template (confirm_delete_group.html)
    return render(request, 'core/confirm_delete_group.html', {'group': group})

@login_required
def update_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # Check if the user has permission to update the group
    if request.user != group.user:
        return HttpResponseForbidden("You don't have permission to update this group.")

    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            form.save()
            return redirect('core:group_post_list',group_id=group.id)  # Replace 'profile' with the URL name of the user's profile
    else:
        form = GroupForm(instance=group)

    return render(request, 'core/update_group.html', {'form': form, 'group': group})

def update_page(request, page_id):
    page = get_object_or_404(Page, id=page_id)

    # Check if the user has permission to update the page
    if request.user != page.user:
        return HttpResponseForbidden("You don't have permission to update this page.")

    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            form.save()
            return redirect('core:page_post_list',page_id=page.id)  # Replace 'profile' with the URL name of the user's profile
    else:
        form = PageForm(instance=page)

    return render(request, 'core/update_page.html', {'form': form, 'page': page})


@login_required
def delete_page(request, page_id):
    page = get_object_or_404(Page, id=page_id)

    # Check if the user has permission to delete the page
    if request.user != page.user:
        return HttpResponseForbidden("You don't have permission to delete this page.")

    # Delete the page and return a JSON response
    if request.method == 'POST':
        page.delete()
        return redirect('core:feed')

    # Render the confirmation template (confirm_delete_page.html)
    return render(request, 'core/confirm_delete_page.html', {'page': page})

# def create_group(request):
#     form = GroupForm(request.POST, request.FILES or None)
#     print(form)
#     if form.is_valid():
#         print(form)

#         name = form.cleaned_data['name']
#         privacy = form.cleaned_data['privacy']
#         description = form.cleaned_data['description']
#         cover = form.cleaned_data['cover']
#         group = Group.objects.create(
#             name=name, privacy=privacy, description=description, cover=cover, owner=request.user)
#         request.user.userprofile.groups.add(group)
#         return redirect("/group/group-page/"+str(group.id))
#     return render(request, "core/create-group.html", {
#         "form": form
#     })

noti_new_like = "New Like"
noti_new_follower = "New Follower"
noti_friend_request = "Friend Request"
noti_new_comment = "New Comment"
noti_comment_liked = "Comment Liked"
noti_comment_replied = "Comment Replied"
noti_friend_request_accepted = "Friend Request Accepted"

def send_notification(user, sender, post, comment, notification_type):
    notification = Notification.objects.create(
        user=user, 
        sender=sender, 
        post=post, 
        comment=comment, 
        notification_type=notification_type
    )
    return notification


@login_required
def index(request):
    blocked_users = Block.objects.filter(blocked_user=request.user).values_list('blocker', flat=True)
    friends = request.user.profile.friends.all()
    followings = request.user.profile.followings.all()   
        # danh sach nguoi dang theo doi
    group = Group.objects.filter(member=request.user)
    posts = Post.objects.filter(Q(user = request.user) |Q(user__in = followings)|Q(user__in=friends)).exclude(
        user__in=Block.objects.filter(blocker=request.user).values_list('blocked_user__id', flat=True)
        ).order_by('-id')
    
    context = {
        "posts":posts
    }
    return render(request, "core/index.html",context)

def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    # Check if the user has permission to delete the post
    if request.user != post.user:
        return HttpResponseForbidden("You don't have permission to delete this post.")

    # Delete the post and redirect to a relevant page (e.g., user's profile)
    if request.method == 'POST':
        post.delete()
        return redirect('core:feed')  # Replace 'profile' with the URL name of the user's profile

    # Render the confirmation template (confirm_delete_post.html)
    return render(request, 'core/confirm_delete_post.html', {'post': post})

def update_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    # Check if the user has permission to update the post
    if request.user != post.user:
        return HttpResponseForbidden("You don't have permission to update this post.")

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('core:feed')  # Replace 'profile' with the URL name of the user's profile
    else:
        form = PostForm(instance=post)

    return render(request, 'core/update_post.html', {'form': form, 'post': post})

@login_required
def post_detail(request, slug):
    post = Post.objects.get(slug= slug, active=True, visibility="Everyone")
    context = {
        "p":post
    }
    return render(request, "core/post-detail.html",context)

@csrf_exempt
def create_post(request):

    if request.method == 'POST':
        title = request.POST.get('post-caption')
        visibility = request.POST.get('visibility')
        image = request.FILES.get('post-thumbnail')
        
        print("Title ============", title)
        print("thumbnail ============", image)
        print("visibility ============", visibility)

        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]

        if title and image:
            post = Post(title=title, image=image,  visibility=visibility, user=request.user, slug=slugify(title) + "-" + str(uniqueid.lower()))
            post.save()

            
            return JsonResponse({'post': {
                'title': post.title,
                'image_url': post.image.url,
                
                "full_name":post.user.profile.full_name,
                "profile_image":post.user.profile.image.url,
                "date":timesince(post.date),
                "id":post.id,
            }})
        else:
            return JsonResponse({'error': 'Invalid post data'})

    return JsonResponse({"data":"Sent"})

def create_page_posts(request, page_id):
    
    if request.method == 'POST':
        title = request.POST.get('page-post-caption')
        image = request.FILES.get('page-post-thumbnail')
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]

        if title and image:
            page = PagePost(title=title, image=image, user=request.user, slug=slugify(title) + "-" + str(uniqueid.lower()))
            page.save()

            return JsonResponse({'page': {
                'title': page.title,
                'image_url': page.image.url,
                
                "full_name":page.page.name,
                "profile_image":page.image.url,
                "date":timesince(page.date),
                "id":page.id,
            }})
        else:
            return JsonResponse({'error': 'Invalid post data'})

    return JsonResponse({"data":"Sent"})



def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.user = request.user
            group.save()
            return redirect('core:group_post_list',group_id=group.id)  # Redirect to the group list page after creating the group
    else:
        form = GroupForm()
    
    return render(request, 'core/create-group.html', {'form': form})

def create_page(request):
    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES)
        if form.is_valid():
            page = form.save(commit=False)
            page.user = request.user
            page.save()
            return redirect('core:page_post_list', page_id=page.id)  # Redirect to the group list page after creating the group
    else:
        form = PageForm()
    
    return render(request, 'core/create-page.html', {'form': form}) 
    


def create_group_post(request, group_id):
    # Fetch the group based on the group_id (you'll need to customize this part)
    group = Group.objects.get(id=group_id)

    if request.method == 'POST':
        form = GroupPostForm(request.POST, request.FILES)
        if form.is_valid():
            group_post = form.save(commit=False)
            group_post.group = group
            group_post.user = request.user
            group_post.save()
            
            return redirect('core:group_post_list', group.id)  # Redirect to the group post list page
    else:
        form = GroupPostForm()
    
    return render(request, 'core/create_group_post.html', {'form': form, 'group': group})   



def create_page_post(request, page_id):
    # Fetch the group based on the group_id (you'll need to customize this part)
    page = Page.objects.get(id=page_id)

    if request.method == 'POST':
        form = PagePostForm(request.POST, request.FILES)
        if form.is_valid():
            page_post = form.save(commit=False)
            page_post.page = page
            page_post.user = request.user
            page_post.save()
            
            return redirect('core:page_post_list', page.id)  # Redirect to the group post list page
    else:
        form = GroupPostForm()
    
    return render(request, 'core/create_page_post.html', {'form': form, 'page': page}) 


@login_required
def update_page_post(request, page_id):
    # Assuming 'page_id' is the primary key of your 'Page' model
    page_post = get_object_or_404(PagePost, page__id=page_id, user=request.user)

    if request.method == 'POST':
        form = PagePostForm(request.POST, request.FILES, instance=page_post)
        if form.is_valid():
            form.save()
            return redirect('core:page_post_list', page_id)
    else:
        form = PagePostForm(instance=page_post)

    return render(request, 'core/update_page_post.html', {'form': form, 'page_post': page_post})


@login_required
def delete_page_post(request, page_id):
    # Assuming 'page_id' is the primary key of your 'Page' model
    page_post = get_object_or_404(PagePost, page__id=page_id, user=request.user)

    if request.method == 'POST':
        # Delete the page post
        page_post.delete()
        return redirect('core:page_post_list', page_id)

    return render(request, 'core/delete_page_post.html', {'page_post': page_post})

def group_post_list(request, group_id):
   
    group = Group.objects.get(id=group_id)  # Fetch the group based on group_id
    group_posts = GroupPost.objects.filter(group=group).order_by('-id')

    groups_joined = GroupMembership.objects.filter(user=request.user, status='approved').all()
    groups_rejected = GroupMembership.objects.filter(user=request.user, status='rejected').values('group')
    groups_not_joined = Group.objects.exclude(
    Q(id__in=groups_joined) | Q(id__in=groups_rejected)
)
    is_member = GroupMembership.objects.filter(user=request.user, group=group).exists()
    status = GroupMembership.objects.get(user=request.user, group=group).status if is_member else None
    
    group = get_object_or_404(Group, id=group_id)
    members = User.objects.filter(groupmembership__group=group)
    profiles = Profile.objects.all()
    
        
        # Get all pending membership requests for the group
    pending_memberships = GroupMembership.objects.filter(group=group, status='requested')


    context = {
        'group': group,
        'group_posts': group_posts,
        'groups_joined':groups_joined,
        'groups_not_joined':groups_not_joined,
        'is_member':is_member,
        'members':members,
        'status':status,
        'profiles':profiles,
        'pending_memberships': pending_memberships,
    }

    return render(request, 'core/group_post_list.html', context)

@login_required
def update_group_post(request, group_id):
    # Assuming 'group_id' is the primary key of your 'Group' model
    group_post = get_object_or_404(GroupPost, group__id=group_id, user=request.user)

    if request.method == 'POST':
        form = GroupPostForm(request.POST, request.FILES, instance=group_post)
        if form.is_valid():
            form.save()
            return redirect('core:group_post_list', group_id)
    else:
        form = GroupPostForm(instance=group_post)

    return render(request, 'core/update_group_post.html', {'form': form, 'group_post': group_post})

@login_required
def delete_group_post(request, group_id):
    # Assuming 'group_id' is the primary key of your 'Group' model
    group_post = get_object_or_404(GroupPost, group__id=group_id, user=request.user)

    if request.method == 'POST':
        # Delete the group post
        group_post.delete()
        return redirect('core:group_post_list', group_id)

    return render(request, 'core/delete_group_post.html', {'group_post': group_post})

def page_post_list(request, page_id):
    page = Page.objects.get(id=page_id)  # Fetch the group based on group_id
    page_posts = PagePost.objects.filter(page=page).order_by('-id')

    context = {
        'page': page,
        'page_posts': page_posts,
        
    }
    return render(request, 'core/page_post_list.html', context)

def list_groups(request):
    # Filter groups with visibility set to "Everyone"
    groups = Group.objects.filter(visibility="Everyone")

    context = {
        'groups': groups,
        
    }

    return render(request, 'core/groups.html', context)

def list_pages(request):
    # Filter pages with visibility set to "Everyone"
    pages = Page.objects.filter(visibility="Everyone")

    context = {
        'pages': pages,
    }

    return render(request, 'core/pages.html', context)


def list_non_friends(request):
    # Filter users who are not friends with the requesting user
    non_friends = Profile.objects.exclude(user__friends=request.user)

    context = {
        'non_friends': non_friends,
    }

    return render(request, 'core/friends.html', context)


@login_required
def follow_user(request, username):
    try:
        # Ensure the user is not trying to follow/unfollow themselves
        if request.user.username == username:
            return JsonResponse({'success': False, 'error': 'You cannot follow/unfollow yourself'})

        user_to_follow = get_object_or_404(User, username=username)
        user_profile = request.user.profile

        if user_to_follow in user_profile.followings.all():
            user_profile.followings.remove(user_to_follow)
            is_following = False
        else:
            user_profile.followings.add(user_to_follow)
            is_following = True

        return JsonResponse({'success': True, 'is_following': is_following})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    

@login_required
def block_user(request, user_id):
    blocked_user = User.objects.get(pk=user_id)

    # Kiểm tra xem đã có trong danh sách chặn chưa
    if not Block.objects.filter(blocker=request.user, blocked_user=blocked_user).exists():
        Block.objects.create(blocker=request.user, blocked_user=blocked_user)
        return redirect('core:feed')
    return render(request, 'core/confirm_block_user.html', {'blocked_user': blocked_user})

@login_required
def unblock_user(request, user_id):
    blocked_user = User.objects.get(pk=user_id)

    # Kiểm tra xem đã chặn chưa
    try:
        block_entry = Block.objects.get(blocker=request.user, blocked_user=blocked_user)
        block_entry.delete()  # Xóa bản ghi chặn nếu tồn tại
    except Block.DoesNotExist:
        pass  # Nếu không tìm thấy bản ghi chặn, không cần làm gì cả

    # Điều hướng trở lại trang người dùng hoặc trang trước đó
    referer = request.META.get('HTTP_REFERER', None)
    if referer:
        return redirect(referer)
    else:
        return redirect('profiles:profile', pk=user_id)

def follow_page(request, page_id):
    if request.user.is_authenticated:
        try:
            page = Page.objects.get(id=page_id)
            if request.user in page.follower.all():
                page.follower.remove(request.user)
                is_following = False
            else:
                page.follower.add(request.user)
                is_following = True

            return JsonResponse({'success': True, 'is_following': is_following})
        except Page.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Page not found'})
    else:
        return JsonResponse({'success': False, 'error': 'User not authenticated'})

class DeleteChatRoom(View):
    def post(self, request, room_id):
        room = get_object_or_404(ChatMessage, id=room_id)
        if request.user.id == room.creator.id:
            room.delete()
        return redirect('core:feed')  # Điều hướng sau khi xóa

    def get(self, request, room_id):
        room = get_object_or_404(ChatMessage, id=room_id)
        if request.user.id == room.creator.id:
            room.delete()
        return redirect('core:feed')

class ManageGroupMembershipView(CreateView):
    def post(self, request, group_id, user_id, action):
        group = get_object_or_404(Group, id=group_id)
        user = get_object_or_404(User, id=user_id)
        if request.user == group.user:
            membership = GroupMembership.objects.get(user=user, group=group)
            if action == 'approve':
                membership.status = 'approved'
            elif action == 'reject':
                membership.status = 'rejected'
            membership.save()

        pending_memberships = GroupMembership.objects.filter(group=group, status='requested')
        return redirect('core:group_post_list', group_id=group.id)
        # return render(request, 'core/group_post_list.html', {'group': group, 'user': user, 'action': action, 'members': pending_memberships})
    
class ConfirmMembershipView(View):
    def get(self,request, user_id,group_id, action):
        # Lấy thông tin Membership dựa trên membership_id
        group = get_object_or_404(Group, id=group_id)
        membership = GroupMembership.objects.get(user=user_id, group=group_id)
        # message = MessageGroup.objects.get(user=user_id, group=group_id)
        
        if action == 'approved':
            membership.status = 'approved'
            membership.save()
            

            
        elif action == 'rejected':
            membership.status = 'rejected'
            membership.save()

        return redirect('core:group_post_list', group_id=group.id)

            
        
        # Chuyển hướng về trang gốc, chẳng hạn là trang chứa danh sách yêu cầu
    
class ListPendingMembershipsView(View):
    template_name = 'core/list_pending_memberships.html'  # Replace with your actual template path

    def get(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        
        # Get all pending membership requests for the group
        pending_memberships = GroupMembership.objects.filter(group=group, status='requested')

        return render(request, self.template_name, {'group': group, 'pending_memberships': pending_memberships})

class JoinGroupView(CreateView):
    def get(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        membership, created = GroupMembership.objects.get_or_create(user=request.user, group=group)
        
        if created:
            membership.status = 'requested'
            membership.save()
        
        # Kiểm tra xem người dùng hiện tại có phải là người tạo nhóm hay không
        if request.user == group.user:
            return redirect('core:group_post_list', group_id=group_id)
            # return redirect('core:membership-requests', group_id=group.id)
        else:
            # Lựa chọn một URL bạn muốn chuyển hướng người dùng trong trường hợp người tạo nhóm không thấy thông báo.
            # Ví dụ: return redirect('social:group_posts', group_id=group.id)
            return redirect('core:group_post_list', group_id=group_id) 
    
class LeaveGroupView(CreateView):
    def get(self, request, group_id):
        try:
            membership = GroupMembership.objects.get(user=request.user, group_id=group_id)
            membership.delete()  # Xóa mối quan hệ của người dùng với nhóm
        except GroupMembership.DoesNotExist:
            pass  # Người dùng không tham gia nhóm, không cần thực hiện gì

        return redirect('core:group_post_list', group_id=group_id) 


# def page_post_list(request, page_id):
   
#     page = Page.objects.get(id=page_id)  # Fetch the group based on group_id
#     page_posts = PagePost.objects.filter(page=page).order_by('-id')

#     context = {
#         "page": page,
#         "page_posts": page_posts,
#     }
#     return render(request, 'core/page_post_list.html', context)



# class ConfirmMembershipView(View):
#     def get(self,request, user_id,group_id, action):
#         # Lấy thông tin Membership dựa trên membership_id
#         membership = GroupMembership.objects.get(user=user_id, group=group_id)
#         message = MessageGroup.objects.get(user=user_id, group=group_id)
        
#         if action == 'approve':
#             membership.status = 'approved'
#             membership.save()

#             message.status = 'approved'
#             message.save()

#         elif action == 'reject':
#             membership.status = 'rejected'
#             membership.save()

#             message.status = 'rejected'
#             message.save()
        
#         # Chuyển hướng về trang gốc, chẳng hạn là trang chứa danh sách yêu cầu
#         return redirect('home')

@csrf_exempt
def like_page(request):
    id = request.GET['id']
    page = Page.objects.get(id=id)
    user = request.user
    bool = False

    if user in page.likes.all():
        page.likes.remove(user)
        bool = False
    else:
        page.likes.add(user)
        bool = True

        if page.user != request.user:
            send_notification(page.user, user, page, None, noti_new_like)

    data = {
        "bool":bool,
        'likes':page.likes.all().count()
    }
    return JsonResponse({"data":data})

@csrf_exempt
def like_post(request):

    id = request.GET['id']
    post = Post.objects.get(id=id)
    user = request.user
    bool = False 

    if user in post.likes.all():
        post.likes.remove(user)
        bool = False
    else:
        post.likes.add(user)
        bool = True 

        if post.user != request.user:
            send_notification(post.user, user, post, None, noti_new_like)

    data = {
        "bool":bool,
        'likes':post.likes.all().count()
    }
    return JsonResponse({"data":data})

@csrf_exempt
def comment_on_post(request):

    id = request.GET['id']
    comment = request.GET['comment']
    post = Post.objects.get(id=id)
    comment_count = Comment.objects.filter(post=post).count()
    user = request.user

    new_comment = Comment.objects.create(
        post=post,
        comment=comment,
        user=user
    )
    # Notifications system
    if new_comment != post.user:
        send_notification(post.user, user, post, new_comment, noti_new_comment)

    
    data = {
        "bool":True,
        'comment':new_comment.comment,
        "profile_image":new_comment.user.profile.image.url,
        "date":timesince(new_comment.date),
        "comment_id":new_comment.id,
        "post_id":new_comment.post.id,
        "comment_count":comment_count + int(1)
    }
    return JsonResponse({"data":data})



@csrf_exempt
def like_comment(request):

    id = request.GET['id']
    comment = Comment.objects.get(id=id)
    user = request.user
    bool = False 

    if user in comment.likes.all():
        comment.likes.remove(user)
        bool = False
    else:
        comment.likes.add(user)
        bool = True 

        # Notifications system
        if comment.user != user:
            send_notification(comment.user, user, comment.post, comment, noti_comment_liked)



    data = {
        "bool":bool,
        'likes':comment.likes.all().count()
    }
    return JsonResponse({"data":data})


def reply_comment(request):
    id = request.GET['id']
    reply = request.GET['reply']

    comment = Comment.objects.get(id=id)
    user = request.user

    new_reply = ReplyComment.objects.create(
        comment=comment,
        user=user,
        reply=reply,
    )
    if comment.user != user:
            send_notification(comment.user, user, comment.post, comment, noti_comment_replied)


    data = {
        "bool":True,
        'reply':new_reply.reply,
        "profile_image":new_reply.user.profile.image.url,
        "date":timesince(new_reply.date),
        "reply_id":new_reply.id,
        "post_id":new_reply.comment.post.id,
    }
    return JsonResponse({"data":data})

@csrf_exempt
def edit_comment(request):
    if request.method == "POST":
        comment_id = request.POST.get("id")
        edited_comment = request.POST.get("edited_comment")

        # Update the comment in the database
        comment = Comment.objects.get(id=comment_id)
        comment.comment = edited_comment
        comment.save()

        data = {
            "bool": True,
            "edited_comment": edited_comment,
        }

        return JsonResponse({"data": data})

@csrf_exempt
def delete_comment(request):
    id = request.GET['id']
    
    comment = Comment.objects.get(id=id, user=request.user)
    comment.delete()

    data = {
        "bool":True,
    }
    return JsonResponse({"data":data})


@csrf_exempt
def edit_reply(request):
    if request.method == "POST":
        reply_id = request.POST.get("id")
        edited_reply = request.POST.get("edited_reply")

        # Update the reply in the database
        reply = ReplyComment.objects.get(id=reply_id)
        reply.reply = edited_reply
        reply.save()

        data = {
            "bool": True,
            "edited_reply": edited_reply,
        }

        return JsonResponse({"data": data})

@csrf_exempt
def delete_reply(request):
    if request.method == 'GET':
        reply_id = request.GET.get('id', None)
        if reply_id:
            try:
                reply = ReplyComment.objects.get(id=reply_id, user=request.user)
                reply.delete()
                return JsonResponse({'success': True})
            except ReplyComment.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Reply not found or user does not have permission.'})

        return JsonResponse({'success': False, 'error': 'Reply ID not provided.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})





def add_friend(request):
    sender = request.user
    receiver_id = request.GET['id'] 
    bool = False

    if sender.id == int(receiver_id):
        return JsonResponse({'error': 'You cannot send a friend request to yourself.'})
    
    receiver = User.objects.get(id=receiver_id)
    
    try:
        friend_request = FriendRequest.objects.get(sender=sender, receiver=receiver)
        if friend_request:
            friend_request.delete()
        bool = False
        return JsonResponse({'error': 'Cancelled', 'bool':bool})
    except FriendRequest.DoesNotExist:
        friend_request = FriendRequest(sender=sender, receiver=receiver)
        friend_request.save()
        bool = True

        
        send_notification(receiver, sender, None, None, noti_friend_request)

        

        return JsonResponse({'success': 'Sent',  'bool':bool})



@csrf_exempt
def accept_friend_request(request):
    id = request.GET['id'] 

    receiver = request.user
    sender = User.objects.get(id=id)
    
    friend_request = FriendRequest.objects.filter(receiver=receiver, sender=sender).first()

    receiver.profile.friends.add(sender)
    sender.profile.friends.add(receiver)

    friend_request.delete()

    send_notification(sender, receiver, None, None, noti_friend_request_accepted)


    data = {
        "message":"Accepted",
        "bool":True,
    }
    
    return JsonResponse({'data': data})




@csrf_exempt
def reject_friend_request(request):
    id = request.GET['id'] 

    receiver = request.user
    sender = User.objects.get(id=id)
    
    friend_request = FriendRequest.objects.filter(receiver=receiver, sender=sender).first()
    friend_request.delete()

    data = {
        "message":"Rejected",
        "bool":True,
    }
    return JsonResponse({'data': data})


@csrf_exempt
def unfriend(request):
    sender = request.user
    friend_id = request.GET['id'] 
    bool = False

    if sender.id == int(friend_id):
        return JsonResponse({'error': 'You cannot unfriend yourself'})
    
    my_friend = User.objects.get(id=friend_id)
    
    if my_friend in sender.profile.friends.all():
        sender.profile.friends.remove(my_friend)
        my_friend.profile.friends.remove(sender)
        bool = True
        return JsonResponse({'success': 'Unfriend Successfull',  'bool':bool})
    

def search_users(request):
    query = request.GET.get('q')
    users_data = []
    current_user = request.user
    blocked_users = Block.objects.filter(blocker=current_user).values('blocked_user__id')
    blockers = Block.objects.filter(blocked_user=current_user).values('blocker__id')
    if query:
        # Search for users
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(full_name__icontains=query)
        ).exclude(
            Q(id__in=blocked_users) | Q(id__in=blockers)
        )
        

        for user in users:
            # if not Block.objects.filter(blocker=request.user, blocked_user=user).exists() and  Block.objects.filter(blocker=user, blocked_user=request.user).exists():
            try:
                profile = Profile.objects.get(user=user)
                profile_image = profile.image.url
                full_name = profile.full_name
            except Profile.DoesNotExist:
                profile_image = None
                full_name = None

            user_data = {
                'type': 'user',
                'username': user.username,
                'full_name': full_name,
                'email': user.email,
                'profile_image': profile_image,
            }
            users_data.append(user_data)

        # Search for posts
        posts = Post.objects.filter(
            Q(title__icontains=query)   # Assuming 'tags' is a field in your Post model
        )

        for post in posts:
            post_data = {
                'type': 'post',
                'title': post.title,
                'slug': post.slug,
                
                # Adjust this based on your actual Post model
            }
            users_data.append(post_data)
        
        groups = Group.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

        for group in groups:
            group_data = {
                'type': 'group',
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'image': group.image.url if group.image else None,
                'slug': group.slug,
            }
            users_data.append(group_data)

        # Search for pages
        pages = Page.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

        for page in pages:
            page_data = {
                'type': 'page',
                'id': page.id,
                'name': page.name,
                'description': page.description,
                'image': page.image.url if page.image else None,
                'slug': page.slug,
            }
            users_data.append(page_data)


    return JsonResponse({'results': users_data})
    


@login_required
def inbox(request):
    user_id = request.user

    chat_message = ChatMessage.objects.filter(
        id__in =  Subquery(
            User.objects.filter(
                Q(sender__reciever=user_id) |
                Q(reciever__sender=user_id)
            ).distinct().annotate(
                last_msg=Subquery(
                    ChatMessage.objects.filter(
                        Q(sender=OuterRef('id'),reciever=user_id) |
                        Q(reciever=OuterRef('id'),sender=user_id)
                    ).order_by('-id')[:1].values_list('id',flat=True) 
                )
            ).values_list('last_msg', flat=True).order_by("-id")
        )
    ).order_by("-id")
    
    context = {
        'chat_message': chat_message,
    }
    return render(request, 'chat/inbox.html', context)


@login_required
def inbox_detail(request, username):
    user_id = request.user
    message_list = ChatMessage.objects.filter(
        id__in =  Subquery(
            User.objects.filter(
                Q(sender__reciever=user_id) |
                Q(reciever__sender=user_id)
            ).distinct().annotate(
                last_msg=Subquery(
                    ChatMessage.objects.filter(
                        Q(sender=OuterRef('id'),reciever=user_id) |
                        Q(reciever=OuterRef('id'),sender=user_id)
                    ).order_by('-id')[:1].values_list('id',flat=True) 
                )
            ).values_list('last_msg', flat=True).order_by("-id")
        )
    ).order_by("-id")


    
    sender = request.user
    receiver = User.objects.get(username=username)
    receiver_details = User.objects.get(username=username)
    
    messages_detail = ChatMessage.objects.filter(
        Q(sender=sender, reciever=receiver) | Q(sender=receiver, reciever=sender)
    ).order_by("date")

    messages_detail.update(is_read=True)
    
    if messages_detail:
        r = messages_detail.first()
        reciever = User.objects.get(username=r.reciever)
    else:
        reciever = User.objects.get(username=username)

    context = {
        'message_detail': messages_detail,
        "reciever":reciever,
        "sender":sender,
        "receiver_details":receiver_details,
        "message_list":message_list,
    }
    return render(request, 'chat/inbox_detail.html', context)


# def block_user(request):
#     id = request.GET['id']
#     user = request.user
#     friend = User.objects.get(id=id)

#     if user.id == friend.id:
#         return JsonResponse({'error': 'You cannot block yourself'})


#     if friend in user.profile.friends.all():
#         user.profile.blocked.add(friend)
#         user.profile.friends.remove(friend)
#         friend.profile.friends.remove(user)
#     else:
#         return JsonResponse({'error': 'You cannot block someone that is not your friend'})

#     return JsonResponse({'success': 'User Blocked'})





def load_more_posts(request):
    all_posts = Post.objects.filter(active=True, visibility="Everyone").order_by('-date')

    # Paginate the posts
    paginator = Paginator(all_posts, 3)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    posts_data = []
    for post in page_obj:
        post_data = {
            'title': post.title,
            'profile_image': post.user.profile.image.url,
            'full_name': post.user.profile.full_name,
            'image_url': post.image.url if post.image else None,
            'video': post.video.url if post.video else None,
            'id': post.id,
            'id': post.id,
            'likes': post.likes.count(),
            'slug': post.slug,
            'views': post.views,
            'date': timesince(post.date),
        }
        posts_data.append(post_data)

    return JsonResponse({'posts': posts_data})


def group_inbox(request):
    groupchat = GroupChat.objects.filter(members__in=User.objects.filter(pk=request.user.pk), active=True)
    print("groupchat =============", groupchat)
    context = {
        'groupchat': groupchat,
    }
    return render(request, 'chat/group_inbox.html', context)


@login_required
def group_inbox_detail(request, slug):
    groupchat_list = GroupChat.objects.filter(members__in=User.objects.filter(pk=request.user.pk), active=True)
    groupchat = GroupChat.objects.get(slug=slug, active=True)
    group_messages = GroupChatMessage.objects.filter(groupchat=groupchat).order_by("id")

    if request.user not in groupchat.members.all():
        return redirect("core:join_group_chat_page", groupchat.slug)


    context = {
        'groupchat': groupchat,
        'group_name': groupchat.slug,
        'group_messages': group_messages,
        'groupchat_list': groupchat_list,
    }
    return render(request, 'chat/group_inbox_detail.html', context)

def join_group_chat_page(request, slug):
    groupchat = GroupChat.objects.get(slug=slug, active=True)

    context = {
        'groupchat': groupchat,
    }
    return render(request, 'chat/join_group_chat_page.html', context)


def join_group_chat(request, slug):
    groupchat = GroupChat.objects.get(slug=slug, active=True)

    if request.user in groupchat.members.all():
        return redirect("core:group_inbox_detail", groupchat.slug)
    
    groupchat.members.add(request.user)
    return redirect("core:group_inbox_detail", groupchat.slug)







def leave_group_chat(request, slug):
    groupchat = GroupChat.objects.get(slug=slug, active=True)

    if request.user in groupchat.members.all():
        groupchat.members.remove(request.user)
        return redirect("core:join_group_chat_page", groupchat.slug)

    return redirect("core:join_group_chat_page", groupchat.slug)

class ForgotPasswordView(View):
    form_class = ForgotPasswordForm
    template_name = 'userauths/forgot_password.html' 

    def get(self, request):
        form = ForgotPasswordForm()
        return render(request, self.template_name, { 'form': form, 'check_email': True, 'check_otp': True })

    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        first_filter = Q(email=request.POST.get('email'))
        second_filter = Q(email=request.session.get('email'))
        user = User.objects.filter(first_filter | second_filter).first()
        print(user)

        if not user:
            return render(request, self.template_name, { 'form': form, 'check_email': False, 'check_otp': True })
        elif 'send-otp' in request.POST:
            rs_form = ForgotPasswordForm(request.POST, initial={'email': request.POST.get('email')})
            if not request.session.get('email'):
                request.session['email'] = request.POST.get('email')
            code = random.randint(100000, 999999)
            OTP.objects.create(user=user, code=code, is_active=True)

            subject = 'Django social - OTP reset password'
            message = f'Your OTP is: {code}'
            from_email = EMAIL_HOST_USER
            recipient_list = [user.email]
            send_mail(subject, message, from_email, recipient_list)

            return render(request, self.template_name, { 'form': rs_form, 'email': request.POST.get('email') or request.session.get('email'), 'check_email': True, 'check_otp': True })
        else:
            otp = OTP.objects.filter(Q(is_active=True, user=user)).last()
            if otp.code == request.POST.get('otp'):
                print(f"otp is: {otp.code}", user.password)
                new_password = random_password()
                user.set_password(new_password)
                user.save()
                return render(request, self.template_name, { 
                    'form': form, 
                    'email': request.session.get('email'), 
                    'otp': otp.code,
                    'newpassword': new_password,
                    'check_email': True,
                    'check_otp': True
                })
            otp.is_active = False
            otp.save()
            return render(request, self.template_name, { 'form': form, 'email': request.session.get('email'), 'check_email': True, 'check_otp': False })

# Send mail
def random_password(length=20):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))

    return password
