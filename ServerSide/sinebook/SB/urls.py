from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (AddMemberView, CreatedPagesOfProfile, FollowUnfollowPage, MyFollowedPages,
                    PageCreateView, PageRUDView, PostListCreateView, PostRUDView, RegisterUserView, RemoveMemberView, UpdateProfileView,
                    PostLikeView, CommentView,
                    CommentLikeView, CommentListView, CommentRDView, ListFriends, RetrieveProfileView,
                    FriendRequestView, AcceptCancelRequestView, UnfriendView, RetrieveProfileWithoutId)


urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register', RegisterUserView.as_view(), name="register_user"),
    path('myprofile/<int:pk>', UpdateProfileView.as_view(), name="profile"),
    path('myprofile', RetrieveProfileWithoutId.as_view(),
         name="retrieve_your_profile_without_id"),
    path('post', PostListCreateView.as_view(), name="post"),
    path('postLike/<int:pk>', PostLikeView.as_view(), name="post_like"),
    path('comment', CommentView.as_view(), name="comment"),
    path('commentLike/<int:pk>', CommentLikeView.as_view(), name="comment_like"),
    path('post/<int:pk>', PostRUDView.as_view(), name="post_rud"),
    path('postComments/<int:pk>', CommentListView.as_view(), name="post_comments"),
    path('comment/<int:pk>', CommentRDView.as_view(), name="Comment_RUD"),
    path('friendsList/<int:pk>', ListFriends.as_view(), name="Friends List"),
    path('profile/<int:pk>', RetrieveProfileView.as_view(), name="retrieve_profile"),
    path('friendrequest/<int:pk>', FriendRequestView.as_view(), name="send_request"),
    path('acceptrequest/<int:pk>',
         AcceptCancelRequestView.as_view(), name="accept_requests"),
    path('unfriend/<int:pk>', UnfriendView.as_view(), name="unfriend"),
    path('page', PageCreateView.as_view(), name="create_page"),
    path('page/<int:pk>', PageRUDView.as_view(), name="page_rud"),
    path('addMember', AddMemberView.as_view(), name="add_page_member"),
    path('removeMember', RemoveMemberView.as_view(), name="remove_page_member"),
    path('followPage/<int:pk>', FollowUnfollowPage.as_view(),
         name="follow_unfollow_page"),
    path('pages/<int:pk>', CreatedPagesOfProfile.as_view(),
         name="created_pages_by_user"),
    path('pages', MyFollowedPages.as_view(), name="followed_pages")
]
