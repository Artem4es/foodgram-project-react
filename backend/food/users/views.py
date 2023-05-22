from djoser.views import UserViewSet, TokenCreateView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import (
    status,
)

from users.models import Follow, User
from users.serializers import (
    CustomUserSerializer,
    SubscribeUserSerializer,
)
from users.validators import (
    check_already_subscribed,
    check_if_not_subscribed,
    check_user,
    check_user_is_author,
)


class CustomTokenCreateView(TokenCreateView):
    """Status code change from 200 to 201"""

    def _action(self, serializer):
        response = super()._action(serializer)
        response.status_code = status.HTTP_201_CREATED
        return response


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)

    @action(
        detail=False,
        methods=('get',),
        url_path='subscriptions',
    )
    def subscription(self, request):
        user = self.request.user
        subscriptions = user.following.all().values_list('author', flat=True)
        queryset = self.queryset.filter(id__in=subscriptions)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscribeUserSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscribeUserSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=('post', 'delete'), url_path=r'subscribe')
    def subscribe(self, request, id):
        self.check_permissions(request)
        check_user(id, User)
        author = User.objects.get(id=id)
        cur_user = request.user
        if request.method == 'POST':
            check_user_is_author(author, cur_user, User)
            check_already_subscribed(author, cur_user, Follow)
            Follow.objects.create(user=cur_user, author=author)
            serializer = SubscribeUserSerializer(
                instance=author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            check_if_not_subscribed(cur_user, author, Follow)
            Follow.objects.filter(user=cur_user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
