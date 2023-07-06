""" Набор представлений для управления комментариями к цели (CRUD)

GoalCommentCreateView - создание комментария (только владелец/редактор)
GoalCommentListView - формирование списка комментариев (доступно любому участнику доски)
GoalCommentDetailView - предоставление информации по комментарию / его изменение / удаление (только владелец/редактор)

"""
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions

from goals.models import GoalComment
from goals.permissions import GoalCommentPermission
from goals.serializers import GoalCommentSerializer, GoalCommentWithUserSerializer


class GoalCommentCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentSerializer


class GoalCommentListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentWithUserSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['goal']
    ordering = ['-created']

    def get_queryset(self) -> QuerySet[GoalComment]:
        """ Показывает комментарии участникам """

        return GoalComment.objects.filter(goal__category__board__participants__user=self.request.user)


class GoalCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [GoalCommentPermission]
    serializer_class = GoalCommentWithUserSerializer

    def get_queryset(self) -> QuerySet[GoalComment]:
        """ Показывает детальный комментарий участникам """

        return GoalComment.objects.select_related('user').filter(
                goal__category__board__participants__user=self.request.user
            )
