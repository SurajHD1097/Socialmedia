from django.urls import path

from .api import *

urlpatterns = [
    path('search/', UserSearchAPIView.as_view(), name='search'),
    path('sendrequest/', SendFriendRequestView.as_view(), name='send_request'),
    path('acceptrequest/<int:pk>/', AcceptFriendRequestView.as_view(), name='accept_request'),
    path('rejectrequest/<int:pk>/', RejectFriendRequestView.as_view(), name='reject_request'),
    path('friendslist/', ListFriendsView.as_view(), name='friends_list'),
    path('pendingrequests/', ListPendingFriendRequestsView.as_view(), name='pending_requests'),
    path('suggestion/', ListFriendSuggestionView.as_view(), name='suggestion'),
]