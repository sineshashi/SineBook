from rest_framework import serializers
from django.contrib.auth.models import User
from .models import FieldPages, FriendRequest, HashTag, Like, PagePostList, PostShare, UserInterest, Page, SBUser, Post, Comment, Tags


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
        fields = ['user', 'mobile_number', 'date_of_birth', 'favourite_fields', 'your_city',
                  'image', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = validated_data.pop('user')
        user_instance = User.objects.create(**user)
        UserInterest.objects.create(user=user_instance)
        validated_data = {"user": user_instance, **validated_data}
        return super().create(validated_data)


class UpdateProfileSerialier(serializers.ModelSerializer):
    user = UpdateUserSerializer()

    class Meta:
        model = SBUser
        fields = ['user', 'mobile_number', 'date_of_birth', 'image', 'your_school', 'your_college', 'your_occupation', 'your_city', 'favourite_movies', 'favourite_books',
                  'tell_your_friends_about_you', 'favourite_fields', 'display_email', 'display_mobile', 'display_personal_info', 'display_friends', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        if validated_data.get('user') is None:
            return super().update(instance, validated_data)
        else:
            user = validated_data.pop('user')
            User.objects.filter(id=instance.user_id).update(**user)
            return super().update(instance, validated_data)


class RertriveWithOutIDProfileSerialier(serializers.ModelSerializer):
    user = UpdateUserSerializer()

    class Meta:
        model = SBUser
        fields = ['user', 'user_id', 'id', 'mobile_number', 'date_of_birth', 'image', 'your_school', 'your_college', 'your_occupation', 'your_city', 'favourite_movies', 'favourite_books',
                  'tell_your_friends_about_you', 'favourite_fields', 'display_email', 'display_mobile', 'display_personal_info', 'display_friends', 'created_at', 'updated_at']


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
        fields = ['id', 'user_id', 'user', 'mobile_number', 'date_of_birth', 'image', 'your_school', 'your_college',
                  'your_occupation', 'your_city', 'tell_your_friends_about_you', 'favourite_fields', 'favourite_movies', 'favourite_books', 'created_at', 'updated_at']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['tag_name']


class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['liker', 'post', 'liked_at']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'comment_on_which_user_can_comment',
                  'comment', 'commented_at', 'updated_at']

    def create(self, validated_data):
        comment = super().create(validated_data)
        post = comment.post
        post.number_of_comments += 1
        if comment.user_id != post.user_id:
            post.effective_number_of_comments += 1
        post.score = post.number_of_likes*0.20 + post.effective_number_of_comments*0.35 + post.number_of_shares*0.45
        post.save()
        return comment


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


class PageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['title', 'description', 'image', 'fields',
                  'tags', 'creator', 'members', 'created_at']

    def create(self, validated_data):
        page = super().create(validated_data)
        try:
            for tag in page.tags.all():
                hash_tag = HashTag.objects.get_or_create(tag=tag)
                hash_tag_instance = hash_tag[0]
                hash_tag_instance.pages.add(page)
        except:
            pass
        PagePostList.objects.create(page = page)
        for field in page.fields.all():
            field_instance_tuple = FieldPages.objects.get_or_create(field = field)
            field_instance = field_instance_tuple[0]
            field_instance.pages.add(page)
        return page


class PageRetrieveSerializerByMember(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['title', 'description', 'image', 'fields', 'tags', 'creator',
                  'members', 'followers', 'number_of_followers', 'created_at', 'updated_at']


class PageUpdateDestroyByCreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['title', 'description', 'image',
                  'fields', 'tags', 'members', 'updated_at']

    def update(self, instance, validated_data):
        if validated_data.get('tags') is not None:
            tags_list = validated_data['tags']
            try:
                for tag in tags_list:
                    hash_tag = HashTag.objects.get_or_create(tag=tag)
                    hash_tag_instance = hash_tag[0]
                    hash_tag_instance.pages.add(instance)
            except:
                pass
        return super().update(instance, validated_data)


class PageUpdateByMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['title', 'description', 'image',
                  'fields', 'tags', 'updated_at']

    def update(self, instance, validated_data):
        if validated_data.get('tags') is not None:
            tags_list = validated_data['tags']
            try:
                for tag in tags_list:
                    hash_tag = HashTag.objects.get_or_create(tag=tag)
                    hash_tag_instance = hash_tag[0]
                    hash_tag_instance.pages.add(instance)
            except:
                pass
        return super().update(instance, validated_data)


class RetrievePageByUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['title', 'description', 'image',
                  'number_of_followers', 'created_at', 'updated_at']

class PostShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostShare
        fields = ['sharing_post', 'shared_post', 'created_at']

class PostByUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['user', 'description', 'image',
                  'shared_post', 'tags', 'posted_at', 'updated_at']

    def create(self, validated_data):
        post = super().create(validated_data)
        if validated_data.get('tags') is not None:
            for tag in post.tags.all():
                hash_tag_tuple = HashTag.objects.get_or_create(tag_id=tag.id)
                hash_tag = hash_tag_tuple[0]
                hash_tag.posts.add(post)
        user_interest = UserInterest.objects.get(user_id = post.user_id)
        user_interest.posts.add(post)
        shared_post = post.shared_post
        if shared_post is not None:
            shared_post.number_of_shares += 1
            shared_post.score = shared_post.number_of_likes*0.20 + shared_post.effective_number_of_comments*0.35 + shared_post.number_of_shares*0.45
            shared_post.save()
            postshare_data = {"sharing_post": post, "shared_post":shared_post}
            serializer = PostShareSerializer(postshare_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return post


class PostByPageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['user', 'page', 'description', 'shared_post',
                  'image', 'tags', 'posted_at', 'updated_at']

    def create(self, validated_data):
        post = super().create(validated_data)
        try:
            for tag in post.tags.all():
                hash_tag_tuple = HashTag.objects.get_or_create(tag_id=tag.id)
                hash_tag = hash_tag_tuple[0]
                hash_tag.posts.add(post)
        except:
            pass
        shared_post = post.shared_post
        if shared_post is not None:
            shared_post.number_of_shares += 1
            shared_post.score = shared_post.number_of_likes*0.20 + shared_post.effective_number_of_comments*0.35 + shared_post.number_of_shares*0.45
            shared_post.save()
            postshare_data = {"sharing_post": post, "shared_post":shared_post}
            serializer = PostShareSerializer(postshare_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        page_post_tuple = PagePostList.objects.get_or_create(page = post.page)        
        page_post_instance = page_post_tuple[0]
        page_post_instance.posts.add(post)
        return post


class PostByUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'user', 'description', 'shared_post',
                  'image', 'posted_at', 'updated_at']


class PostByPageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'user', 'page', 'description', 'shared_post',
                  'image', 'posted_at', 'updated_at']


class PostByUserRetrieveByOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'user', 'description', 'image', 'shared_post', 'number_of_likes',
                  'number_of_comments', 'number_of_shares', 'posted_at', 'updated_at']
    #This and below serializers have been used in listing posts in feed.

class PostByPageRetrieveByOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'user', 'page', 'description', 'image', 'shared_post', 'number_of_likes',
                  'number_of_comments', 'number_of_shares', 'posted_at', 'updated_at']


class PostByUserRetrieveByPosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['user', 'description', 'image', 'shared_post', 'number_of_likes',
                  'number_of_comments', 'number_of_shares', 'likes', 'who_can_comment', 'who_can_see', 'posted_at', 'updated_at']


class PostByPageRetrieveByMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['user', 'page', 'description', 'image', 'shared_post', 'number_of_likes',
                  'number_of_comments', 'number_of_shares', 'likes', 'posted_at', 'updated_at']


class PostByUserUpdateDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['description', 'who_can_comment',
                  'who_can_see', 'tags', 'posted_at', 'updated_at']

    def update(self, instance, validated_data):
        if validated_data.get('tags') is not None:
            tags_list = validated_data['tags']
            try:
                for tag in tags_list:
                    hash_tag = HashTag.objects.get_or_create(tag=tag)
                    hash_tag_instance = hash_tag[0]
                    hash_tag_instance.posts.add(instance)
            except:
                pass
        score = instance.number_of_likes*0.20 + instance.effective_number_of_comments*0.35 + instance.number_of_shares*0.45
        validated_data = {"score": score, **validated_data}
        if instance.shared_post is not None:
            shared_post = instance.shared_post
            shared_post.score = shared_post.number_of_likes*0.20 + shared_post.effective_number_of_comments*0.35 + shared_post.number_of_shares*0.45
            shared_post.save()
        return super().update(instance, validated_data)


class PostByPageUpdateDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['description', 'tags', 'posted_at', 'updated_at']

    def update(self, instance, validated_data):
        if validated_data.get('tags') is not None:
            tags_list = validated_data['tags']
            try:
                for tag in tags_list:
                    hash_tag = HashTag.objects.get_or_create(tag=tag)
                    hash_tag_instance = hash_tag[0]
                    hash_tag_instance.posts.add(instance)
            except:
                pass
        score = instance.number_of_likes*0.20 + instance.effective_number_of_comments*0.35 + instance.number_of_shares*0.45
        validated_data = {"score": score, **validated_data}
        if instance.shared_post is not None:
            shared_post = instance.shared_post
            shared_post.score = shared_post.number_of_likes*0.20 + shared_post.effective_number_of_comments*0.35 + shared_post.number_of_shares*0.45
            shared_post.save()
        return super().update(instance, validated_data)
