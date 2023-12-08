from django.db import models
from userauths.models import User, Profile, user_directory_path
from shortuuid.django_fields import ShortUUIDField
from django.utils.text import slugify
import shortuuid
from django.utils.html import mark_safe




# Create your models here.

VISIBILITY = (
    ("Only Me", "Only Me"),
    ("Everyone", "Everyone"),
)

FRIEND_REQUEST = (
    ("pending","pending"),
    ("accept","Accept"),
    ("reject","Reject"),
)

NOTIFICATION_TYPE = (
    ("Friend Request", "Friend Request"),
    ("Friend Request Accepted", "Friend Request Accepted"),
    ("New Follower", "New Follower"),
    ("New Like", "New Like"),
    ("New Comment", "New Comment"),
    ("Comment Liked", "Comment Liked"),
    ("Comment Replied", "Comment Replied"),
)

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, blank=True, null=True)
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    video = models.FileField(upload_to=user_directory_path, blank=True, null=True)
    visibility = models.CharField(max_length=100, choices=VISIBILITY, default="Everyone")
    pid = ShortUUIDField(length=7, max_length=25, alphabet='abcdefghijklmnopqrstuvwxyz')
    likes = models.ManyToManyField(User, blank=True, related_name="likes")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    views = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Post"
    
    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + "-" + str(uniqueid.lower())
        super(Post, self).save(*args, **kwargs) 

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))
    
    def gallery_images(self):
        return Gallery.objects.filter(post=self)
    
    def title_len_count(self):
        return len(self.title)
    
    def galley_img_count(self):
        return Gallery.objects.filter(post=self).count()

    def post_comments(self):
        comments = Comment.objects.filter(post=self, active=True)
        return comments
    
    def post_comments_count(self):
        comments_count = Comment.objects.filter(post=self, active=True).count()
        return comments_count
    

class Gallery(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="gallery", null=True, blank=True)
    active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.post)
    
    class Meta:
        verbose_name_plural = 'Gallery'

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))

class FriendRequest(models.Model):
    fid = ShortUUIDField(length=7, max_length=25, alphabet='abcdefghijklmnopqrstuvwxyz')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="request_sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="request_receiver")
    status = models.CharField(max_length=100, default="pending", choices=FRIEND_REQUEST)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.sender)
    
    class Meta:
        verbose_name_plural = 'Friend Request'

class Block(models.Model):
    blocker = models.ForeignKey(User, related_name='blocker', on_delete=models.CASCADE)
    blocked_user = models.ForeignKey(User, related_name='blocked_user', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('blocker', 'blocked_user')
    
    

class Friend(models.Model):
    fid = ShortUUIDField(length=7, max_length=25, alphabet='abcdefghijklmnopqrstuvwxyz')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend")

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)
    
    class Meta:
        verbose_name_plural = 'Friend'

class Comment(models.Model):
    cid = ShortUUIDField(length=7, max_length=25, alphabet='abcdefghijklmnopqrstuvwxyz')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commnet_user")
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name="commnet_likes")
    comment = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.post)
    
    class Meta:
        verbose_name_plural = 'Comment'

    def comment_replies(self):
        comment_replies = ReplyComment.objects.filter(comment=self, active=True)
        return comment_replies

class ReplyComment(models.Model):
    cid = ShortUUIDField(length=7, max_length=25, alphabet='abcdefghijklmnopqrstuvwxyz')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reply_user")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)
    reply = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.comment)
    
    class Meta:
        verbose_name_plural = 'Reply Comment'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="noti_user")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="noti_sender")
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.SET_NULL, null=True, blank=True)
    notification_type = models.CharField(max_length=500, choices=NOTIFICATION_TYPE)
    is_read = models.BooleanField(default=False)
    nid = ShortUUIDField(length=7, max_length=25, alphabet='abcdefghijklmnopqrstuvwxyz')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)
    
    class Meta:
        verbose_name_plural = 'Notification'

