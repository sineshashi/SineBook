from django.contrib.auth.hashers import make_password
from .models import FieldPages, FriendRequest, HashTag, PagePostList, UserInterest, Page, SBUser, Post, Comment, Tags, Like
from django.contrib.auth.models import User
from rest_framework import generics, status
from .serializers import (FriendRequestSerializer, PageCreateSerializer, PageRetrieveSerializerByMember,
                          PageUpdateByMemberSerializer, PageUpdateDestroyByCreatorSerializer, PostByPageCreateSerializer, PostByPageListSerializer, PostByPageRetrieveByMemberSerializer, PostByPageRetrieveByOtherSerializer, PostByPageUpdateDestroySerializer, PostByUserCreateSerializer, PostByUserListSerializer, PostByUserRetrieveByOtherSerializer, PostByUserRetrieveByPosterSerializer, PostByUserUpdateDestroySerializer, PostLikeSerializer, RegisterSBUserSerializer,
                          RertriveWithOutIDProfileSerialier, RetrievePageByUserSerializer, UpdateProfileSerialier,
                          CommentSerializer,
                          CommentLRDSerializerForPoster, CommentLRSerializerForUser, CommentRDSerializerForCommentor,
                          CommentUpdateSerializer,
                          RetrieveProfileSerializer, ListFriendsSerializer, UserSerializer)
from rest_framework.exceptions import NotAcceptable, NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import json
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
from django.utils import timezone


class RegisterUserView(generics.CreateAPIView):
    '''
    It creates user with request.data={
        "user":{
            "first_name": " ",
            "last_name": " ",
            "email": " ",
            "password": "",
            "confirm_password": " "
        },
        "mobile_number": " ",
        "date_of_birth" : " ",
        "image": " ",
        "favourite_fields": [],
        "your_city": " "
    }
    It automatically sets username = email.
    '''

    def create(self, request, *args, **kwargs):
        if len(request.data) == 0:
            raise NotAcceptable(detail="No data provided")
        if request.data.get('user') is None:
            raise NotAcceptable(detail="user data not provided")
        userdata = request.data['user']
        if userdata.get('first_name') is None:
            raise NotAcceptable(detail="First Name not provided.")
        if userdata.get('last_name') is None:
            raise NotAcceptable(detail="Last Name not provided.")
        if userdata.get('email') is None:
            raise NotAcceptable(detail="Email not provided.")
        if userdata.get('password') is None:
            raise NotAcceptable(detail="Password not provided.")
        if userdata.get('confirm_password') is None:
            raise NotAcceptable(detail="Confirm Password not provided.")
        if request.data.get('mobile_number') is None:
            raise NotAcceptable("Mobile Number not provided.")
        if request.data.get('date_of_birth') is None:
            raise NotAcceptable(detail="Date of birth not provided.")
        if str(request.data['user']['password']).isnumeric():
            raise NotAcceptable(detail="password must contain alphabets also.")
        if str(request.data['user']['password']).isalpha():
            raise NotAcceptable(detail="Password must contain digits also.")
        if len(request.data['user']['password']) < 8:
            raise NotAcceptable(
                detail="Password must have at least 8 characters.")
        if userdata['password'] != userdata['confirm_password']:
            raise NotAcceptable(
                detail="Password and confirm password do not match.")
        password = userdata.get('password')
        password = make_password(password)
        del request.data['user']['confirm_password']
        if request.data.get('your_city') is not None:
            self.request['your_city'] = str(
                request.data['your_city']).capitalize()
        request.data['user']['password'] = password
        request.data['user']['username'] = request.data['user']['email']
        return super().create(request, *args, **kwargs)
    serializer_class = RegisterSBUserSerializer


class RetrieveProfileWithoutId(generics.ListAPIView):
    def get_queryset(self):
        return SBUser.objects.filter(user_id=self.request.user.id)
    serializer_class = RertriveWithOutIDProfileSerialier
    permission_classes = [IsAuthenticated]


class UpdateProfileView(generics.RetrieveUpdateDestroyAPIView):
    def update(self, request, *args, **kwargs):
        '''
        It updates the profile and takes SBUser id as primary key.
        There are many fields like favourite_books, your_city, you_college etc which can be filled here.
        '''
        if kwargs.get('pk') is None:
            raise NotAcceptable(detail="Provide primary key.")
        id = kwargs['pk']
        requesting_user = SBUser.objects.filter(
            user_id=self.request.user.id).first()
        if requesting_user is None:
            raise NotAcceptable(detail="Please provide right SBUser id.")
        if id != requesting_user.id:
            raise NotAuthenticated(
                detail="You are not authorized for this action.")
        kwargs['partial'] = True
        if request.data.get('user') is not None:
            user = request.data['user']
            if user.get('email') is not None:
                request.data['user']['username'] = request.data['user']['email']
        if self.request.get('your_city') is not None:
            self.request['your_city'] = str(
                request.data['your_city']).capitalize()
        return super().update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if kwargs.get('pk') is None:
            raise NotAcceptable(detail="Provide primary key.")
        id = kwargs['pk']
        try:
            requesting_user = SBUser.objects.get(user_id=self.request.user.id)
        except ObjectDoesNotExist:
            raise NotAcceptable(detail="Provide right primary key.")
        if id != requesting_user.id:
            raise NotAuthenticated(
                detail="You are not authorized for this action.")
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if kwargs.get('pk') is None:
            raise NotAcceptable(detail="Provide primary key.")
        id = kwargs['pk']
        try:
            requesting_user = SBUser.objects.get(user_id=self.request.user.id)
        except ObjectDoesNotExist:
            raise NotAcceptable(detail="Provide right primary key.")
        if id != requesting_user.id:
            raise NotAuthenticated(
                detail="You are not authorized for this action.")
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        return SBUser.objects.filter(user_id=self.request.user.id)
    serializer_class = UpdateProfileSerialier
    permission_classes = [IsAuthenticated]


class PostLikeView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        '''
        It likes the post of given pk if it is not liked earlier, else it will unlike it.
        '''
        post = Post.objects.filter(id=kwargs['pk']).first()
        if post is None:
            raise NotAcceptable(detail="Provide right post id.")
        if post.likes.filter(id=self.request.user.id).exists():
            post.likes.remove(self.request.user.id)
            post.number_of_likes -= 1
            post.score = post.number_of_likes*0.20 + \
                post.effective_number_of_comments*0.35 + post.number_of_shares*0.45
            post.save()
            return Response("Post has been unliked", status=status.HTTP_200_OK)
        else:
            data = {"liker": self.request.user.id, "post": post.id}
            serializer = PostLikeSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            post.number_of_likes += 1
            post.score = post.number_of_likes*0.20 + \
                post.effective_number_of_comments*0.35 + post.number_of_shares*0.45
            post.save()
            return Response("Post has been liked.", status=status.HTTP_200_OK)


