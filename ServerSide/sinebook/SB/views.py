from django.contrib.auth.hashers import make_password
from .models import FriendRequest, SBUser, Post, Comment
from django.contrib.auth.models import User
from rest_framework import generics, status
from .serializers import (FriendRequestSerializer, RegisterSBUserSerializer, UpdateProfileSerialier, PostSerializer,
                          CommentSerializer, PostRetrieveSerializer, PostRDSerializer, PostUSerializer,
                          CommentLRDSerializerForPoster, CommentLRSerializerForUser, CommentRDSerializerForCommentor, CommentUpdateSerializer,
                          RetrieveProfileSerializer, ListFriendsSerializer)
from rest_framework.exceptions import NotAcceptable, NotAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import json
from django.core.exceptions import ObjectDoesNotExist

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
        "image": " "
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
        if request.data['user']['password'].isdigit():
            raise NotAcceptable(detail="password must contain alphabets also.")
        password_list = list(request.data['user']['password'])
        for i in password_list:
            try:
                int(i)
                bool = True
                break
            except:
                bool = False
        if bool == False:
            raise NotAcceptable(
                detail="Password must contain digits along with alphbets.")
        if len(request.data['user']['password']) < 8:
            raise NotAcceptable(
                detail="Password must have at least 8 characters.")
        if userdata['password'] != userdata['confirm_password']:
            raise NotAcceptable(
                detail="Password and confirm password do not match.")
        password = userdata.get('password')
        password = make_password(password)
        del request.data['user']['confirm_password']
        request.data['user']['password'] = password
        request.data['user']['username'] = request.data['user']['email']
        return super().create(request, *args, **kwargs)
    queryset = SBUser.objects.all()
    serializer_class = RegisterSBUserSerializer


class UpdateProfileView(generics.RetrieveUpdateDestroyAPIView):
    def update(self, request, *args, **kwargs):
        '''
        It updates the profile and takes SBUser id as primary key.
        There are many fields like favourite_books, your_address, you_college etc which can be filled here.
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


class Postview(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        '''
        request.data = {
            "description" : " ",
            "image" : "  "
        } 
        It posts a post on SIneBook.
        '''
        if len(request.data) == 0:
            raise NotAcceptable(detail="No data provided.")
        request.data['user'] = self.request.user.id
        if (request.data.get('description') is None) and (request.data.get('image') is None):
            raise NotAcceptable(detail="Please provide data to post.")
        return super().create(request, *args, **kwargs)
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]


class PostLikeView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        '''
        It likes the post of given pk if it is not liked earlier, else it will unlike it.
        '''
        kwargs['partial'] = True
        post = Post.objects.filter(id=kwargs['pk']).first()
        if post is None:
            raise NotAcceptable(detail="Provide right post id.")
        if post.likes.filter(id=self.request.user.id).exists():
            post.likes.remove(self.request.user.id)
            return Response("Post has been unliked", status=status.HTTP_200_OK)
        else:
            post.likes.add(self.request.user.id)
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
    queryset = Comment.objects.all()
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
            return Response("comment has been unliked", status=status.HTTP_200_OK)
        else:
            comment.likes.add(self.request.user.id)
            return Response("comment has been liked.", status=status.HTTP_200_OK)


class PostRUDView(generics.RetrieveUpdateDestroyAPIView):
    def retrieve(self, request, *args, **kwargs):
        '''
        Retrieves any post and manages who_can_see and who_can_comment fields also.
        '''
        post_id = kwargs['pk']
        try:
            post = Post.objects.get(id=post_id)
        except ObjectDoesNotExist:
            raise NotAcceptable(detail="Provide right primary key.")
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
            raise NotAcceptable(detail="Please Provide details.")
        try:
            post = Post.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            raise NotAcceptable(detail="Provide right primary key.")
        if self.request.user.id != post.user_id:
            raise NotAcceptable(
                detail="You are not authorized for this action.")
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if kwargs.get('pk') is None:
            raise NotAcceptable(detail="Please Provide details.")
        try:
            post = Post.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            raise NotAcceptable(detail="Provide right primary key.")
        if self.request.user.id != post.user_id:
            raise NotAcceptable(
                detail="You are not authorized for this action.")
        return super().destroy(request, *args, **kwargs)
    queryset = Post.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        post = Post.objects.get(id=self.kwargs['pk'])
        if self.request.user.id == post.user_id:
            if (self.request.method == 'PUT') or (self.request.method == 'PATCH'):
                return PostUSerializer
            else:
                return PostRDSerializer
        else:
            return PostRetrieveSerializer
    serializer_class = get_serializer_class
    permission_classes = [IsAuthenticated]


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
        posting_user = comment.post.user_id
        if (self.request.user.id != comment.user_id) or (self.request.user.id != posting_user):
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
        if (self.request.user.id != comment.user_id) or (self.request.user.id != posting_user):
            raise NotAcceptable(
                detail="You are not authorized for this action.")
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


class PostListsofProfileView(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        '''
        Lists all the posts of a given user.
        '''
        if kwargs.get('pk') is None:
            raise NotAcceptable(detail="Please provide user id.")
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        requesting_user = self.request.user
        requested_userid = self.kwargs['pk']
        if requesting_user.id == requested_userid:
            return Post.objects.filter(user_id=requested_userid)
        else:
            requesting_sb_user = SBUser.objects.get(user_id=requesting_user.id)
            requested_sb_user = SBUser.objects.get(user_id=requested_userid)
            if requesting_sb_user not in requested_sb_user.friends.all():
                return Post.objects.filter(user_id=requested_userid, who_can_see='Public')
            else:
                return Post.objects.filter(user_id=requested_userid).exclude(who_can_see='None')
    serializer_class = PostRetrieveSerializer
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
                requested_data = SBUser.objects.get(user_id=self.request.user.id)
            except ObjectDoesNotExist:
                raise NotAcceptable(detail="This user is not registered completely.")
            serializer = RetrieveProfileSerializer(requested_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            try:
                requesting_sb_user = SBUser.objects.get(
                    user_id=self.request.user.id)
            except ObjectDoesNotExist:
                raise NotAcceptable(detail="This user is not registered completely.")
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
                data.pop('your_first_school')
                data.pop('your_college')
                data.pop('your_occupation')
                data.pop('favourite_movies')
                data.pop('favourite_books')
                data.pop('your_address')
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
                    data.pop('your_first_school')
                    data.pop('your_college')
                    data.pop('your_occupation')
                    data.pop('favourite_movies')
                    data.pop('favourite_books')
                    data.pop('your_address')
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
