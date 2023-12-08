from django import forms
from .models import Group, GroupPost, Page, PagePost, GroupChat, Post, Comment
from userauths.models import User
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'image', 'image2', 'visibility']

class GroupPostForm(forms.ModelForm):
    class Meta:
        model = GroupPost
        fields = ['title', 'image', 'visibility']

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['name', 'description', 'image', 'image_page', 'visibility']

class PagePostForm(forms.ModelForm):
    class Meta:
        model = PagePost
        fields = ['title', 'image', 'visibility']

class CreateGroupChatForm(forms.ModelForm):
    class Meta:
        model = GroupChat
        fields = ['name', 'description', 'images']  # Add or remove fields as needed

    def __init__(self, *args, **kwargs):
        super(CreateGroupChatForm, self).__init__(*args, **kwargs)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'image', 'visibility']

    # Add this method to clean and validate the uploaded files
    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')

        # Check if either image or video is provided
        if not image and not video:
            raise forms.ValidationError("Please provide either an image or a video.")

        return cleaned_data
    
class ForgotPasswordForm(forms.ModelForm):
    otp = forms.CharField(max_length=6, label='OTP', required=False)
    class Meta:
        model = User
        fields = ['email', 'otp']