class CommentView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        '''
        Using this API, one can comment on a post as well as on a comment also. 
        And those posts which are set to commentable by friends only or none have been managed also.
        '''
        if len(request.data) == 0:
            raise NotAcceptable(detail="No data provided.")
        if request.data.get('post') is None:
            raise NotAcceptable(detail="No data provided.")
        request.data['user'] = self.request.user.id
        if request.data.get('comment') is None:
            raise NotAcceptable(detail="Comment is blank.")
        post_id = request.data.get('post')
        try:
            post = Post.objects.get(id=post_id)
        except ObjectDoesNotExist:
            raise NotAcceptable(detail="Provide right primary key.")
        if post.who_can_comment == 'None':
            raise NotAcceptable(
                detail="User has blocked his comments on this post.")
        if post.who_can_comment == 'Friends':
            sbuser = SBUser.objects.get(user_id=post.user_id)
            if (sbuser.friends.filter(user_id=self.request.user.id).exists() == False) and (self.request.user != sbuser.user):
                raise NotAcceptable(
                    detail="You are not friend of the user and only his/her friends can comment on this post.")
        return super().create(request, *args, **kwargs)
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]


class CommentLikeView(generics.UpdateAPIView):
    '''
    This API works same as post like api. It likes any comment.
    '''
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        try:
            comment = Comment.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            raise NotAcceptable(detail="Provide right primary key.")
        if comment.likes.filter(id=self.request.user.id).exists():
            comment.likes.remove(self.request.user.id)
            comment.number_of_likes -= 1
            comment.save()
            return Response("comment has been unliked", status=status.HTTP_200_OK)
        else:
            comment.likes.add(self.request.user.id)
            comment.number_of_likes += 1
            comment.save()
            return Response("comment has been liked.", status=status.HTTP_200_OK)


