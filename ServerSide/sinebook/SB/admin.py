from django.contrib import admin
from .models import FavouriteField, FieldPages, Like, PagePostList, PostShare, UserInterest, Page, SBUser, Post, Comment, FriendRequest, HashTag


@admin.register(SBUser)
class SBUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'user', 'mobile_number', 'date_of_birth', 'image', 'your_school', 'your_college', 'your_occupation', 'your_city', 'favourite_movies', 'favourite_books',
                    'tell_your_friends_about_you', 'display_email', 'display_mobile', 'display_personal_info', 'display_friends', 'created_at', 'updated_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'page', 'description', 'image', 'shared_post', 'number_of_likes', 'number_of_shares',
                    'number_of_comments', 'effective_number_of_comments', 'score', 'who_can_see', 'who_can_comment', 'posted_at', 'updated_at']



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

@admin.register(UserInterest)
class LikedOrCommentedPostsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user']

@admin.register(HashTag)
class HashTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'tag']

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'image', 'creator', 'description', 'number_of_followers', 'created_at', 'updated_at']

@admin.register(FavouriteField)
class FavouriteFieldsAdmin(admin.ModelAdmin):
    list_display = ['field']

@admin.register(PagePostList)
class PagePostListAdmin(admin.ModelAdmin):
    list_display = ['id', 'page']

@admin.register(PostShare)
class PostShareAdmin(admin.ModelAdmin):
    list_display = ['id', 'sharing_post', 'shared_post']

@admin.register(FieldPages)
class FieldPageAdmin(admin.ModelAdmin):
    list_display = ['id', 'field']

