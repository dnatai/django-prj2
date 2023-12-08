from django.contrib import admin
from core.models import Post, Gallery, Friend, FriendRequest, Comment, ReplyComment, Notification, GroupPost, Page, PagePost, Group, ChatMessage, GroupMembership, MessageGroup,GroupChat,GroupChatMessage, Block
# Register your models here.

class GalleryAdminTab(admin.TabularInline):
    model = Gallery

class PostAdmin(admin.ModelAdmin):
    inlines = [GalleryAdminTab]
    list_editable = ['active']
    list_display = ['thumbnail', 'user', 'title', 'visibility','active']
    prepopulated_fields = {"slug": ("title", )}

class GalleryAdmin(admin.ModelAdmin):
    list_editable = ['active']
    list_display = ['thumbnail', 'post', 'active']

class FriendRequestAdmin(admin.ModelAdmin):
    list_editable = ['status']
    list_display = ['sender', 'receiver', 'status']

class FriendAdmin(admin.ModelAdmin):
    list_display = ['user', 'friend']

class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'comment', 'active']


class ReplyAdmin(admin.ModelAdmin):
    list_display = ['user', 'comment', 'active']

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'sender', 'post', 'comment', 'is_read']

class GroupPostTabAdmin(admin.TabularInline):
    model = GroupPost

class GroupAdmin(admin.ModelAdmin):
    # inlines = [GroupPostTabAdmin]
    list_editable = ['user', 'name', 'visibility']
    list_display = ['thumbnail', 'user', 'name', 'visibility']
    prepopulated_fields = {"slug": ("name", )}

class PageAdmin(admin.ModelAdmin):
    # inlines = [GroupPostTabAdmin]
    list_editable = ['user', 'name', 'visibility']
    list_display = ['thumbnail', 'user', 'name', 'visibility']
    prepopulated_fields = {"slug": ("name", )}

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'reciever', 'message', 'is_read']
    list_editable = ['message']

class GroupChatAdmin(admin.ModelAdmin):
    list_display = ['name', 'description' ,'host','active']
    prepopulated_fields = {"slug": ("name", )}
    

class GroupChatMessageAdmin(admin.ModelAdmin):
    list_display = ['groupchat', 'sender', 'message' ,'is_read','date']

admin.site.register(Post, PostAdmin)
admin.site.register(Gallery, GalleryAdmin)
admin.site.register(Friend, FriendAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(ReplyComment, ReplyAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(GroupPost)
admin.site.register(PagePost)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(GroupMembership)
admin.site.register(MessageGroup)
admin.site.register(GroupChatMessage, GroupChatMessageAdmin)
admin.site.register(GroupChat, GroupChatAdmin)
admin.site.register(Block)