class CommentListView(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        '''
        Lists comments of the post whose pk is provided.
        '''
        if kwargs.get('pk') is None:
            raise NotAcceptable(detail="Please provide post id.")
        post_id = kwargs['pk']
        post = Post.objects.get(id=post_id)
        post_user = post.user_id
        requesting_user = self.request.user
        sbuser = SBUser.objects.get(user_id=post_user)
        if post_user != requesting_user.id:
            if post.who_can_see == 'None':
                raise NotAcceptable(
                    detail="You are not authorized for this action.")
            if post.who_can_see == 'Friends':
                if sbuser.friends.filter(user_id=requesting_user.id).exists() == False:
                    raise NotAcceptable(
                        detail="You are not a friend of the user and he/she has kept this post for friends only.")
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        post_id = self.kwargs['pk']
        return Comment.objects.filter(post_id=post_id)

    def get_serializer_class(self):
        post = Post.objects.get(id=self.kwargs['pk'])
        if self.request.user.id == post.user_id:
            return CommentLRDSerializerForPoster
        else:
            return CommentLRSerializerForUser
    serializer_class = get_serializer_class
    permission_classes = [IsAuthenticated]


class CommentRDView(generics.RetrieveUpdateDestroyAPIView):
    def retrieve(self, request, *args, **kwargs):
        '''
        retrieves comment with the management of who_can_see section of post.
        '''
        comment_id = kwargs['pk']
        try:
            comment = Comment.objects.get(id=comment_id)
        except ObjectDoesNotExist:
            raise NotAcceptable(detail="Provide right primary key.")
        post = comment.post
        post_user = post.user_id
        requesting_user = self.request.user
        sbuser = SBUser.objects.get(user_id=post_user)
        if post_user != requesting_user.id:
            if post.who_can_see == 'None':
                raise NotAcceptable(
                    detail="You are not authorized for this action.")
            if post.who_can_see == 'Friends':
                if sbuser.friends.filter(user_id=requesting_user.id).exists() == False:
                    raise NotAcceptable(
                        detail="You are not a friend of the user and he/she has kept this post for friends only.")
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if kwargs.get('pk') is None:
            raise NotAcceptable(detail="Provide primary key.")
        kwargs['partial'] = True
        comment_id = kwargs['pk']
        try:
            comment = Comment.objects.get(id=comment_id)
        except ObjectDoesNotExist:
            raise NotAcceptable(detail="Provide right primary key.")
        if self.request.user.id != comment.user_id:
            raise NotAcceptable(
                detail="You are not authorized for this action.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if kwargs.get('pk') is None:
            raise NotAcceptable(detail="Provide primary key.")
        comment_id = kwargs['pk']
        try:
            comment = Comment.objects.get(id=comment_id)
        except ObjectDoesNotExist:
            raise NotAcceptable(detail="Provide right primary key.")
        posting_user = comment.post.user_id
        if (self.request.user.id != comment.user_id) and (self.request.user.id != posting_user):
            raise NotAcceptable(
                detail="You are not authorized for this action.")
        post = comment.post
        post.number_of_comments -= 1
        if comment.user_id != post.user_id:
            post.effective_number_of_comments -= 1
        post.score = post.number_of_likes*0.20 + \
            post.effective_number_of_comments*0.35 + post.number_of_shares*0.45
        post.save()
        return super().destroy(request, *args, **kwargs)
    queryset = Comment.objects.all()

    def get_serializer_class(self):
        requesting_user = self.request.user
        commenting_user = Comment.objects.get(id=self.kwargs['pk'])
        posting_user = commenting_user.post.user
        if requesting_user == posting_user:
            if (self.request.method == 'PUT') or (self.request.method == 'PATCH'):
                return CommentUpdateSerializer
            else:
                return CommentLRDSerializerForPoster
        elif requesting_user == commenting_user:
            if (self.request.method == 'PUT') or (self.request.method == 'PATCH'):
                return CommentUpdateSerializer
            else:
                return CommentRDSerializerForCommentor
        else:
            return CommentLRSerializerForUser
    serializer_class = get_serializer_class
    permission_classes = [IsAuthenticated]


class ListFriends(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        '''
        Lists friends of a given user.
        '''
        if kwargs.get('pk') is None:
            raise NotAcceptable(
                detail="Please provide the user id whose friend you seek.")
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.id == self.kwargs['pk']:
            sbuser = SBUser.objects.get(user_id=self.request.user.id)
            return sbuser.friends.all()
        else:
            requested_user = SBUser.objects.get(user_id=self.kwargs['pk'])
            if requested_user.display_friends == 'None':
                raise NotAcceptable(
                    detail="You are trying to access friends list of the user who has blocked this service.")
            if requested_user.display_friends == 'Friends':
                requesting_sb_user = SBUser.objects.get(
                    user_id=self.request.user.id)
                if requested_user.friends.filter(id=requesting_sb_user.id).exists() == False:
                    raise NotAcceptable(
                        detail="You are trying to access a private list.")
                else:
                    return requested_user.friends.all()
            else:
                requested_user = SBUser.objects.get(user_id=self.kwargs['pk'])
                return requested_user.friends.all()
    serializer_class = ListFriendsSerializer
    permission_classes = [IsAuthenticated]


class RetrieveProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        '''
        retrieves profile with the management of display_email, display_mobile and display_personal_info.
        It takes primary key of user. i.e. userid not sbuser id.
        '''
        if kwargs['pk'] is None:
            raise NotAcceptable(detail="Please provide user id.")
        if self.request.user.id == kwargs['pk']:
            try:
                requested_data = SBUser.objects.get(
                    user_id=self.request.user.id)
            except ObjectDoesNotExist:
                raise NotAcceptable(
                    detail="This user is not registered completely.")
            serializer = RetrieveProfileSerializer(requested_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            try:
                requesting_sb_user = SBUser.objects.get(
                    user_id=self.request.user.id)
            except ObjectDoesNotExist:
                raise NotAcceptable(
                    detail="This user is not registered completely.")
            try:
                requested_sb_user = SBUser.objects.get(user_id=kwargs['pk'])
            except ObjectDoesNotExist:
                raise NotAcceptable(detail="Provide right primary key")
            serializer = RetrieveProfileSerializer(requested_sb_user)
            data = json.loads(json.dumps(serializer.data))
            if requested_sb_user.display_email == 'None':
                data['user'].pop('email')
                data['user'].pop('username')
            if requested_sb_user.display_email == 'Friends':
                if requesting_sb_user not in requested_sb_user.friends.all():
                    data['user'].pop('email')
                    data['user'].pop('username')
                else:
                    pass
            if requested_sb_user.display_mobile == 'None':
                data.pop('mobile_number')
            if requested_sb_user.display_mobile == 'Friends':
                if requesting_sb_user not in requested_sb_user.friends.all():
                    data.pop('mobile_number')
                else:
                    pass
            if requested_sb_user.display_personal_info == 'None':
                if data.get('mobile_number') is not None:
                    data.pop('mobile_number')
                if data['user'].get('username') is not None:
                    data['user'].pop('username')
                if data['user'].get('email') is not None:
                    data['user'].pop('email')
                data.pop('date_of_birth')
                data.pop('your_school')
                data.pop('your_college')
                data.pop('your_occupation')
                data.pop('favourite_movies')
                data.pop('favourite_books')
                data.pop('your_city')
                data.pop('tell_your_friends_about_you')
            if requested_sb_user.display_personal_info == 'Friends':
                if requesting_sb_user not in requested_sb_user.friends.all():
                    if data.get('mobile_number') is not None:
                        data.pop('mobile_number')
                    if data['user'].get('username') is not None:
                        data['user'].pop('username')
                    if data['user'].get('email') is not None:
                        data['user'].pop('email')
                    data.pop('date_of_birth')
                    data.pop('your_school')
                    data.pop('your_college')
                    data.pop('your_occupation')
                    data.pop('favourite_movies')
                    data.pop('favourite_books')
                    data.pop('your_city')
                    data.pop('tell_your_friends_about_you')
                else:
                    pass
        return Response(data, status=status.HTTP_200_OK)


class FriendRequestView(generics.ListCreateAPIView):
    def create(self, request, *args, **kwargs):
        '''
        Sends friend request to the user.
        '''
        if kwargs.get('pk') is None:
            raise NotAcceptable(detail="Please provide user id.")
        request.data['user'] = kwargs['pk']
        request.data['sender'] = self.request.user.id
        user = SBUser.objects.get(user_id=request.data['user'])
        sender = SBUser.objects.get(user_id=request.data['sender'])
        if user in sender.friends.all():
            raise NotAcceptable(detail="You are already friends.")
        if user == sender:
            raise NotAcceptable(detail="You can send request to yourself.")
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        return FriendRequest.objects.filter(user_id=self.request.user.id)
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]


class AcceptCancelRequestView(generics.RetrieveUpdateAPIView):
    '''
    For accept, bool = True
    For cancel, bool = False
    '''
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        '''
        accepts or denies the request with bool = True or False.
        '''
        if kwargs['pk'] is None:
            raise NotAcceptable(detail="Provide Request id.")
        if request.data.get('bool') is None:
            raise NotAcceptable(
                detail="Please provie bool, True for accept and False for cancel.")
        friend_request = FriendRequest.objects.filter(id=kwargs['pk']).first()
        if friend_request is None:
            raise NotAcceptable(detail="Please provide right request id.")
        requesting_user = SBUser.objects.get(user_id=self.request.user.id)
        sender = SBUser.objects.get(user_id=friend_request.sender_id)
        acceptor = SBUser.objects.get(user_id=friend_request.user_id)
        if request.data['bool'] == False:
            if (requesting_user != sender) and (requesting_user != acceptor):
                raise NotAcceptable(
                    detail="You are not authorized for this action.")
            else:
                friend_request.delete()
                return Response("Request has been cancelled.", status=status.HTTP_200_OK)
        if request.data['bool'] == True:
            if requesting_user != acceptor:
                raise NotAcceptable(
                    detail="You are not authorized for this action.")
            else:
                acceptor.friends.add(sender)
                friend_request.delete()
                return Response(f'You and {sender} are friends now.', status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        if kwargs['pk'] is None:
            raise NotAcceptable(detail="Provide request id.")
        try:
            friend_request = FriendRequest.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            raise NotAcceptable(detail="Provide right primary key")
        requesting_user = SBUser.objects.get(user_id=self.request.user.id)
        sender = SBUser.objects.get(user_id=friend_request.sender_id)
        acceptor = SBUser.objects.get(user_id=friend_request.user_id)
        if (requesting_user != sender) and (requesting_user != acceptor):
            raise NotAcceptable(
                detail="You are not authorized for this action.")
        else:
            serializer = FriendRequestSerializer(friend_request)
            return Response(serializer.data, status=status.HTTP_200_OK)


class UnfriendView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        '''
        This unfriends a friend whose pk (sbuserid) is passed by kwargs.
        '''
        if kwargs.get('pk') is None:
            raise NotAcceptable(
                detail="Please provide sine book user id of the friend.")
        requesting_user_id = self.request.user.id
        try:
            unfriending_sb_user = SBUser.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            raise NotAcceptable(detail="Provide right primary key")
        if unfriending_sb_user.friends.filter(user_id=requesting_user_id).exists() == False:
            raise NotAcceptable(detail="You are already not friends.")
        requesting_sb_user = SBUser.objects.get(user_id=requesting_user_id)
        requesting_sb_user.friends.remove(unfriending_sb_user)
        return Response(f"You have unfriended {unfriending_sb_user}.", status=status.HTTP_200_OK)


class PageCreateView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        if len(request.data) == 0:
            raise NotAcceptable(detail="Please provide data.")
        if request.data.get('title') is None:
            raise NotAcceptable(detail="Please provide page title.")
        request.data['creator'] = self.request.user.id
        if request.data.get('tags') is not None:
            if '#' in str(request.data['tags']):
                raise NotAcceptable(
                    "Do not use # in the tags, write them only seperated by , and whitespace. as 'love, affection, romance'")
            tags_list = str(request.data['tags']).split(', ')
            if len(tags_list) > 10:
                raise NotAcceptable("Do not use tags more than 10.")
            tag_id_list = []
            for tag in tags_list:
                tag = tag.strip()
                tag = tag.casefold()
                tag_instance_tuple = Tags.objects.get_or_create(
                    tag_name=tag)
                tag_instance = tag_instance_tuple[0]
                tag_id_list.append(tag_instance.id)
            request.data['tags'] = tag_id_list
        return super().create(request, *args, **kwargs)
    serializer_class = PageCreateSerializer
    permission_classes = [IsAuthenticated]


class PageRUDView(generics.RetrieveUpdateDestroyAPIView):
    def retrieve(self, request, *args, **kwargs):
        if kwargs.get('pk') is None:
            raise NotAcceptable(detail="Please Provide page id.")
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if kwargs.get('pk') is None:
            raise NotAcceptable(detail="Please Provide page id.")
        try:
            page = Page.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            raise NotAcceptable("Please provide correct page id.")
        if (self.request.user.id != page.creator_id) and (page.members.filter(id=self.request.user.id).exists() == False):
            raise NotAuthenticated("you are not authorized for this action.")
        kwargs['partial'] = True
        if request.data.get('tags') is not None:
            if '#' in str(request.data['tags']):
                raise NotAcceptable(
                    "Do not use # in the tags, write them only seperated by , and whitespace. as 'love, affection, romance'")
            tags_list = str(request.data['tags']).split(', ')
            if len(tags_list) > 10:
                raise NotAcceptable("Do not use tags more than 10.")
            tag_id_list = []
            for tag in tags_list:
                tag = tag.strip()
                tag = tag.casefold()
                tag_instance_tuple = Tags.objects.get_or_create(
                    tag_name=tag)
                tag_instance = tag_instance_tuple[0]
                tag_id_list.append(tag_instance.id)
            request.data['tags'] = tag_id_list
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if kwargs.get('pk') is None:
            raise NotAcceptable(detail="Please Provide page id.")
        try:
            page = Page.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            raise NotAcceptable("Please provide correct page id.")
        if self.request.user.id != page.creator_id:
            raise NotAuthenticated("you are not authorized for this action.")
        return super().destroy(request, *args, **kwargs)
    queryset = Page.objects.all()

    def get_serializer_class(self):
        try:
            page = Page.objects.get(id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            raise NotAcceptable("Provide right page id.")
        page_creator_id = page.creator_id
        requesting_user_id = self.request.user.id
        method = self.request.method
        if page_creator_id == requesting_user_id:
            if (method == 'PUT') or (method == 'DELETE'):
                return PageUpdateDestroyByCreatorSerializer
        if (page_creator_id != requesting_user_id) and (page.members.filter(id=requesting_user_id).exists()):
            if method == 'PUT':
                return PageUpdateByMemberSerializer
        if (page_creator_id == requesting_user_id) or (page.members.filter(id=requesting_user_id).exists()):
            if method == 'GET':
                return PageRetrieveSerializerByMember
        if (page_creator_id != requesting_user_id) and (page.members.filter(id=requesting_user_id).exists() == False):
            if method == 'GET':
                return RetrievePageByUserSerializer
        else:
            raise NotAcceptable("You are not authorized for this action.")
    serializer_class = get_serializer_class
    permission_classes = [IsAuthenticated]


class AddMemberView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if len(request.data) == 0:
            raise NotAcceptable(detail="provide data")
        if request.data.get('page') is None:
            raise NotAcceptable(detail="Provide page id.")
        if request.data.get('member') is None:
            raise NotAcceptable(detail="Please Provide user id of member.")
        try:
            page = Page.objects.get(id=request.data['page'])
        except ObjectDoesNotExist:
            raise NotAcceptable(detail="Provide right page id.")
        try:
            member = User.objects.get(id=request.data['member'])
        except ObjectDoesNotExist:
            raise NotAcceptable(detail="Provide right user id of member.")
        if page.creator_id != self.request.user.id:
            raise NotAuthenticated("You are not authorized for this action.")
        if page.members.filter(id=member.id).exists():
            raise NotAcceptable(detail=f"{member} is already a member.")
        page.members.add(member)
        return Response(f"{member} is now member of the page {page}")


class RemoveMemberView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if len(request.data) == 0:
            raise NotAcceptable(detail="provide data")
        if request.data.get('page') is None:
            raise NotAcceptable(detail="Provide page id.")
        if request.data.get('member') is None:
            raise NotAcceptable(detail="Please Provide user id of member.")
        try:
            page = Page.objects.get(id=request.data['page'])
        except ObjectDoesNotExist:
            raise NotAcceptable(detail="Provide right page id.")
        try:
            member = User.objects.get(id=request.data['member'])
        except ObjectDoesNotExist:
            raise NotAcceptable(detail="Provide right user id of member.")
        if page.creator_id != self.request.user.id:
            raise NotAuthenticated("You are not authorized for this action.")
        if page.members.filter(id=member.id).exists() == False:
            raise NotAcceptable(detail=f"{member} is already not a member.")
        page.members.remove(member)
        return Response(f"{member} is no more a member of the page {page}")


class FollowUnfollowPage(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        if kwargs.get('pk') is None:
            raise NotAcceptable(detail="Please provide page id.")
        kwargs['partial'] = True
        try:
            page = Page.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            raise NotAcceptable("Use right user id.")
        follower = self.request.user
        if page.followers.filter(id=follower.id).exists() == False:
            page.followers.add(follower)
            user_interests = UserInterest.objects.get_or_create(
                user_id=follower.id)
            instance = user_interests[0]
            instance.followed_pages.add(page)
            page.number_of_followers += 1
            page.save()
            return Response(f'{page} followed.', status=status.HTTP_200_OK)
        else:
            page.followers.remove(follower)
            user_interests = UserInterest.objects.get_or_create(
                user_id=follower.id)
            instance = user_interests[0]
            instance.followed_pages.remove(page)
            page.number_of_followers -= 1
            page.save()
            return Response(f'{page} unfollowed', status=status.HTTP_200_OK)


class CreatedPagesOfProfile(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        if kwargs.get('pk') is None:
            raise NotAcceptable(detail="Provide user id of the creator.")
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return Page.objects.filter(creator_id=self.kwargs['pk'])
    serializer_class = RetrievePageByUserSerializer
    permission_classes = [IsAuthenticated]


class MyFollowedPages(generics.ListAPIView):
    def get_queryset(self):
        interest = UserInterest.objects.get_or_create(
            user_id=self.request.user.id)
        instance = interest[0]
        return instance.followed_pages.all()
    serializer_class = RetrievePageByUserSerializer
    permission_classes = [IsAuthenticated]


class PostListCreateView(generics.ListCreateAPIView):
    '''
    For post share, send additional data:
        "shared_post": "pk"
        It will share the post with another post. 
        In such case, frontend will call retrieve request for post of pk to get the info of sharing post and integrate that too.
    '''

    def create(self, request, *args, **kwargs):
        if len(request.data) == 0:
            raise NotAcceptable("Please provide data.")
        if (request.data.get('image') is None) and (request.data.get('description') is None):
            raise NotAcceptable("Please provide post data.")
        if request.data.get('shared_post') is not None:
            if request.data.get('image') is not None:
                raise NotAcceptable(
                    "You can not add a image while sharing a post.")
        request.data['user'] = self.request.user.id
        if request.data.get('page') is not None:
            try:
                page = Page.objects.get(id=request.data['page'])
            except ObjectDoesNotExist:
                raise NotAcceptable("Please provide right page id.")
            if (page.creator_id != self.request.user.id) and (page.members.filter(id=self.request.user.id)):
                raise NotAuthenticated(
                    'You are not a member or creator of this page.')
        description = request.data.get('description')
        if description is not None:
            description = str(description)
            if str(description).count('#') > 10:
                raise NotAcceptable(
                    "You can not use more than 10 hash tags in your post.")
            words_list = description.split(' ')
            tags_id_list = []
            for item in words_list:
                if item.__contains__('#'):
                    words = item.split('#')
                    for word in words:
                        word = word.replace('.', '')
                        word = word.casefold()
                        word = word.strip()
                        if word != '':
                            tag_tuple = Tags.objects.get_or_create(
                                tag_name=word)
                            tag = tag_tuple[0]
                            tags_id_list.append(tag.id)
            if len(tags_id_list) > 0:
                request.data['tags'] = tags_id_list
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        '''
        For posts which share other post, will contain shared_post an integer which is id of the post.
        Front end must take care of those too so that user can see the shared and sharing post at the same page.
        '''
        if (request.data.get('user') is None) and (request.data.get('page') is None):
            raise NotAcceptable(
                detail="Please provide id of user or page whose posts you seek.")
        if (request.data.get('user') is not None) and (request.data.get('page') is not None):
            raise NotAcceptable(
                detail="Please provide only one id, either of page or of user.")
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.data.get('page') is not None:
            return Post.objects.filter(page_id=self.request.data['page'])
        else:
            try:
                requesting_sb_user = SBUser.objects.get(
                    user_id=self.request.user.id)
                requested_sb_user = SBUser.objects.get(
                    user_id=self.request.data['user'])
            except ObjectDoesNotExist:
                raise NotAcceptable("provide right user id.")
            if requested_sb_user.id == requesting_sb_user.id:
                return Post.objects.filter(user_id=self.request.data['user']).filter(page=None)
            if requesting_sb_user.friends.filter(id=requested_sb_user.id).exists():
                return Post.objects.filter(user_id=self.request.data['user']).filter(page=None).exclude(who_can_see='None')
            else:
                return Post.objects.filter(user_id=self.request.data['user']).filter(page=None).filter(who_can_see='Public')

    def get_serializer_class(self):
        if self.request.data.get('page') is None:
            if self.request.method == 'GET':
                return PostByUserListSerializer
            if self.request.method == 'POST':
                return PostByUserCreateSerializer
        else:
            if self.request.method == 'GET':
                return PostByPageListSerializer
            if self.request.method == 'POST':
                return PostByPageCreateSerializer
    serializer_class = get_serializer_class
    permission_classes = [IsAuthenticated]


class PostRUDView(generics.RetrieveUpdateDestroyAPIView):
    def retrieve(self, request, *args, **kwargs):
        '''
        For posts which share other post, will contain shared_post an integer which is id of the post.
        Front end must take care of those too so that user can see the shared and sharing post at the same page.
        '''
        if kwargs.get('pk') is None:
            raise NotAcceptable(detail="Please provide pk of post.")
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if kwargs.get('pk') is None:
            raise NotAcceptable("Please provide pk of the post.")
        requesting_user = self.request.user
        if request.data.get('tags') is not None:
            request.data.pop('tags')
        try:
            post = Post.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            raise NotAcceptable("provide right post id.")
        if post.page is None:
            if requesting_user.id != post.user.id:
                raise NotAuthenticated(
                    'You are not authorized for this action.')
        else:
            page = post.page
            if (requesting_user.id != page.creator_id) and (page.members.filter(id=requesting_user.id).exists() == False):
                raise NotAuthenticated(
                    'You are not authorized for this action.')
        description = request.data.get('description')
        if description is not None:
            description = str(description)
            if str(description).count('#') > 10:
                raise NotAcceptable(
                    "You can not use more than 10 hash tags in your post.")
            words_list = description.split(' ')
            tags_id_list = []
            for item in words_list:
                if item.__contains__('#'):
                    words = item.split('#')
                    for word in words:
                        word = word.replace('.', '')
                        word = word.casefold()
                        word = word.strip()
                        if word != '':
                            tag_tuple = Tags.objects.get_or_create(
                                tag_name=word)
                            tag = tag_tuple[0]
                            tags_id_list.append(tag.id)
            if len(tags_id_list) > 0:
                request.data['tags'] = tags_id_list
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if kwargs.get('pk') is None:
            raise NotAcceptable("Please provide pk of the post.")
        requesting_user = self.request.user
        try:
            post = Post.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            raise NotAcceptable("provide right post id.")
        if post.page is None:
            if requesting_user.id != post.user.id:
                raise NotAuthenticated(
                    'You are not authorized for this action.')
        else:
            page = post.page
            if requesting_user.id != page.creator_id:
                raise NotAuthenticated(
                    'You are not authorized for this action.')
        shared_post = post.shared_post
        if shared_post is not None:
            shared_post.number_of_shares -= 1
            shared_post.save()
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        try:
            post = Post.objects.get(id=self.kwargs['pk'])
            requesting_userid = self.request.user.id
            posterid = post.user_id
            requesting_sb_user = SBUser.objects.get(user_id=requesting_userid)
        except ObjectDoesNotExist:
            raise NotAcceptable("Provide right post id.")
        if post.page is not None:
            return Post.objects.filter(id=self.kwargs['pk'])
        else:
            if post.who_can_see == 'Public':
                return Post.objects.filter(id=self.kwargs['pk'])
            if post.who_can_see == 'Friends':
                if (requesting_userid != posterid) and (requesting_sb_user.friends.filter(user_id=posterid).exists() == False):
                    raise NotAuthenticated(
                        'You are not authorized for this action as you should be the friend of the poster.')
                else:
                    return Post.objects.filter(id=self.kwargs['pk'])
            else:
                if requesting_userid != posterid:
                    raise NotAuthenticated(
                        "This is a private post, you can not open it.")
                else:
                    return Post.objects.filter(id=self.kwargs['pk'])

    def get_serializer_class(self):
        try:
            post = Post.objects.get(id=self.kwargs['pk'])
            requesting_userid = self.request.user.id
        except ObjectDoesNotExist:
            raise NotAcceptable("Provide right post id.")
        method = self.request.method
        if post.page is None:
            if post.user_id != requesting_userid:
                if method == 'GET':
                    return PostByUserRetrieveByOtherSerializer
                else:
                    raise NotAuthenticated(
                        "You are not autherized for this action.")
            else:
                if method == 'GET':
                    return PostByUserRetrieveByPosterSerializer
                else:
                    return PostByUserUpdateDestroySerializer
        else:
            if (post.page.creator_id != requesting_userid) and (post.page.members.filter(id=requesting_userid).exists() == False):
                if method == 'GET':
                    return PostByPageRetrieveByOtherSerializer
                else:
                    raise NotAuthenticated(
                        "You are not authorized for this action.")
            else:
                if method == 'GET':
                    return PostByPageRetrieveByMemberSerializer
                else:
                    return PostByPageUpdateDestroySerializer
    serializer_class = get_serializer_class
    permission_classes = [IsAuthenticated]


class PostFeedView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        i = 10
        requesting_userid = self.request.user.id
        requesting_sb_user = SBUser.objects.prefetch_related(
            'friends').get(user_id=requesting_userid)
        user_interest = UserInterest.objects.prefetch_related(
            'suggested_posts', 'followed_pages', 'likes').get(user_id=requesting_userid)
        recently_suggested_posts = user_interest.suggested_posts.all()
        user_posts_to_be_suggested = Post.objects.none()
        friends_list = requesting_sb_user.friends.all()
        '''
        Posts by the friends, posted within 2 days, are being listed and ordered with respect to score
        as well as recently suggested posts are being excluded.
        '''
        if len(friends_list) > 0:
            for friend in friends_list:
                friend_interest = UserInterest.objects.prefetch_related(
                    'posts').get(user_id=friend.user_id)
                friends_recent_posts = friend_interest.posts.filter(
                    posted_at__gte=timezone.now() - timedelta(days=2)).exclude(who_can_see='None')
                user_posts_to_be_suggested = user_posts_to_be_suggested.union(
                    friends_recent_posts)
        user_posts_to_be_suggested = user_posts_to_be_suggested.difference(
            recently_suggested_posts)
        ordered_posts_by_user_to_be_suggested = user_posts_to_be_suggested.order_by(
            '-score')
        number_of_suggested_posts_by_user = len(user_posts_to_be_suggested)
        if number_of_suggested_posts_by_user >= i:
            suggested_posts = ordered_posts_by_user_to_be_suggested[0:i]
            serializer = PostByUserRetrieveByOtherSerializer(
                suggested_posts, many=True)
            data = serializer.data
            '''
            Add the suggested posts to recently suggested posts of the user.
            '''
            for post in suggested_posts:
                user_interest.suggested_posts.add(post)
            return Response(data, status=status.HTTP_200_OK)
            #level 1 of posts by user for suggestions is completed.
        else:
            '''
            Posts By the pages followed by the user, posted within last 2 days are being listed for suggestions.
            '''
            required_number_of_posts = i - number_of_suggested_posts_by_user
            page_posts_to_be_suggested = Post.objects.none()
            if len(user_interest.followed_pages.all()) > 0:
                for page in user_interest.followed_pages.all():
                    post_page_instance = PagePostList.objects.prefetch_related(
                        'posts').get(page_id=page.id)
                    page_recent_posts = post_page_instance.posts.filter(
                        posted_at__gte=timezone.now() - timedelta(days=2))
                    page_posts_to_be_suggested = page_posts_to_be_suggested.union(
                        page_recent_posts)
            page_posts_to_be_suggested = page_posts_to_be_suggested.difference(
                recently_suggested_posts)
            ordered_posts_by_page_to_be_suggested = page_posts_to_be_suggested.order_by(
                '-score')
            number_of_page_posts_to_be_suggested = len(
                page_posts_to_be_suggested)
            if number_of_page_posts_to_be_suggested >= required_number_of_posts:
                required_page_posts = ordered_posts_by_page_to_be_suggested[
                    0:required_number_of_posts]
                user_serializer = PostByUserRetrieveByOtherSerializer(
                    user_posts_to_be_suggested, many=True)
                page_serializer = PostByPageRetrieveByOtherSerializer(
                    required_page_posts, many=True)
                data = user_serializer.data+page_serializer.data
                suggested_posts = user_posts_to_be_suggested.union(
                    required_page_posts)
                for post in suggested_posts:
                    user_interest.suggested_posts.add(post)
                return Response(data, status=status.HTTP_200_OK)
                # level 1 of posts by page, for suggestions, is completed.
            else:
                '''
                Posts by the pages, whose posted has been liked with in 2 days, posted within 2 days are listed.
                '''
                required_number_of_posts = i - \
                    (number_of_suggested_posts_by_user +
                     number_of_page_posts_to_be_suggested)
                page_post_likes = user_interest.likes.exclude(
                    post__page__isnull=True).order_by('-liked_at')
                unknown_page_posts_to_be_suggested = Post.objects.none()
                if len(page_post_likes) > 0:
                    for like in page_post_likes:
                        posting_page_id = like.post.page_id
                        if user_interest.followed_pages.filter(id=posting_page_id).exists() == False:
                            post_page_list_instance = PagePostList.objects.prefetch_related(
                                'posts').get(page_id=posting_page_id)
                            posts_list_by_page = post_page_list_instance.posts.filter(
                                posted_at__gte=timezone.now() - timedelta(days=2))
                            unknown_page_posts_to_be_suggested = unknown_page_posts_to_be_suggested.union(
                                posts_list_by_page)
                unknown_page_posts_to_be_suggested = unknown_page_posts_to_be_suggested.difference(
                    recently_suggested_posts, page_posts_to_be_suggested)
                ordered_unkown_page_posts_to_be_suggested = unknown_page_posts_to_be_suggested.order_by(
                    '-score')
                if len(unknown_page_posts_to_be_suggested) >= required_number_of_posts:
                    required_page_posts = ordered_unkown_page_posts_to_be_suggested[
                        0:required_number_of_posts]
                    user_serializer = PostByUserRetrieveByOtherSerializer(
                        user_posts_to_be_suggested, many=True)
                    page_serializer_level_1 = PostByPageRetrieveByOtherSerializer(
                        page_posts_to_be_suggested, many=True)
                    page_serializer_level_2 = PostByPageRetrieveByOtherSerializer(
                        required_page_posts, many=True)
                    data = user_serializer.data+page_serializer_level_1.data+page_serializer_level_2.data
                    suggested_posts = user_posts_to_be_suggested.union(
                        page_posts_to_be_suggested, required_page_posts)
                    for post in suggested_posts:
                        user_interest.suggested_posts.add(post)
                    return Response(data, status=status.HTTP_200_OK)
                    # level 2 of posts by page, to be suggested, has completed.
                else:
                    '''
                    Posts by user, whose recent posts has been liked by the requesting user within 2 days, posted within last 2 days, are listed.
                    '''
                    required_number_of_posts = i - \
                        (number_of_suggested_posts_by_user +
                         number_of_page_posts_to_be_suggested)
                    user_post_likes = user_interest.likes.filter(
                        post__page__isnull=True).order_by('-liked_at')
                    unknown_user_posts_to_be_suggested = Post.objects.none()
                    if len(user_post_likes) > 0:
                        for like in user_post_likes:
                            posting_user_id = like.post.user_id
                            if requesting_sb_user.friends.filter(user_id=posting_user_id).exists() == False:
                                liked_user_interest_instance = UserInterest.objects.prefetch_related(
                                    'posts').get(user_id=posting_user_id)
                                posts_list_by_user = liked_user_interest_instance.posts.filter(
                                    posted_at__gte=timezone.now() - timedelta(days=2)).filter(who_can_see='Public')
                                unknown_user_posts_to_be_suggested = unknown_user_posts_to_be_suggested.union(
                                    posts_list_by_user)
                    unknown_user_posts_to_be_suggested = unknown_user_posts_to_be_suggested.difference(
                        recently_suggested_posts, user_posts_to_be_suggested)
                    ordered_unkown_user_posts_to_be_suggested = unknown_user_posts_to_be_suggested.order_by(
                        '-score')
                    if len(unknown_user_posts_to_be_suggested) >= required_number_of_posts:
                        required_user_posts = ordered_unkown_user_posts_to_be_suggested[
                            0:required_number_of_posts]
                        user_serializer_level_1 = PostByUserRetrieveByOtherSerializer(
                            user_posts_to_be_suggested, many=True)
                        user_serializer_level_2 = PostByUserRetrieveByOtherSerializer(
                            required_user_posts, many=True)
                        page_serializer_level_1 = PostByPageRetrieveByOtherSerializer(
                            page_posts_to_be_suggested, many=True)
                        page_serializer_level_2 = PostByPageRetrieveByOtherSerializer(
                            unknown_page_posts_to_be_suggested, many=True)
                        data = user_serializer_level_1.data+user_serializer_level_2.data + \
                            page_serializer_level_1.data+page_serializer_level_2.data
                        suggested_posts = user_posts_to_be_suggested.union(required_user_posts, unknown_page_posts_to_be_suggested,
                                                                           page_posts_to_be_suggested)
                        for post in suggested_posts:
                            user_interest.suggested_posts.add(post)
                        return Response(data, status=status.HTTP_200_OK)
                        # level 2 of posts by user, to be suggested, has completed.

                    else:
                        '''
                        Posts by those pages which have same hashtags as in recently liked posts by the user have, are being listed.
                        '''
                        required_number_of_posts = required_number_of_posts - \
                            len(unknown_user_posts_to_be_suggested)
                        tags_of_reacted_page_posts = Tags.objects.none()
                        tagged_page_posts_to_be_suggested = Post.objects.none()
                        most_liked_tags_id_list = []
                        if len(page_post_likes) > 0:
                            if len(page_post_likes) > 10:
                                page_post_likes = page_post_likes[0:10]
                            for like in page_post_likes:
                                if len(like.post.tags.all()) > 0:
                                    tags_list_of_liked_post = like.post.tags.all()
                                    tags_of_reacted_page_posts = tags_of_reacted_page_posts.union(
                                        tags_list_of_liked_post, all=True)
                            if len(tags_of_reacted_page_posts) > 0:
                                tags_id_of_reacted_page_posts = list(
                                    tags_of_reacted_page_posts.values_list('pk', flat=True))
                                most_liked_tag_id = max(
                                    set(tags_id_of_reacted_page_posts), key=tags_id_of_reacted_page_posts.count)
                                most_liked_tags_id_list.append(
                                    most_liked_tag_id)
                                while most_liked_tag_id in tags_id_of_reacted_page_posts:
                                    tags_id_of_reacted_page_posts.remove(
                                        most_liked_tag_id)
                                if len(tags_id_of_reacted_page_posts) > 0:
                                    second_most_liked_tag_id = max(
                                        set(tags_id_of_reacted_page_posts), key=tags_id_of_reacted_page_posts.count)
                                    most_liked_tags_id_list.append(
                                        second_most_liked_tag_id)
                                    while second_most_liked_tag_id in tags_id_of_reacted_page_posts:
                                        tags_id_of_reacted_page_posts.remove(
                                            second_most_liked_tag_id)
                                    if len(tags_id_of_reacted_page_posts) > 0:
                                        third_most_liked_tag_id = max(
                                            set(tags_id_of_reacted_page_posts), key=tags_id_of_reacted_page_posts.count)
                                        most_liked_tags_id_list.append(
                                            third_most_liked_tag_id)
                                for tag_id in most_liked_tags_id_list:
                                    hash_tag_instance = HashTag.objects.prefetch_related(
                                        'posts').get(tag_id=tag_id)
                                    tagged_page_posts_of_instance = hash_tag_instance.posts.filter(
                                        posted_at__gte=timezone.now() - timedelta(days=2)).exclude(page__isnull=True)
                                    tagged_page_posts_to_be_suggested = tagged_page_posts_to_be_suggested.union(
                                        tagged_page_posts_of_instance)
                        tagged_page_posts_to_be_suggested = tagged_page_posts_to_be_suggested.difference(
                            recently_suggested_posts, unknown_page_posts_to_be_suggested, page_posts_to_be_suggested)
                        if len(tagged_page_posts_to_be_suggested) >= required_number_of_posts:
                            tagged_page_posts_to_be_suggested = tagged_page_posts_to_be_suggested.order_by(
                                '-score')[0:required_number_of_posts]
                            user_serializer_level_1 = PostByUserRetrieveByOtherSerializer(
                                user_posts_to_be_suggested, many=True)
                            user_serializer_level_2 = PostByUserRetrieveByOtherSerializer(
                                unknown_user_posts_to_be_suggested, many=True)
                            page_serializer_level_1 = PostByPageRetrieveByOtherSerializer(
                                page_posts_to_be_suggested, many=True)
                            page_serializer_level_2 = PostByPageRetrieveByOtherSerializer(
                                unknown_page_posts_to_be_suggested, many=True)
                            page_serializer_level_3 = PostByPageRetrieveByOtherSerializer(
                                tagged_page_posts_to_be_suggested, many=True)
                            data = user_serializer_level_1.data+user_serializer_level_2.data+page_serializer_level_1.data + \
                                page_serializer_level_2.data+page_serializer_level_3.data
                            suggested_posts = user_posts_to_be_suggested.union(unknown_user_posts_to_be_suggested, unknown_page_posts_to_be_suggested,
                                                                               page_posts_to_be_suggested, tagged_page_posts_to_be_suggested)
                            for post in suggested_posts:
                                user_interest.suggested_posts.add(post)
                            return Response(data, status=status.HTTP_200_OK)
                            # level 3 of page posts suggestions completed.
                        else:
                            '''
                            Posts by users, which has same hashtags as the user recently liked, posted within 2 days are listed.
                            '''
                            required_number_of_posts = required_number_of_posts - \
                                len(tagged_page_posts_to_be_suggested)
                            tagged_user_posts_to_be_suggested = Post.objects.none()
                            if len(most_liked_tags_id_list) > 0:
                                for tag_id in most_liked_tags_id_list:
                                    hash_tag_instance = HashTag.objects.prefetch_related(
                                        'posts').get(tag_id=tag_id)
                                    tagged_user_posts_of_instance = hash_tag_instance.posts.filter(posted_at__gte=timezone.now(
                                    ) - timedelta(days=2)).filter(page__isnull=True).filter(who_can_see='Public')
                                    tagged_user_posts_to_be_suggested = tagged_user_posts_to_be_suggested.union(
                                        tagged_user_posts_of_instance)
                            tagged_user_posts_to_be_suggested = tagged_user_posts_to_be_suggested.difference(
                                recently_suggested_posts, unknown_user_posts_to_be_suggested, user_posts_to_be_suggested)
                            if len(tagged_user_posts_to_be_suggested) >= required_number_of_posts:
                                tagged_user_posts_to_be_suggested = tagged_user_posts_to_be_suggested.order_by(
                                    '-score')[0:required_number_of_posts]
                                user_serializer_level_1 = PostByUserRetrieveByOtherSerializer(
                                    user_posts_to_be_suggested, many=True)
                                user_serializer_level_2 = PostByUserRetrieveByOtherSerializer(
                                    unknown_user_posts_to_be_suggested, many=True)
                                user_serializer_level_3 = PostByUserRetrieveByOtherSerializer(
                                    tagged_user_posts_to_be_suggested, many=True)
                                page_serializer_level_1 = PostByPageRetrieveByOtherSerializer(
                                    page_posts_to_be_suggested, many=True)
                                page_serializer_level_2 = PostByPageRetrieveByOtherSerializer(
                                    unknown_page_posts_to_be_suggested, many=True)
                                page_serializer_level_3 = PostByPageRetrieveByOtherSerializer(
                                    tagged_page_posts_to_be_suggested, many=True)
                                data = user_serializer_level_1.data+user_serializer_level_2.data+user_serializer_level_3.data+page_serializer_level_1.data + \
                                    page_serializer_level_2.data+page_serializer_level_3.data
                                suggested_posts = user_posts_to_be_suggested.union(unknown_user_posts_to_be_suggested, unknown_page_posts_to_be_suggested,
                                                                                   page_posts_to_be_suggested, tagged_page_posts_to_be_suggested, tagged_user_posts_to_be_suggested)
                                for post in suggested_posts:
                                    user_interest.suggested_posts.add(post)
                                return Response(data, status=status.HTTP_200_OK)
                                # level 3 of posts by user suggestions is completed.
                            else:
                                '''
                                Posts by those pages which have same fields as user has selected his favourite field are being listed.
                                '''
                                required_number_of_posts = required_number_of_posts - \
                                    len(tagged_user_posts_to_be_suggested)
                                requesting_sb_user_fields = requesting_sb_user.favourite_fields.all()
                                favourite_field_top_pages = Page.objects.none()
                                for field in requesting_sb_user_fields:
                                    field_page_instance = FieldPages.objects.prefetch_related(
                                        'pages').get(field=field)
                                    if field_page_instance.pages.count() > 3:
                                        fields_pages = field_page_instance.pages.order_by(
                                            '-number_of_followers')[0:3]
                                    else:
                                        fields_pages = field_page_instance.pages.all()
                                    favourite_field_top_pages = favourite_field_top_pages.union(
                                        fields_pages)
                                if len(favourite_field_top_pages) > 5:
                                    favourite_field_top_pages = favourite_field_top_pages.order_by(
                                        '-number_of_followers')[0:5]
                                favourite_field_top_posts = Post.objects.none()
                                for page in favourite_field_top_pages:
                                    post_page_list_instance = PagePostList.objects.prefetch_related(
                                        'posts').get(page=page)
                                    post_list_by_page = post_page_list_instance.posts.filter(
                                        posted_at__gte=timezone.now() - timedelta(days=2))
                                    favourite_field_top_posts = favourite_field_top_posts.union(
                                        post_list_by_page)
                                favourite_field_top_posts = favourite_field_top_posts.difference(
                                    recently_suggested_posts, tagged_page_posts_to_be_suggested, unknown_page_posts_to_be_suggested, page_posts_to_be_suggested)
                                if len(favourite_field_top_posts) >= required_number_of_posts:
                                    '''
                                    If i number of posts are not obtained send the posts which has been obtained.
                                    It will be front end which will call for suggestion for pages and profile when empty list is returned.
                                    '''
                                    favourite_field_top_posts = favourite_field_top_posts.order_by(
                                        '-score')[0:required_number_of_posts]
                                    user_serializer_level_1 = PostByUserRetrieveByOtherSerializer(
                                        user_posts_to_be_suggested, many=True)
                                    user_serializer_level_2 = PostByUserRetrieveByOtherSerializer(
                                        unknown_user_posts_to_be_suggested, many=True)
                                    user_serializer_level_3 = PostByUserRetrieveByOtherSerializer(
                                        tagged_user_posts_to_be_suggested, many=True)
                                    page_serializer_level_1 = PostByPageRetrieveByOtherSerializer(
                                        page_posts_to_be_suggested, many=True)
                                    page_serializer_level_2 = PostByPageRetrieveByOtherSerializer(
                                        unknown_page_posts_to_be_suggested, many=True)
                                    page_serializer_level_3 = PostByPageRetrieveByOtherSerializer(
                                        tagged_page_posts_to_be_suggested, many=True)
                                    page_serializer_level_4 = PostByPageRetrieveByOtherSerializer(
                                        favourite_field_top_posts, many=True)
                                    data = user_serializer_level_1.data + user_serializer_level_2.data + user_serializer_level_3.data + \
                                        page_serializer_level_1.data + page_serializer_level_2.data + \
                                        page_serializer_level_3.data + page_serializer_level_4.data
                                    suggested_posts = user_posts_to_be_suggested.union(unknown_user_posts_to_be_suggested, unknown_page_posts_to_be_suggested,
                                                                                       page_posts_to_be_suggested, tagged_page_posts_to_be_suggested, tagged_user_posts_to_be_suggested, favourite_field_top_posts)
                                    user_interest.suggested_posts.add(
                                        suggested_posts)
                                    return Response(data, status=status.HTTP_200_OK)
                                    # level4 of posts by page suggestions completed.
                                else:
                                    user_serializer_level_1 = PostByUserRetrieveByOtherSerializer(
                                        user_posts_to_be_suggested, many=True)
                                    user_serializer_level_2 = PostByUserRetrieveByOtherSerializer(
                                        unknown_user_posts_to_be_suggested, many=True)
                                    user_serializer_level_3 = PostByUserRetrieveByOtherSerializer(
                                        tagged_user_posts_to_be_suggested, many=True)
                                    page_serializer_level_1 = PostByPageRetrieveByOtherSerializer(
                                        page_posts_to_be_suggested, many=True)
                                    page_serializer_level_2 = PostByPageRetrieveByOtherSerializer(
                                        unknown_page_posts_to_be_suggested, many=True)
                                    page_serializer_level_3 = PostByPageRetrieveByOtherSerializer(
                                        tagged_page_posts_to_be_suggested, many=True)
                                    page_serializer_level_4 = PostByPageRetrieveByOtherSerializer(
                                        favourite_field_top_posts, many=True)
                                    data = user_serializer_level_1.data + user_serializer_level_2.data + user_serializer_level_3.data + \
                                        page_serializer_level_1.data + page_serializer_level_2.data + \
                                        page_serializer_level_3.data + page_serializer_level_4.data
                                    suggested_posts = user_posts_to_be_suggested.union(unknown_user_posts_to_be_suggested, unknown_page_posts_to_be_suggested,
                                                                                       page_posts_to_be_suggested, tagged_page_posts_to_be_suggested, tagged_user_posts_to_be_suggested, favourite_field_top_posts)
                                    for post in suggested_posts:
                                        user_interest.suggested_posts.add(post)
                                    return Response(data, status=status.HTTP_200_OK)
                                    # last level completed.


