from rest_framework import status
from rest_framework import generics, status, pagination, permissions
from rest_framework.response import Response

from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from Authentication.models import FriendRequest, Friends
from .serializers import *

from django.contrib.auth import get_user_model
User = get_user_model()

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10  # Number of records per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserSearchAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        search_query = self.request.query_params.get('q', None)
        if search_query:
            if '@' in search_query:
                queryset = User.objects.filter(email__iexact=search_query)
            else:
                queryset = User.objects.filter(
                    Q(first_name__icontains=search_query) | 
                    Q(last_name__icontains=search_query)
                )
        else:
            queryset = User.objects.none()  # Return an empty queryset if no search query is provided
        
        return queryset

class SendFriendRequestView(generics.CreateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        from_user = request.user
        to_user = request.data.get('to_user')
        request.data['from_user'] = from_user.id

        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_requests_count = FriendRequest.objects.filter(from_user=from_user, timestamp__gte=one_minute_ago).count()
        
        if recent_requests_count >= 3:
            return Response({"message": "You cannot send more than 3 friend requests within a minute."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({"message": "Friend request already sent."}, status=status.HTTP_400_BAD_REQUEST)
    
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({'message': 'Request sent', 'results': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Failed to send request', 'error': serializer.errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AcceptFriendRequestView(generics.UpdateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        friend_request = self.get_object()
        if friend_request.to_user != request.user:
            return Response({"message": "You are not authorized to accept this request."}, status=status.HTTP_403_FORBIDDEN)
        
        friend_request.status = 'accepted'
        friend_request.save()

        # Create a Friendship for both users
        Friends.objects.create(user=friend_request.from_user, friend=friend_request.to_user)
        Friends.objects.create(user=friend_request.to_user, friend=friend_request.from_user)

        return Response({"message": "Friend request accepted."}, status=status.HTTP_200_OK)

class RejectFriendRequestView(generics.UpdateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        friend_request = self.get_object()
        if friend_request.to_user != request.user:
            return Response({"message": "You are not authorized to reject this request."}, status=status.HTTP_403_FORBIDDEN)
        
        friend_request.status = 'rejected'
        friend_request.save()

        return Response({"message": "Friend request rejected."}, status=status.HTTP_200_OK)

class ListFriendsView(generics.ListAPIView):
    serializer_class = FriendsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
       return Friends.objects.filter(user=self.request.user)

class ListPendingFriendRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, status='pending')
    
class ListFriendSuggestionView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)