class Group(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group")
    member = models.ManyToManyField(User, blank=True, related_name="members")

    description = models.TextField(max_length=500, blank=True, null=True)
    name = models.CharField(max_length=500, blank=True, null=True)
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True,default="cover.jpg")
    image2 = models.ImageField(upload_to=user_directory_path, blank=True, null=True,default="cover.jpg")
    visibility = models.CharField(max_length=100, choices=VISIBILITY, default="Everyone")
    gid = ShortUUIDField(length=7, max_length=25, alphabet='abcdefghijklmnopqrstuvwxyz')
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    views = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.user.username
        
    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:2]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.name) + '-' + uniqueid

        super(Group, self).save(*args, **kwargs)
    
    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))

class GroupPost(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, blank=True, null=True)
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    video = models.FileField(upload_to=user_directory_path, blank=True, null=True)
    visibility = models.CharField(max_length=100, choices=VISIBILITY, default="Everyone")
    pid = ShortUUIDField(length=7, max_length=25, alphabet='abcdefghijklmnopqrstuvwxyz')
    likes = models.ManyToManyField(User, blank=True, related_name="group_post_likes")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    views = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return self.user.username
        
    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + "-" + str(uniqueid.lower())
        super(GroupPost, self).save(*args, **kwargs) 
    
    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))


class Page(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="page_user")
    follower = models.ManyToManyField(User, related_name="page_menber")
    likes = models.ManyToManyField(User, blank=True, related_name="page_likes")
    description = models.TextField(max_length=500, blank=True, null=True)
    name = models.CharField(max_length=500, blank=True, null=True)
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    image_page = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    video = models.FileField(upload_to=user_directory_path, blank=True, null=True)
    visibility = models.CharField(max_length=100, choices=VISIBILITY, default="Everyone")
    pid = ShortUUIDField(length=7, max_length=25, alphabet='abcdefghijklmnopqrstuvwxyz')
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    views = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.user.username
        
    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:2]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.name) + '-' + uniqueid

        super(Page, self).save(*args, **kwargs)
    
    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))


class PagePost(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, blank=True, null=True)
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    video = models.FileField(upload_to=user_directory_path, blank=True, null=True)
    visibility = models.CharField(max_length=100, choices=VISIBILITY, default="Everyone")
    pid = ShortUUIDField(length=7, max_length=25, alphabet='abcdefghijklmnopqrstuvwxyz')
    likes = models.ManyToManyField(User, blank=True, related_name="page_post_likes")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    views = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return self.user.username
        
    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:2]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + '-' + uniqueid

        super(PagePost, self).save(*args, **kwargs)
    
    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="chat_user")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sender")
    reciever = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="reciever")
    message = models.CharField(max_length=10000000000)
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    mid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")
    
    def __str__(self):
        return self.user.username
    
    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Personal Chat"

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))
    
    
    
class GroupChat(models.Model):
    name = models.CharField(max_length=1000)
    description = models.CharField(max_length=10000)
    images = models.FileField(upload_to="group_chat", blank=True, null=True)
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="group_host")
    members = models.ManyToManyField(User, related_name="group_chat_members")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Group Chat"
    
    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.name) + "-" + str(uniqueid.lower())
        super(GroupChat, self).save(*args, **kwargs) 

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))
    
    def last_message(self):
        last_message = GroupChatMessage.objects.filter(groupchat=self).order_by("-id").first()
        return last_message

class GroupChatMessage(models.Model):
    groupchat = models.ForeignKey(GroupChat, on_delete=models.SET_NULL, null=True, related_name="group_chat")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="group_chat_message_sender")
    message = models.CharField(max_length=100000)
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    mid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")
    
    
    def __str__(self):
        return self.groupchat.name
    
    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Group Chat Messages"

# class GroupMenber(models.Model):
#     group = models.ForeignKey(Group, related_name="member", on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="user-group")

#     def __str__(self):
#         return self.user.username

class GroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('requested', 'Requested'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='requested')
    is_creator = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} | {self.group}"
    
class MessageGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE) 
    message = models.TextField()
    status = models.CharField(max_length=20, choices=[('requested', 'Requested'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='requested')
    post = models.ForeignKey(
    GroupPost, 
    on_delete=models.CASCADE,
    null=True,
    blank=True
  )

class JoinRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Request from {self.user} to join {self.group}"
    

class OTP(models.Model):
    code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='otps', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    
    def getCode(self):
        return self.code
    
