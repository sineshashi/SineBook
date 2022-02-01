from django.contrib import admin
from .models import SBUser, Post, Comment, FriendRequest


@admin.register(SBUser)
class SBUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'user', 'mobile_number', 'date_of_birth', 'image', 'your_first_school', 'your_college', 'your_occupation', 'your_address', 'favourite_movies', 'favourite_books',
                    'tell_your_friends_about_you', 'display_email', 'display_mobile', 'display_personal_info', 'display_friends', 'created_at', 'updated_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'description', 'image', 'total_number_of_likes',
                    'total_number_of_comments', 'who_can_see', 'who_can_comment', 'posted_at', 'updated_at']

    def total_number_of_likes(self, instance):
        likes_count = instance.likes.all().count()
        Post.objects.filter(id= instance.id).update(number_of_likes = likes_count)
        return likes_count

    def total_number_of_comments(self, instance):
        comment_count = Comment.objects.filter(post_id=instance.id).count()
        Post.objects.filter(id = instance.id).update(number_of_comments = comment_count)
        return comment_count


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'comment_on_which_user_can_comment',
                    'comment', 'total_number_of_likes', 'commented_at', 'updated_at']

    def total_number_of_likes(self, instance):
        likes_count = instance.likes.all().count()
        Comment.objects.filter(id = instance.id).update(number_of_likes = likes_count)
        return likes_count
@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'user', 'requested_at']