from django.urls import path
from core.views import index, JoinGroupView, LeaveGroupView, ManageGroupMembershipView,ListPendingMembershipsView, ConfirmMembershipView, delete_post, ForgotPasswordView
from core import views

app_name = "core"

urlpatterns = [
    path("",index, name="feed"),
    path("post/<slug:slug>/", views.post_detail, name="post-detail"),

    path("create-post/", views.create_post, name="create-post"),
    path("like-post/", views.like_post, name="like-post"),
    path("comment-post/", views.comment_on_post, name="comment-post"),
    path("like-comment/", views.like_comment, name="like-comment"),
    path("reply-comment/", views.reply_comment, name="reply-comment"),
    path("delete-comment/", views.delete_comment, name="delete-comment"),
    path('delete_post/', views.delete_post, name='delete_post'),
    path("add-friend/", views.add_friend, name="add-friend"),
    path("accept-friend-request/", views.accept_friend_request, name="accept-friend-request"),
    path("reject-friend-request/", views.reject_friend_request, name="reject-friend-request"),
    path("unfriend/", views.unfriend, name="unfriend"),
    path('delete-reply/', views.delete_reply, name='delete-reply'),
    path("like-page/", views.like_page, name="like-page"),
    path('edit-comment/', views.edit_comment, name='edit_comment'),
    path('delete_post/<slug:slug>/', views.delete_post, name='delete_post'),
    path('update_post/<slug:slug>/', views.update_post, name='update_post'),
    path('edit-reply/', views.edit_reply, name='edit_reply'),
    path('unblock_user/<int:user_id>/', views.unblock_user, name='unblock_user'),

    path('group/<int:group_id>/post-list/', views.group_post_list, name='group_post_list'),
    path('group/<int:group_id>/create-post/', views.create_group_post, name='create_group_post'),
    path('create-group/', views.create_group, name='create-group'),
    path("group-page/<id>/",views.group_index, name="group-page"),
    path('join-group/<int:group_id>/', JoinGroupView.as_view(), name='join-group'),
    path('leave-group/<int:group_id>/', LeaveGroupView.as_view(), name='leave-group'),
    path('manage-membership/<int:group_id>/<int:user_id>/<str:action>/', ManageGroupMembershipView.as_view(), name='manage-membership'),
    path('pending-memberships/<int:group_id>/', ListPendingMembershipsView.as_view(), name='pending-memberships'),
    path('confirm-membership/<int:user_id>/<str:action>/<int:group_id>/', ConfirmMembershipView.as_view(), name='confirm-membership'),
    path('delete_group/<int:group_id>/', views.delete_group, name='delete_group'),
    path('update_group/<int:group_id>/', views.update_group, name='update_group'),
    path('follow_user/<str:username>/', views.follow_user, name='follow_user'),
    path('groups/<int:group_id>/leave/', LeaveGroupView.as_view(), name='leave-group'),
    path('update_group_post/<int:group_id>/', views.update_group_post, name='update_group_post'),
    path('delete_group_post/<int:group_id>/', views.delete_group_post, name='delete_group_post'),
    path('list_groups/', views.list_groups, name='list_groups'),
     path('list_non_friends/', views.list_non_friends, name='list_non_friends'),

    path('page/<int:page_id>/post-list/', views.page_post_list, name='page_post_list'),
    #path('page/<int:page_id>/create-post/', views.create_page_post, name='create_page_post'),
    path('create-page/', views.create_page, name='create-page'),
    path('update_page/<int:page_id>/', views.update_page, name='update_page'),
    path('delete_page/<int:page_id>/', views.delete_page, name='delete_page'),
    path('page/<int:page_id>/create-posts/', views.create_page_post, name='create_page_post'),
    path('follow/<int:page_id>/', views.follow_page, name='follow-page'),
    path('update_page_post/<int:page_id>/', views.update_page_post, name='update_page_post'),
    path('delete_page_post/<int:page_id>/', views.delete_page_post, name='delete_page_post'),
    # path('block-user/', views.block_user, name='block_user'),
    # path('unblock/<str:username>/', views.unblock_user, name='unblock-user'),
    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('list_pages/', views.list_pages, name='list_pages'),
    
    path("core/inbox/", views.inbox, name="inbox"),
    path("core/inbox/<username>/", views.inbox_detail, name="inbox_detail"),
    path('search/', views.search_users, name='search_users'),


    # Group CHat
    path("core/group-inbox/", views.group_inbox, name="group_inbox"),
    path("core/group-inbox/<slug:slug>/", views.group_inbox_detail, name="group_inbox_detail"),
    path("create-group-inbox/", views.create_group_inbox, name="create-group-inbox"),

    # Join & leave Group
    path("core/join-group-page/<slug:slug>/", views.join_group_chat_page, name="join_group_chat_page"),
    path("core/join-group/<slug:slug>/", views.join_group_chat, name="join_group"),
    path("core/leave-group/<slug:slug>/", views.leave_group_chat, name="leave_group_chat"),

    path('forgot_password/', ForgotPasswordView.as_view(), name='forgot_password'),
]


