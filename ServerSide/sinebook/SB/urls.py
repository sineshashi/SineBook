from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (RegisterUserView, UpdateProfileView, Postview, PostLikeView, CommentView,
 CommentLikeView, PostRUDView, CommentListView, CommentRDView, PostListsofProfileView, ListFriends, RetrieveProfileView,
 FriendRequestView, AcceptCancelRequestView)
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Pastebin API')

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', schema_view),
    path('register', RegisterUserView.as_view(), name = "register_user"),
    path('myprofile/<int:pk>', UpdateProfileView.as_view(), name = "profile"),
    path('post', Postview.as_view(), name= "post"),
    path('postLike/<int:pk>', PostLikeView.as_view(), name="post_like"),
    path('comment', CommentView.as_view(), name= "comment"),
    path('commentLike/<int:pk>', CommentLikeView.as_view(), name = "comment_like"),
    path('post/<int:pk>', PostRUDView.as_view(), name = "post_rud"),
    path('postComments/<int:pk>', CommentListView.as_view(), name= "post_comments"),
    path('comment/<int:pk>', CommentRDView.as_view(), name= "Comment_RUD"),
    path('posts/<int:pk>', PostListsofProfileView.as_view(), name="posts_of_specific_profile"),
    path('friendsList/<int:pk>', ListFriends.as_view(), name = "Friends List"),
    path('profile/<int:pk>', RetrieveProfileView.as_view(), name="retrieve_profile"),
    path('friendrequest/<int:pk>', FriendRequestView.as_view(), name="send_request"),
    path('acceptrequest/<int:pk>', AcceptCancelRequestView.as_view(), name = "accept_requests")
]