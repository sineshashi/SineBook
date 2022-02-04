from rest_framework import serializers
from django.contrib.auth.models import User
from .models import FriendRequest, LikedOrCommentedPosts, SBUser, Post, Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']


class RegisterSBUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = SBUser
        fields = ['user', 'mobile_number', 'date_of_birth',
                  'image', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = validated_data.pop('user')
        user_instance = User.objects.create(**user)
        LikedOrCommentedPosts.objects.create(user = user_instance)
        return SBUser.objects.create(user=user_instance, **validated_data)


class UpdateProfileSerialier(serializers.ModelSerializer):
    user = UpdateUserSerializer()

    class Meta:
        model = SBUser
        fields = ['user', 'mobile_number', 'date_of_birth', 'image', 'your_first_school', 'your_college', 'your_occupation', 'your_address', 'favourite_movies', 'favourite_books',
                  'tell_your_friends_about_you', 'display_email', 'display_mobile', 'display_personal_info', 'display_friends', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        if validated_data.get('user') is None:
            return super().update(instance, validated_data)
        else:
            user = validated_data.pop('user')
            User.objects.filter(id=instance.user_id).update(**user)
            return super().update(instance, validated_data)


class EmailLessUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ListFriendsSerializer(serializers.ModelSerializer):
    user = EmailLessUserSerializer()

    class Meta:
        model = SBUser
        fields = ['id', 'user_id', 'user', 'image', 'created_at', 'updated_at']


class RetrieveProfileSerializer(serializers.ModelSerializer):
    user = UpdateUserSerializer()

    class Meta:
        model = SBUser
        fields = ['id', 'user_id', 'user', 'mobile_number', 'date_of_birth', 'image', 'your_first_school', 'your_college',
                  'your_occupation', 'your_address', 'tell_your_friends_about_you', 'favourite_movies', 'favourite_books', 'created_at', 'updated_at']


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['user', 'description', 'image', 'posted_at', 'updated_at']




class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['user', 'post', 'comment_on_which_user_can_comment',
                  'comment', 'commented_at', 'updated_at']



class PostRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['user', 'description', 'image', 'number_of_likes',
                  'number_of_comments', 'posted_at', 'updated_at']
        # We have used same serializer for listing posts.


class PostRDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['user', 'description', 'image', 'likes', 'number_of_likes', 'number_of_comments',
                  'who_can_comment', 'who_can_see', 'posted_at', 'updated_at']


class PostUSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['description', 'image', 'who_can_comment',
                  'who_can_see', 'posted_at', 'updated_at']


class CommentLRDSerializerForPoster(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['user', 'post', 'comment_on_which_user_can_comment', 'likes', 'number_of_likes',
                  'comment', 'commented_at', 'updated_at']


class CommentLRSerializerForUser(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['user', 'post', 'comment_on_which_user_can_comment', 'number_of_likes',
                  'comment', 'commented_at', 'updated_at']


class CommentRDSerializerForCommentor(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['user', 'post', 'comment_on_which_user_can_comment', 'likes', 'number_of_likes',
                  'comment', 'commented_at', 'updated_at']


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['comment', 'updated_at']


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['sender', 'user', 'requested_at']



