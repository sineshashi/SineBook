from django.contrib import admin
from .models import Like, LikedOrCommentedPosts, SBUser, Post, Comment, FriendRequest, HashTag


@admin.register(SBUser)
class SBUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'user', 'mobile_number', 'date_of_birth', 'image', 'your_first_school', 'your_college', 'your_occupation', 'your_address', 'favourite_movies', 'favourite_books',
                    'tell_your_friends_about_you', 'display_email', 'display_mobile', 'display_personal_info', 'display_friends', 'created_at', 'updated_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'description', 'image', 'number_of_likes',
                    'number_of_comments', 'who_can_see', 'who_can_comment', 'posted_at', 'updated_at']



@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'comment_on_which_user_can_comment',
                    'comment', 'number_of_likes', 'commented_at', 'updated_at']


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'user', 'requested_at']

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'liker', 'post', 'liked_at']

@admin.register(LikedOrCommentedPosts)
class LikedOrCommentedPostsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'likes', 'comments']

@admin.register(HashTag)
class HashTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'tag_name']