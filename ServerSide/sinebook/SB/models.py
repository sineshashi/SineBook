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


class FavouriteField(models.Model):
    field = models.CharField(max_length=255)


class Tags(models.Model):
    tag_name = models.CharField(max_length=500, unique=True)

    def __str__(self):
        return self.tag_name


class Page(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=5000)
    image = models.ImageField(null=True, blank=True)
    fields = models.ManyToManyField(
        FavouriteField, related_name="page_related_fields")
    tags = models.ManyToManyField(Tags, blank=True, related_name="page_tags")
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="page_creator")
    members = models.ManyToManyField(
        User, blank=True, related_name="page_members")
    followers = models.ManyToManyField(
        User, blank=True, related_name="page_followers")
    number_of_followers = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class SBUser(models.Model):
    user = models.OneToOneField(
        User, blank=False, null=False, on_delete=models.CASCADE)
    mobile_number = PhoneNumberField(unique=True)
    date_of_birth = models.DateField()
    image = models.ImageField(null=True, blank=True)
    your_first_school = models.CharField(blank=True, null=True, max_length=255)
    your_college = models.CharField(blank=True, null=True, max_length=255)
    your_occupation = models.CharField(blank=True, null=True, max_length=255)
    your_address = models.CharField(blank=True, null=True, max_length=255)
    favourite_movies = models.CharField(blank=True, null=True, max_length=255)
    favourite_books = models.CharField(blank=True, null=True, max_length=255)
    favourite_fields = models.ManyToManyField(
        FavouriteField, blank=True, related_name="user_favourite_fields")
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
    page = models.ForeignKey(Page, on_delete=models.CASCADE,
                             related_name="posting_page", null=True, blank=True)
    description = models.TextField(max_length=200, blank=True, null=True)
    image = models.ImageField(null=True, blank=True)
    shared_post = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True, related_name="sharing_post")
    likes = models.ManyToManyField(
        User, blank=True, related_name="liking_users", through='Like')
    number_of_likes = models.IntegerField(
        validators=[MinValueValidator(0)], default=0)
    number_of_comments = models.IntegerField(
        validators=[MinValueValidator(0)], default=0)
    number_of_shares = models.IntegerField(
        validators=[MinValueValidator(0)], default=0)
    effective_number_of_comments = models.IntegerField(
        validators=[MinValueValidator(0)], default=0)
    who_can_see = models.CharField(
        choices=Display_Choices, max_length=255, default='Public')
    who_can_comment = models.CharField(
        choices=Display_Choices, max_length=255, default='Public')
    tags = models.ManyToManyField(Tags, blank=True, related_name="post_tags")
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def score(self):
        return self.number_of_likes*0.25 + self.effective_number_of_comments*0.35 + self.number_of_shares*0.40

class HashTag(models.Model):
    tag = models.ForeignKey(Tags, on_delete=models.DO_NOTHING, null=True)
    posts = models.ManyToManyField(
        Post, blank=True, related_name="tagged_posts")
    pages = models.ManyToManyField(
        Page, blank=True, related_name="tagged_pages")

    def __str__(self):
        return self.tag.tag_name


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


    class Meta:
        ordering = ['-commented_at']
    def save(self, *args, **kwargs):
        data = super().save(*args, **kwargs)
        user_interest_tuple = UserInterest.objects.get_or_create(user = self.user)
        user_interest = user_interest_tuple[0]
        user_interest.comments.add(self)
        return data


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
    def save(self, *args, **kwargs):
        data = super().save(*args, **kwargs)
        user_interest_tuple = UserInterest.objects.get_or_create(user = self.liker)
        user_interest = user_interest_tuple[0]
        user_interest.likes.add(self)
        return data

class UserInterest(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='liker_or_commentor')
    likes = models.ManyToManyField(
        Like, blank=True, related_name="liked_posts")
    comments = models.ManyToManyField(
        Comment, blank=True, related_name="commented_posts")
    shares = models.ManyToManyField(Post, blank=True, related_name="shares")
    followed_pages = models.ManyToManyField(
        Page, blank=True, related_name="followed_pages")

