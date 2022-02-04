from colorsys import ONE_THIRD
from turtle import ondrag
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

Display_Choices = (
    ('Public', 'Public'),
    ('Friends', 'Friends'),
    ('None', 'None')
)


class SBUser(models.Model):
    user = models.OneToOneField(
        User, blank=False, null=False, on_delete=models.CASCADE)
    mobile_number = PhoneNumberField()
    date_of_birth = models.DateField()
    image = models.ImageField(null=True, blank=True)
    your_first_school = models.CharField(blank=True, null=True, max_length=255)
    your_college = models.CharField(blank=True, null=True, max_length=255)
    your_occupation = models.CharField(blank=True, null=True, max_length=255)
    your_address = models.CharField(blank=True, null=True, max_length=255)
    favourite_movies = models.CharField(blank=True, null=True, max_length=255)
    favourite_books = models.CharField(blank=True, null=True, max_length=255)
    tell_your_friends_about_you = models.TextField(
        max_length=500, blank=True, null=True)
    friends = models.ManyToManyField("self", blank=True)
    display_email = models.CharField(
        choices=Display_Choices, max_length=255, default='Public')
    display_mobile = models.CharField(
        choices=Display_Choices, max_length=255, default='None')
    display_personal_info = models.CharField(
        choices=Display_Choices, max_length=255, default='Public')
    display_friends = models.CharField(
        choices=Display_Choices, max_length=255, default='Public')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.username



class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=200, blank=True, null=True)
    image = models.ImageField(null=True, blank=True)
    likes = models.ManyToManyField(
        User, blank=True, related_name="liking_users", through='Like')
    number_of_likes = models.IntegerField(
        validators=[MinValueValidator(0)], default=0)
    number_of_comments = models.IntegerField(
        validators=[MinValueValidator(0)], default=0)
    who_can_see = models.CharField(
        choices=Display_Choices, max_length=255, default='Public')
    who_can_comment = models.CharField(
        choices=Display_Choices, max_length=255, default='Public')
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def number_of_likes(self):
        self.number_of_likes = self.likes.all().count()
        return self.number_of_likes

    def number_of_comments(self):
        self.number_of_comments = Comment.objects.filter(
            post_id=self.id).count()
        return self.number_of_comments


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_on_which_user_can_comment = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='comment_object')
    comment = models.TextField(max_length=255)
    likes = models.ManyToManyField(
        User, blank=True, related_name="comment_likers")
    number_of_likes = models.IntegerField(
        validators=[MinValueValidator(0)], default=0)
    commented_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def number_of_likes(self):
        self.number_of_likes = self.likes.all().count()
        return self.number_of_likes
    class Meta:
        ordering = ['-commented_at']


class FriendRequest(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sender")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sine_book_user")
    requested_at = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    liker = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-liked_at']

class LikedOrCommentedPosts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liker_or_commentor')
    likes = models.ManyToManyField(Like, blank=True, related_name="liked_posts")
    comments = models.ManyToManyField(Comment, blank=True, related_name="commented_posts")
    def likes(self):
        self.likes = Like.objects.filter(liker = self.user)
        return self.likes
    def comments(self):
        self.comments = Comment.objects.filter(user=self.user)
        return self.comments
